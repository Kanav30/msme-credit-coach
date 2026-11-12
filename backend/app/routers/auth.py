"""
Authentication and session endpoints for the MSME Credit Score Coach.
"""

import sys
import os
import uuid
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from fastapi import APIRouter, HTTPException, Depends, Request, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

try:
    from app.core import logging_store as store
    from app.core import security
    from app.core.rate_limiter import login_limiter
    from app.routers import owner
except ModuleNotFoundError:
    import logging_store as store
    import security
    from rate_limiter import login_limiter
    import owner

router = APIRouter(prefix="/auth", tags=["auth"])
store.init_db()


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Owner's full name")
    business_name: str = Field(..., min_length=2, description="Registered or trade business name")
    phone: Optional[str] = Field(None, min_length=7, description="Promoter / Business mobile number")
    email: Optional[str] = Field(None, min_length=5, description="Business email address")
    email_or_phone: Optional[str] = Field(None, description="Legacy single field fallback")
    password: str = Field(..., min_length=8, description="Password for account access (minimum 8 characters)")
    target_rank: Optional[int] = Field(3, ge=1, le=10, description="Target CMR rank needed for bank loan")
    industry_category: Optional[str] = Field("medium", description="Industry risk tier (low, medium, high)")


class LoginRequest(BaseModel):
    email_or_phone: str = Field(..., min_length=3, description="Mobile number (+91) or email address")
    password: str = Field(..., min_length=1, description="Account password")


class DemoLoginRequest(BaseModel):
    archetype: Optional[str] = "demo-owner-1"


def _slugify(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '-', text.strip().lower()).strip('-')
    return cleaned[:24] if cleaned else "msme"


def _validate_email(email: str) -> None:
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address (e.g., name@business.in).",
        )


def _validate_phone(phone: str) -> None:
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid mobile number with at least 10 digits.",
        )


@router.post("/signup")
def signup(req: SignupRequest):
    """Creates a new MSME business account with Argon2id password hashing and JWT token."""
    phone = (req.phone or "").strip()
    email = (req.email or "").strip().lower()

    # Fallback if submitted via legacy single field
    if not phone and req.email_or_phone:
        if "@" in req.email_or_phone:
            email = req.email_or_phone.strip().lower()
        else:
            phone = req.email_or_phone.strip()

    if not phone or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both mobile phone number and email address are required.",
        )

    _validate_email(email)
    _validate_phone(phone)
    security.validate_password(req.password)

    target_rank = max(1, min(10, req.target_rank or 3))
    industry_category = (req.industry_category or "medium").strip().lower()
    if industry_category not in ("low", "medium", "high"):
        industry_category = "medium"

    base_slug = _slugify(req.business_name)
    owner_id = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    try:
        user = store.create_user(
            owner_id=owner_id,
            full_name=req.full_name.strip(),
            business_name=req.business_name.strip(),
            phone=phone,
            email=email,
            password=req.password,
            target_rank=target_rank,
            industry_category=industry_category,
            is_demo=False,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Register in-memory metadata for compatibility
    owner._PROFILE_METADATA[owner_id] = {
        "name": user["business_name"],
        "archetype": "Registered Business",
        "industry_name": f"{industry_category.capitalize()} Risk MSME",
        "target_rank": target_rank,
        "gst_filing_regularity": 0.80,
        "upi_inflow_stability": 0.80,
    }

    # Generate cryptographically signed JWT token
    token = security.create_access_token({
        "sub": owner_id,
        "user_id": user.get("id"),
        "email": email,
        "phone": phone,
        "is_demo": False,
        "target_rank": target_rank,
    })

    return {
        "success": True,
        "message": "Account created successfully.",
        "token": token,
        "token_type": "bearer",
        "is_demo": False,
        "user": user,
    }


@router.post("/login")
def login(req: LoginRequest, request: Request):
    """Authenticates an existing MSME owner with rate-limiting protection and JWT token issuance."""
    raw_ident = req.email_or_phone.strip()
    if not raw_ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide your mobile number or email address.",
        )

    # Throttling key based on client IP and identifier
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{raw_ident.lower()}"
    login_limiter.check(rate_key)

    user = store.authenticate_user(raw_ident, req.password)
    if not user:
        login_limiter.record_failure(rate_key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please verify your mobile number or email address and password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reset rate limiting on successful login
    login_limiter.record_success(rate_key)

    owner_id = user["owner_id"]
    if owner_id not in owner._PROFILE_METADATA:
        owner._PROFILE_METADATA[owner_id] = {
            "name": user["business_name"],
            "archetype": "Registered Business",
            "industry_name": "Commercial MSME",
            "target_rank": user.get("target_rank", 3),
            "gst_filing_regularity": 0.80,
            "upi_inflow_stability": 0.80,
        }

    token = security.create_access_token({
        "sub": owner_id,
        "user_id": user.get("id"),
        "email": user.get("email"),
        "phone": user.get("phone"),
        "is_demo": bool(user.get("is_demo", False)),
        "target_rank": user.get("target_rank", 3),
    })

    return {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "token_type": "bearer",
        "is_demo": bool(user.get("is_demo", False)),
        "user": user,
    }


@router.post("/demo-login")
def demo_login(req: Optional[DemoLoginRequest] = None):
    """
    Creates an isolated guest session with a unique owner identity.
    Persists to database so all foreign keys, action logs, and CIBIL report uploads work cleanly.
    """
    demo_uuid = uuid.uuid4().hex[:8]
    owner_id = f"demo-{demo_uuid}"
    demo_phone = f"+91-0000{uuid.uuid4().int % 1000000:06d}"
    demo_email = f"{owner_id}@demo.msme-credit-coach.internal"

    try:
        user = store.create_user(
            owner_id=owner_id,
            full_name="Demo Business Owner",
            business_name="Apex Precision Tools (Demo)",
            phone=demo_phone,
            email=demo_email,
            password=f"DemoAccessPass_{uuid.uuid4().hex}",
            target_rank=3,
            industry_category="medium",
            is_demo=True,
        )
    except Exception:
        # Fallback dictionary if DB write fails
        user = {
            "owner_id": owner_id,
            "full_name": "Demo Business Owner",
            "business_name": "Apex Precision Tools (Demo)",
            "phone": demo_phone,
            "email": demo_email,
            "email_or_phone": demo_email,
            "target_rank": 3,
            "industry_category": "medium",
            "is_demo": True,
        }

    owner._PROFILE_METADATA[owner_id] = {
        "name": "Apex Precision Tools (Demo)",
        "archetype": "Demo Commercial MSME",
        "industry_name": "Commercial MSME",
        "target_rank": 3,
        "gst_filing_regularity": 0.80,
        "upi_inflow_stability": 0.80,
    }

    token = security.create_access_token({
        "sub": owner_id,
        "user_id": user.get("id"),
        "email": demo_email,
        "phone": demo_phone,
        "is_demo": True,
        "target_rank": 3,
    })

    return {
        "success": True,
        "message": "Demo session initialized with isolated workspace.",
        "token": token,
        "token_type": "bearer",
        "is_demo": True,
        "user": user,
    }


@router.get("/me")
def get_authenticated_user(current_user: Dict[str, Any] = Depends(security.get_current_user)):
    """Retrieves session profile for the authenticated owner derived strictly from the JWT token."""
    return {"user": current_user}


@router.get("/me/{owner_id}")
def get_user_profile_by_path(
    owner_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """
    Retrieves session profile for the active owner.
    Enforces authorization: User A cannot query User B's profile.
    """
    security.verify_owner_access(owner_id, current_user)
    return {"user": current_user}


@router.get("/db-status")
def get_db_status():
    """Returns the current database engine status (MySQL vs. SQLite fallback)."""
    return {
        "status": "ok",
        "database": store.get_active_engine_info(),
    }
