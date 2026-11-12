"""
Phase 3 Regression Tests: Account Isolation and Tenant Security
- Owner identity is strictly derived and verified against the authenticated JWT.
- Arbitrary owner IDs supplied by clients are rejected with 403 Forbidden.
- Check strict ownership for reports, business profiles, actions, and alternate signals.
- Demo users have completely isolated unique identities.
- Test two separate accounts for zero data leakage.
"""

import os
import sys
from pathlib import Path
import pytest
import uuid

os.environ["DB_ENGINE"] = "sqlite"
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ML_SRC_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "..", "ml", "src"))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, ML_SRC_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.core import logging_store as store

client = TestClient(app)


def _create_user(name: str):
    uid = uuid.uuid4().hex[:8]
    res = client.post("/auth/signup", json={
        "full_name": name,
        "business_name": f"{name} Enterprise",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"{uid}@enterprise.in",
        "password": "Password123!",
        "target_rank": 3,
    })
    assert res.status_code == 200
    token = res.json()["token"]
    owner_id = res.json()["user"]["owner_id"]
    headers = {"Authorization": f"Bearer {token}"}
    return owner_id, headers


def test_user_cannot_access_or_mutate_other_user_data():
    """User B cannot access, read, or mutate User A's data via path tampering."""
    owner_a, headers_a = _create_user("Alice Industrial")
    owner_b, headers_b = _create_user("Bob Logistics")

    # Alice sets up her profile and logs an action
    client.post(
        f"/owner/profile/{owner_a}",
        json={
            "name": "Alice Industrial",
            "on_time_payment_pct": 0.95,
            "has_recent_delinquency": False,
            "credit_utilization": 0.40,
            "credit_tenure_years": 5.0,
            "business_age_years": 8.0,
            "industry_risk_category": "low",
            "target_rank": 2,
        },
        headers=headers_a,
    )
    client.post(
        f"/owner/log-action/{owner_a}",
        json={"factor": "credit_utilization", "description": "Alice confidential loan paydown"},
        headers=headers_a,
    )

    # Bob attempts to access Alice's protected endpoints using Bob's valid token:
    endpoints_to_test = [
        ("GET", f"/owner/profile/{owner_a}", None),
        ("GET", f"/owner/diagnostic/{owner_a}", None),
        ("GET", f"/owner/action-plan/{owner_a}", None),
        ("GET", f"/owner/log-history/{owner_a}", None),
        ("GET", f"/owner/streak/{owner_a}", None),
        ("GET", f"/owner/prediction/{owner_a}", None),
        ("POST", f"/owner/profile/{owner_a}", {
            "name": "Malicious Tamper",
            "on_time_payment_pct": 0.5,
            "has_recent_delinquency": True,
            "credit_utilization": 0.9,
            "credit_tenure_years": 1.0,
            "business_age_years": 1.0,
            "industry_risk_category": "high",
            "target_rank": 5,
        }),
        ("POST", f"/owner/log-action/{owner_a}", {"factor": "credit_utilization", "description": "Bob injected"}),
        ("POST", f"/owner/reset-profile/{owner_a}", None),
        ("POST", f"/owner/simulate-what-if/{owner_a}", {
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 3,
            "max_months": 24,
        }),
        ("POST", f"/owner/alternate-signal/{owner_a}", {
            "gst_filing_regularity": 0.9,
            "upi_inflow_stability": 0.9,
        }),
        ("POST", f"/cibil/load-sample/{owner_a}/patel-textiles", None),
    ]

    for method, path, payload in endpoints_to_test:
        if method == "GET":
            r = client.get(path, headers=headers_b)
        else:
            r = client.post(path, json=payload, headers=headers_b)
        assert r.status_code == 403, f"Endpoint {method} {path} must return 403 Forbidden for cross-user access, got {r.status_code}"


def test_user_cannot_delete_other_user_action():
    """User B cannot delete an action logged by User A."""
    owner_a, headers_a = _create_user("Alice Industrial")
    owner_b, headers_b = _create_user("Bob Logistics")

    # Alice logs an action
    action = store.log_action(owner_a, "credit_utilization", "Alice private record")
    action_id = action["id"]

    # Bob attempts to delete Alice's action
    del_res = client.delete(f"/owner/action/{action_id}", headers=headers_b)
    assert del_res.status_code == 404, "Must return 404 when user has no permission to delete other's action"

    # Alice's action must still exist in DB
    alice_actions = store.get_actions(owner_a)
    assert any(a["id"] == action_id for a in alice_actions)


def test_demo_users_have_separate_unique_identities_and_zero_leakage():
    """Multiple demo sessions receive separate identities and cannot see each other's data."""
    # Demo User 1
    d1_res = client.post("/auth/demo-login")
    assert d1_res.status_code == 200
    d1_token = d1_res.json()["token"]
    d1_owner = d1_res.json()["user"]["owner_id"]
    headers_1 = {"Authorization": f"Bearer {d1_token}"}

    # Demo User 2
    d2_res = client.post("/auth/demo-login")
    assert d2_res.status_code == 200
    d2_token = d2_res.json()["token"]
    d2_owner = d2_res.json()["user"]["owner_id"]
    headers_2 = {"Authorization": f"Bearer {d2_token}"}

    # Different owner IDs
    assert d1_owner != d2_owner
    assert d1_owner.startswith("demo-")
    assert d2_owner.startswith("demo-")

    # Demo 1 logs an action
    client.post(
        f"/owner/log-action/{d1_owner}",
        json={"factor": "credit_utilization", "description": "Demo 1 secret log"},
        headers=headers_1,
    )

    # Demo 2 checks history
    hist_2 = client.get(f"/owner/log-history/{d2_owner}", headers=headers_2)
    assert hist_2.status_code == 200
    assert len(hist_2.json()["actions"]) == 0, "Demo 2 must see 0 actions; no data leakage from Demo 1"
