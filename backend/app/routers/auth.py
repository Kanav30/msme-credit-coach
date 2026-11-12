"""
Authentication and session endpoints for the MSME Credit Score Coach.
"""

import sys
import os
import uuid
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging_store as store
from app.routers import owner
from feature_engineering import BusinessCreditProfile

router = APIRouter(prefix="/auth", tags=["auth"])
store.init_db()


class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Owner's full name")
    business_name: str = Field(..., min_length=2, description="Registered or trade business name")
    phone: Optional[str] = Field(None, min_length=7, description="Promoter / Business mobile number")
    email: Optional[str] = Field(None, min_length=5, description="Business email address")
    email_or_phone: Optional[str] = Field(None, description="Legacy single field fallback")
    password: str = Field(..., min_length=6, description="Password for account access")
    target_rank: Optional[int] = Field(3, ge=1, le=10, description="Target CMR rank needed for bank loan")
    industry_category: Optional[str] = Field("medium", description="Industry risk tier (low, medium, high)")


class LoginRequest(BaseModel):
    email_or_phone: str = Field(..., min_length=3, description="Mobile number (+91) or email address")
    password: str


class DemoLoginRequest(BaseModel):
    archetype: Optional[str] = "demo-owner-1"


def _slugify(text: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9]+', '-', text.strip().lower()).strip('-')
    return cleaned[:24] if cleaned else "msme"


@router.post("/signup")
def signup(req: SignupRequest):
    """Creates a new MSME business account connected to both mobile phone and email."""
    # Determine phone and email
    phone = (req.phone or "").strip()
    email = (req.email or "").strip()

    # Fallback if submitted via single field
    if not phone and req.email_or_phone:
        if "@" in req.email_or_phone:
            email = req.email_or_phone.strip()
        else:
            phone = req.email_or_phone.strip()

    if not phone or not email:
        raise HTTPException(
            status_code=400,
            detail="Both mobile phone number and email address are required so either can be used to sign in."
        )

    # Generate unique owner_id
    base_slug = _slugify(req.business_name)
    owner_id = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    try:
        user = store.create_user(
            owner_id=owner_id,
            full_name=req.full_name,
            business_name=req.business_name,
            phone=phone,
            email=email,
            password=req.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Register business metadata without fake credit scores
    owner._PROFILE_METADATA[owner_id] = {
        "name": req.business_name,
        "archetype": "Registered Business",
        "industry_name": "Commercial MSME",
        "target_rank": req.target_rank or 3,
        "gst_filing_regularity": 0.80,
        "upi_inflow_stability": 0.80,
    }

    # Mock access token (survives client sessions)
    token = f"msme_token_{uuid.uuid4().hex}"

    return {
        "success": True,
        "message": "Account created successfully. You can sign in using either your phone number or email address.",
        "token": token,
        "user": {
            "owner_id": owner_id,
            "full_name": user["full_name"],
            "business_name": user["business_name"],
            "phone": user.get("phone", phone),
            "email": user.get("email", email),
            "email_or_phone": user.get("email", email),
            "target_rank": req.target_rank or 3,
        },
    }


@router.post("/login")
def login(req: LoginRequest):
    """Authenticates an existing MSME owner via EITHER mobile phone or email address using the same password."""
    user = store.authenticate_user(req.email_or_phone, req.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials. Please verify your mobile number or email address and password."
        )

    owner_id = user["owner_id"]
    if owner_id not in owner._PROFILE_METADATA:
        owner._PROFILE_METADATA[owner_id] = {
            "name": user["business_name"],
            "archetype": "Registered Business",
            "industry_name": "Commercial MSME",
            "target_rank": 3,
            "gst_filing_regularity": 0.80,
            "upi_inflow_stability": 0.80,
        }

    token = f"msme_token_{uuid.uuid4().hex}"

    return {
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "owner_id": owner_id,
            "full_name": user["full_name"],
            "business_name": user["business_name"],
            "phone": user.get("phone", ""),
            "email": user.get("email", ""),
            "email_or_phone": req.email_or_phone,
            "target_rank": user.get("target_rank", 3),
        },
    }


@router.get("/db-status")
def get_db_status():
    """Returns the current database engine status (MySQL vs. SQLite fallback)."""
    return {
        "status": "ok",
        "database": store.get_active_engine_info(),
    }


@router.post("/demo-login")
def demo_login(req: Optional[DemoLoginRequest] = None):
    """Guest session initialized with empty placeholders."""
    owner_id = "guest-msme"
    owner._PROFILE_METADATA[owner_id] = {
        "name": "My Business",
        "archetype": "Awaiting CIBIL Report",
        "industry_name": "Commercial MSME",
        "target_rank": 3,
        "gst_filing_regularity": 0.0,
        "upi_inflow_stability": 0.0,
    }
    token = f"guest_token_{uuid.uuid4().hex[:8]}"

    return {
        "success": True,
        "message": "Guest session initialized.",
        "token": token,
        "is_demo": False,
        "user": {
            "owner_id": owner_id,
            "full_name": "Business Owner",
            "business_name": "My Business",
            "email_or_phone": "owner@business.in",
            "target_rank": 3,
        },
    }


@router.get("/me/{owner_id}")
def get_current_user_profile(owner_id: str):
    """Retrieves session profile for the active owner."""
    user = store.get_user_by_owner_id(owner_id)
    if user:
        return {"user": user}

    meta = owner._PROFILE_METADATA.get(owner_id)
    if meta:
        return {
            "user": {
                "owner_id": owner_id,
                "full_name": "Business Owner",
                "business_name": meta.get("name", "My Business"),
                "email_or_phone": f"{owner_id}@business.in",
                "target_rank": meta.get("target_rank", 3),
            }
        }

    return {
        "user": {
            "owner_id": owner_id,
            "full_name": "Business Owner",
            "business_name": "My Business",
            "email_or_phone": "",
            "target_rank": 3,
        }
    }
