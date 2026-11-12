"""
Security and authentication utilities for MSME Credit Coach.

Provides:
1. Argon2id cryptographic password hashing with unique salts.
2. Sensible password validation enforcing complexity and length.
3. JWT token generation, signing, decoding, and expiration.
4. FastAPI dependency for token extraction and user session verification.
5. Strict tenant/owner authorization helpers to prevent cross-account access.
"""

import os
import re
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from app.core import logging_store as store
except ModuleNotFoundError:
    import logging_store as store

# Secret key & JWT config: strictly require secure configuration in production
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
APP_ENV = os.getenv("APP_ENV", "development").lower()

if not JWT_SECRET:
    if APP_ENV == "production":
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: JWT_SECRET or SECRET_KEY must be set in environment variables in production mode. "
            "Hardcoded fallback secrets are strictly forbidden."
        )
    JWT_SECRET = "dev-insecure-only-local-secret-key-do-not-use-in-production"
elif JWT_SECRET in ("msme-credit-coach-production-jwt-secret-key-2026-secure", "default", "secret", "change_me"):
    if APP_ENV == "production":
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: Known insecure default JWT_SECRET detected in production environment. "
            "Please configure a strong, random cryptographically generated secret in your environment."
        )

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))  # 7 days

# Argon2id password hasher (64MB memory, 2 iterations, 2 parallelism)
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)

# HTTP Bearer scheme
bearer_scheme = HTTPBearer(auto_error=False)


def validate_password(password: str) -> None:
    """
    Validates password complexity:
    - Minimum 8 characters.
    - Contains at least one letter.
    - Contains at least one digit or symbol.
    - No leading or trailing pure whitespace.
    """
    if not isinstance(password, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be a valid text string.",
        )
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long.",
        )
    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one alphabetic letter.",
        )
    if not re.search(r"[0-9!@#$%^&*()_+\-=\[\]{};':\",.<>/?]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number or special character.",
        )
    if password.strip() != password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot begin or end with whitespace.",
        )


def hash_password(password: str) -> str:
    """Hashes a password using Argon2id with a unique cryptographic salt."""
    validate_password(password)
    return _hasher.hash(password)


def verify_password(stored_hash: str, password: str) -> bool:
    """
    Verifies a password against the stored hash.
    Supports Argon2id natively and falls back to SHA-256 for legacy accounts.
    """
    if not stored_hash or not password:
        return False

    # Standard Argon2id hash check
    if stored_hash.startswith("$argon2"):
        try:
            return _hasher.verify(stored_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    # Legacy SHA-256 fallback
    legacy_sha = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return stored_hash == legacy_sha


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a cryptographically signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    })
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Raises standard HTTPException with 401 on expired or invalid token.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.PyJWTError, Exception):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    FastAPI dependency: extracts and validates the Bearer token,
    derives the authenticated user from the database or verified session,
    and returns the user dictionary.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    owner_id = payload.get("sub")
    if not owner_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject identity.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check for demo user token
    is_demo = bool(payload.get("is_demo", False))

    user = store.get_user_by_owner_id(owner_id)
    if not user:
        if is_demo:
            return {
                "owner_id": owner_id,
                "full_name": payload.get("full_name", "Demo Business Owner"),
                "business_name": payload.get("business_name", "Apex Precision Tools (Demo)"),
                "email": payload.get("email", f"{owner_id}@demo.msme-credit-coach.internal"),
                "phone": payload.get("phone", ""),
                "is_demo": True,
                "target_rank": payload.get("target_rank", 3),
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The user account for this session no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Guarantee password hash is never in user context
    user.pop("password_hash", None)
    user["is_demo"] = is_demo or bool(user.get("is_demo", False))
    return user


def verify_owner_access(owner_id: str, current_user: Dict[str, Any]) -> None:
    """
    Enforces authorization: ensures the authenticated user can only access
    or mutate their own business profile and data.
    """
    authenticated_owner_id = current_user.get("owner_id")
    if not authenticated_owner_id or authenticated_owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to access or modify this profile.",
        )
