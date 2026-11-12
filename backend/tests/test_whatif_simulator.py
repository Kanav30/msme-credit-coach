"""
Phase 1 Regression Tests: What-If Scenario Sandbox
- User-adjustable hypothetical inputs reach backend and calculate on-the-fly.
- Changing utilization alters simulated trajectory.
- Changing payment percentage alters simulated trajectory.
- Changing target rank alters months to target.
- Running what-if simulations NEVER mutates or overwrites the saved business profile.
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
from app.routers import owner

client = TestClient(app)


def _create_authenticated_test_user():
    uid = uuid.uuid4().hex[:8]
    res = client.post("/auth/signup", json={
        "full_name": "WhatIf MSME Founder",
        "business_name": "Precision Engineering Works",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"whatif_{uid}@precision.in",
        "password": "Password123!",
        "target_rank": 3,
        "industry_category": "medium",
    })
    assert res.status_code == 200
    token = res.json()["token"]
    owner_id = res.json()["user"]["owner_id"]
    headers = {"Authorization": f"Bearer {token}"}
    return owner_id, headers


def test_whatif_changing_utilization_alters_trajectory():
    """Adjusting hypothetical utilization improves the simulated trajectory."""
    owner_id, headers = _create_authenticated_test_user()

    # Simulate with high utilization (85%)
    res_high = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 2,
            "max_months": 24,
            "credit_utilization": 0.85,
            "on_time_payment_pct": 0.90,
            "has_recent_delinquency": False,
        },
        headers=headers,
    )
    assert res_high.status_code == 200
    data_high = res_high.json()
    high_m0_score = data_high["simulator_prediction"]["trajectory"][0]["overall_score"]

    # Simulate with low utilization (20%)
    res_low = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 2,
            "max_months": 24,
            "credit_utilization": 0.20,
            "on_time_payment_pct": 0.90,
            "has_recent_delinquency": False,
        },
        headers=headers,
    )
    assert res_low.status_code == 200
    data_low = res_low.json()
    low_m0_score = data_low["simulator_prediction"]["trajectory"][0]["overall_score"]

    # Low utilization must produce a strictly higher starting score
    assert low_m0_score > high_m0_score, f"Expected low util score {low_m0_score} > high util score {high_m0_score}"


def test_whatif_changing_payment_percentage_alters_trajectory():
    """Adjusting payment percentage alters simulated starting score and trajectory."""
    owner_id, headers = _create_authenticated_test_user()

    # Simulate with poor payment conduct (60%)
    res_poor = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 3,
            "max_months": 24,
            "on_time_payment_pct": 0.60,
            "credit_utilization": 0.50,
        },
        headers=headers,
    )
    assert res_poor.status_code == 200
    score_poor = res_poor.json()["simulator_prediction"]["trajectory"][0]["overall_score"]

    # Simulate with flawless payment conduct (100%)
    res_perfect = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 3,
            "max_months": 24,
            "on_time_payment_pct": 1.00,
            "credit_utilization": 0.50,
        },
        headers=headers,
    )
    assert res_perfect.status_code == 200
    score_perfect = res_perfect.json()["simulator_prediction"]["trajectory"][0]["overall_score"]

    assert score_perfect > score_poor, f"Expected perfect payment score {score_perfect} > poor score {score_poor}"


def test_whatif_changing_target_rank():
    """Changing target rank changes target_reached and months_to_target."""
    owner_id, headers = _create_authenticated_test_user()

    # Easy target (CMR-5)
    res_easy = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 5,
            "max_months": 24,
            "credit_utilization": 0.60,
            "on_time_payment_pct": 0.90,
        },
        headers=headers,
    )
    assert res_easy.status_code == 200
    pred_easy = res_easy.json()["simulator_prediction"]

    # Hard target (CMR-1)
    res_hard = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 1,
            "max_months": 24,
            "credit_utilization": 0.60,
            "on_time_payment_pct": 0.90,
        },
        headers=headers,
    )
    assert res_hard.status_code == 200
    pred_hard = res_hard.json()["simulator_prediction"]

    assert res_easy.json()["target_rank"] == 5
    assert res_hard.json()["target_rank"] == 1
    # Months to reach CMR-5 should be less than or equal to CMR-1
    if pred_easy["target_reached"] and pred_hard["target_reached"]:
        assert pred_easy["months_to_target"] <= pred_hard["months_to_target"]


def test_whatif_never_overwrites_saved_business_profile():
    """Simulating what-if scenarios never mutates or overwrites the saved business profile."""
    owner_id, headers = _create_authenticated_test_user()

    # Save an official profile with known values
    save_res = client.post(
        f"/owner/profile/{owner_id}",
        json={
            "name": "Actual Saved Business",
            "on_time_payment_pct": 0.75,
            "has_recent_delinquency": True,
            "credit_utilization": 0.70,
            "credit_tenure_years": 4.0,
            "business_age_years": 5.0,
            "industry_risk_category": "medium",
            "target_rank": 3,
        },
        headers=headers,
    )
    assert save_res.status_code == 200

    # Run What-If simulation with completely different hypothetical values
    sim_res = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={
            "monthly_effort": {"credit_utilization": True, "payment_history": True},
            "target_rank": 1,
            "max_months": 24,
            "credit_utilization": 0.15,
            "on_time_payment_pct": 1.00,
            "has_recent_delinquency": False,
            "credit_tenure_years": 10.0,
            "business_age_years": 15.0,
            "industry_risk_category": "low",
        },
        headers=headers,
    )
    assert sim_res.status_code == 200

    # Verify that the saved profile remains completely unchanged
    prof_res = client.get(f"/owner/profile/{owner_id}", headers=headers)
    assert prof_res.status_code == 200
    prof = prof_res.json()["profile"]

    assert prof["credit_utilization"] == 0.70, "Saved credit_utilization must not be overwritten"
    assert prof["on_time_payment_pct"] == 0.75, "Saved on_time_payment_pct must not be overwritten"
    assert prof["has_recent_delinquency"] is True, "Saved delinquency must not be overwritten"
    assert prof["credit_tenure_years"] == 4.0, "Saved tenure must not be overwritten"
    assert prof["business_age_years"] == 5.0, "Saved business age must not be overwritten"
    assert prof["industry_risk_category"] == "medium", "Saved industry risk must not be overwritten"

    # Also check database directly
    db_profile = store.get_business_profile(owner_id)
    assert db_profile["credit_utilization"] == 0.70
    assert db_profile["on_time_payment_pct"] == 0.75
