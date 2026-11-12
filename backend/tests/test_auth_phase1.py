"""
Automated Test Suite for Phase 1: Authentication and Authorization.

Covers:
1. Argon2id password hashing and unique salt verification.
2. Password validation rules.
3. JWT creation, validity, and expiration.
4. Signup with target_rank and industry_category persistence.
5. Dual-identifier login (phone or email) and duplicate rejection.
6. Login rate limiting (429 Too Many Requests).
7. Demo session isolation (unique identities, is_demo=True).
8. Protection of private endpoints (401 without valid token).
9. Cross-tenant authorization (403 Forbidden on foreign owner_id).
10. Action deletion ownership validation (User A cannot delete User B's actions).
"""

import os
import sys
import uuid
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient

# Ensure backend and ml paths are imported
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ML_SRC_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "..", "ml", "src"))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, ML_SRC_DIR)

from app.main import app
from app.core import security
from app.core import logging_store as store
from app.core.rate_limiter import LoginRateLimiter

client = TestClient(app)


# -------------------------------------------------------------------------
# 1. Password Hashing with Argon2id & Salts
# -------------------------------------------------------------------------
def test_argon2id_password_hashing():
    pwd = "SecurePassword123!"
    h1 = security.hash_password(pwd)
    h2 = security.hash_password(pwd)

    assert h1.startswith("$argon2id$"), "Hash must be an Argon2id hash"
    assert h2.startswith("$argon2id$"), "Hash must be an Argon2id hash"
    assert h1 != h2, "Each hash must have a unique cryptographic salt"

    assert security.verify_password(h1, pwd) is True
    assert security.verify_password(h2, pwd) is True
    assert security.verify_password(h1, "WrongPassword123!") is False


def test_password_validation_rules():
    # Less than 8 characters
    with pytest.raises(Exception) as excinfo:
        security.validate_password("Short1!")
    assert "at least 8 characters" in str(excinfo.value.detail)

    # Missing letter
    with pytest.raises(Exception) as excinfo:
        security.validate_password("1234567890!")
    assert "at least one alphabetic letter" in str(excinfo.value.detail)

    # Missing number or symbol
    with pytest.raises(Exception) as excinfo:
        security.validate_password("OnlyLettersHere")
    assert "number or special character" in str(excinfo.value.detail)

    # Leading/trailing whitespace
    with pytest.raises(Exception) as excinfo:
        security.validate_password(" ValidPass123! ")
    assert "whitespace" in str(excinfo.value.detail)


# -------------------------------------------------------------------------
# 2. JWT Generation & Verification
# -------------------------------------------------------------------------
def test_jwt_lifecycle():
    owner_id = f"test-owner-{uuid.uuid4().hex[:6]}"
    token = security.create_access_token({
        "sub": owner_id,
        "email": "test@business.in",
        "is_demo": False,
    })

    payload = security.decode_access_token(token)
    assert payload["sub"] == owner_id
    assert payload["email"] == "test@business.in"
    assert payload["is_demo"] is False
    assert "exp" in payload

    # Expired token
    expired_token = security.create_access_token(
        {"sub": owner_id},
        expires_delta=timedelta(seconds=-10),
    )
    with pytest.raises(Exception) as excinfo:
        security.decode_access_token(expired_token)
    assert excinfo.value.status_code == 401
    assert "expired" in str(excinfo.value.detail).lower()


# -------------------------------------------------------------------------
# 3. Signup, Field Persistence, and Dual-Identifier Login
# -------------------------------------------------------------------------
def test_signup_field_persistence_and_login():
    unique_suffix = uuid.uuid4().hex[:6]
    phone = f"+9198{uuid.uuid4().int % 100000000:08d}"
    email = f"promoter_{unique_suffix}@precisiontools.in"
    password = "StrongPass2026!#"

    # 1. Signup with target_rank=4 and industry_category="high"
    signup_res = client.post("/auth/signup", json={
        "full_name": "Rajesh Sharma",
        "business_name": "Sharma Precision Forgings",
        "phone": phone,
        "email": email,
        "password": password,
        "target_rank": 4,
        "industry_category": "high",
    })
    assert signup_res.status_code == 200
    signup_data = signup_res.json()
    assert signup_data["success"] is True
    assert signup_data["token"] is not None
    assert signup_data["is_demo"] is False
    user = signup_data["user"]
    assert user["target_rank"] == 4
    assert user["industry_category"] == "high"
    owner_id = user["owner_id"]

    # 2. Duplicate signup with same phone or email rejected
    dup_res = client.post("/auth/signup", json={
        "full_name": "Another Person",
        "business_name": "Duplicate Business",
        "phone": phone,
        "email": f"diff_{unique_suffix}@precisiontools.in",
        "password": password,
    })
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()

    # 3. Login using phone
    login_phone_res = client.post("/auth/login", json={
        "email_or_phone": phone,
        "password": password,
    })
    assert login_phone_res.status_code == 200
    phone_data = login_phone_res.json()
    assert phone_data["user"]["owner_id"] == owner_id
    assert phone_data["user"]["target_rank"] == 4

    # 4. Login using email
    login_email_res = client.post("/auth/login", json={
        "email_or_phone": email,
        "password": password,
    })
    assert login_email_res.status_code == 200
    email_data = login_email_res.json()
    assert email_data["user"]["owner_id"] == owner_id

    # 5. Login with invalid password returns 401
    bad_login_res = client.post("/auth/login", json={
        "email_or_phone": email,
        "password": "WrongPassword999!",
    })
    assert bad_login_res.status_code == 401


# -------------------------------------------------------------------------
# 4. Login Rate Limiting (Throttling)
# -------------------------------------------------------------------------
def test_login_rate_limiting():
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=60)
    test_key = "127.0.0.1:throttle_test@company.in"

    # 3 failed attempts
    for _ in range(3):
        limiter.record_failure(test_key)

    with pytest.raises(Exception) as excinfo:
        limiter.check(test_key)
    assert excinfo.value.status_code == 429
    assert "Too many failed login attempts" in excinfo.value.detail


# -------------------------------------------------------------------------
# 5. Demo Sessions are Isolated & is_demo is True
# -------------------------------------------------------------------------
def test_demo_session_isolation():
    res1 = client.post("/auth/demo-login")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["is_demo"] is True
    owner_id_1 = data1["user"]["owner_id"]

    res2 = client.post("/auth/demo-login")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["is_demo"] is True
    owner_id_2 = data2["user"]["owner_id"]

    # Must have distinct unique IDs
    assert owner_id_1 != owner_id_2, "Each demo session must receive a unique owner ID"

    # Demo 1 token cannot access Demo 2 profile
    token1 = data1["token"]
    cross_res = client.get(
        f"/owner/profile/{owner_id_2}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert cross_res.status_code == 403, "Demo User 1 must not access Demo User 2's profile"


# -------------------------------------------------------------------------
# 6. Private Endpoints Require Valid Authentication
# -------------------------------------------------------------------------
def test_private_endpoints_require_token():
    dummy_owner = "some-owner-123"

    # Endpoints without token must return 401
    endpoints = [
        ("GET", "/owner/profiles"),
        ("GET", f"/owner/profile/{dummy_owner}"),
        ("GET", f"/owner/diagnostic/{dummy_owner}"),
        ("GET", f"/owner/action-plan/{dummy_owner}"),
        ("POST", f"/owner/log-action/{dummy_owner}"),
        ("DELETE", "/owner/action/999"),
        ("GET", f"/owner/streak/{dummy_owner}"),
        ("GET", f"/owner/prediction/{dummy_owner}"),
        ("POST", f"/owner/simulate-what-if/{dummy_owner}"),
        ("POST", f"/owner/alternate-signal/{dummy_owner}"),
    ]

    for method, path in endpoints:
        if method == "GET":
            r = client.get(path)
        elif method == "POST":
            r = client.post(path, json={})
        elif method == "DELETE":
            r = client.delete(path)
        assert r.status_code == 401, f"{method} {path} should require authentication, got {r.status_code}"

    # Invalid token must return 401
    invalid_r = client.get("/owner/profiles", headers={"Authorization": "Bearer invalid_garbage_token"})
    assert invalid_r.status_code == 401


# -------------------------------------------------------------------------
# 7. Multi-Tenant Authorization & Action Deletion Ownership
# -------------------------------------------------------------------------
def test_tenant_authorization_and_action_deletion():
    suffix_a = uuid.uuid4().hex[:6]
    suffix_b = uuid.uuid4().hex[:6]

    # Create User A
    res_a = client.post("/auth/signup", json={
        "full_name": "User Alpha",
        "business_name": "Alpha Traders",
        "phone": f"+9191{uuid.uuid4().int % 100000000:08d}",
        "email": f"alpha_{suffix_a}@traders.in",
        "password": "AlphaPassword123!",
        "target_rank": 3,
    })
    token_a = res_a.json()["token"]
    owner_a = res_a.json()["user"]["owner_id"]

    # Create User B
    res_b = client.post("/auth/signup", json={
        "full_name": "User Beta",
        "business_name": "Beta Enterprises",
        "phone": f"+9192{uuid.uuid4().int % 100000000:08d}",
        "email": f"beta_{suffix_b}@enterprises.in",
        "password": "BetaPassword123!",
        "target_rank": 2,
    })
    token_b = res_b.json()["token"]
    owner_b = res_b.json()["user"]["owner_id"]

    # User A tries to view User B's diagnostic -> 403 Forbidden
    cross_diag = client.get(
        f"/owner/diagnostic/{owner_b}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert cross_diag.status_code == 403
    assert "Forbidden" in cross_diag.json()["detail"]

    # User A tries to log an action into User B's account -> 403 Forbidden
    cross_log = client.post(
        f"/owner/log-action/{owner_b}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "factor": "credit_utilization",
            "description": "Paid down balance",
        },
    )
    assert cross_log.status_code == 403

    # User A logs an action into their OWN account -> 200 OK
    log_a = client.post(
        f"/owner/log-action/{owner_a}",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "factor": "credit_utilization",
            "description": "Paid down 25,000 INR overdraft",
        },
    )
    assert log_a.status_code == 200
    action_a_id = log_a.json()["id"]

    # User B logs an action into their OWN account -> 200 OK
    log_b = client.post(
        f"/owner/log-action/{owner_b}",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "factor": "payment_history",
            "description": "Clean vendor settlement",
        },
    )
    assert log_b.status_code == 200
    action_b_id = log_b.json()["id"]

    # User B attempts to DELETE User A's action -> 404/403 Rejected!
    del_cross = client.delete(
        f"/owner/action/{action_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert del_cross.status_code == 404, "User B must not be able to delete User A's action"

    # Verify User A's action is STILL in User A's history
    hist_a = client.get(
        f"/owner/log-history/{owner_a}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert hist_a.status_code == 200
    actions_a = hist_a.json()["actions"]
    assert any(act["id"] == action_a_id for act in actions_a)

    # User A deletes their OWN action -> 200 OK
    del_own = client.delete(
        f"/owner/action/{action_a_id}",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert del_own.status_code == 200
