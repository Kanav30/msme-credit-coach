"""
Phase 6 Regression Tests: Simulation Disclosures, Truthful Claims, and Model Integrity
- Project-generated scores are strictly separated from official bureau ranks.
- Trajectory projections are labeled hypothetical with explicit fixed assumptions disclosed.
- Guaranteed loan eligibility or approval claims are removed.
- Random Forest model operates intact as a surrogate validator without artificial retraining.
"""

import os
import sys
from pathlib import Path
import pytest
import uuid
from sklearn.ensemble import RandomForestRegressor

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


def _create_user(name: str):
    uid = uuid.uuid4().hex[:8]
    res = client.post("/auth/signup", json={
        "full_name": name,
        "business_name": f"{name} Solutions",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"{uid}@solutions.in",
        "password": "Password123!",
        "target_rank": 3,
    })
    assert res.status_code == 200
    token = res.json()["token"]
    owner_id = res.json()["user"]["owner_id"]
    headers = {"Authorization": f"Bearer {token}"}
    return owner_id, headers


def test_simulation_results_labeled_hypothetical_with_fixed_assumptions():
    """Both prediction and what-if endpoints disclose hypothetical status and fixed mathematical assumptions."""
    owner_id, headers = _create_user("Disclosures MSME")

    # Save a profile so prediction has data
    client.post(
        f"/owner/profile/{owner_id}",
        json={
            "name": "Disclosures MSME",
            "on_time_payment_pct": 0.80,
            "has_recent_delinquency": True,
            "credit_utilization": 0.70,
            "credit_tenure_years": 3.0,
            "business_age_years": 4.0,
            "industry_risk_category": "medium",
            "target_rank": 3,
        },
        headers=headers,
    )

    # 1. Prediction endpoint
    pred_res = client.get(f"/owner/prediction/{owner_id}", headers=headers)
    assert pred_res.status_code == 200
    pred = pred_res.json()

    assert pred["is_hypothetical"] is True
    assert "fixed_assumptions" in pred
    assert pred["fixed_assumptions"]["credit_utilization_drop_per_month"] == 0.08
    assert pred["fixed_assumptions"]["on_time_payment_improvement_per_month"] == 0.03
    assert pred["fixed_assumptions"]["delinquency_aging_months"] == 3
    assert "legal_notice" in pred
    assert "not an official" in pred["legal_notice"].lower() or "hypothetical" in pred["legal_notice"].lower()

    # 2. What-If Sandbox simulation endpoint
    sim_res = client.post(
        f"/owner/simulate-what-if/{owner_id}",
        json={"target_rank": 2, "max_months": 12},
        headers=headers,
    )
    assert sim_res.status_code == 200
    sim = sim_res.json()

    assert sim["is_hypothetical"] is True
    assert sim["fixed_assumptions"]["credit_utilization_drop_per_month"] == 0.08
    assert "legal_notice" in sim


def test_separation_of_project_scores_from_official_cmr():
    """Official CMR column in reports store is never overwritten by estimated proxy scores."""
    owner_id, headers = _create_user("Rank Separation MSME")

    # Persist official CIR report with official CMR rank = 6
    store.save_cibil_report(
        owner_id=owner_id,
        filename="official_cir.pdf",
        rcn="RCN-OFFICIAL-123",
        company_name="Rank Separation MSME",
        cmr_rank=6,
        official_cmr_rank=6,
        total_sanctioned=2000000.0,
        total_balance=1400000.0,
        total_overdue=0.0,
        data_provenance="official_upload",
    )

    # Save business profile with estimated proxy rank = 4
    store.save_business_profile(owner_id, {
        "on_time_payment_pct": 0.90,
        "has_recent_delinquency": False,
        "credit_utilization": 0.70,
        "credit_tenure_years": 3.0,
        "business_age_years": 4.0,
        "industry_risk_category": "medium",
        "estimated_cmr_rank": 4,
        "overall_proxy_score": 68.0,
    })

    # Read back report from database
    reports = store.get_cibil_reports(owner_id)
    assert len(reports) == 1
    assert reports[0]["official_cmr_rank"] == 6, "Official CMR rank must remain exactly 6"
    assert reports[0]["cmr_rank"] == 6

    # Verify profile API preserves distinction
    prof_res = client.get(f"/owner/profile/{owner_id}", headers=headers)
    assert prof_res.status_code == 200
    prof = prof_res.json()
    assert prof["official_cmr_rank"] == 6
    assert prof["diagnostic_preview"]["official_cmr_rank"] == 6


def test_random_forest_surrogate_model_intact():
    """Random Forest surrogate model is loaded, trained as expected, and not artificially manipulated."""
    assert isinstance(owner._trajectory_model, RandomForestRegressor)
    assert hasattr(owner._trajectory_model, "estimators_")
    assert len(owner._trajectory_model.estimators_) > 0
    assert owner._trajectory_model_metrics is not None
    assert "r2" in owner._trajectory_model_metrics
    # R2 should be within valid bounds (surrogate learned simulator rules)
    assert 0.70 <= owner._trajectory_model_metrics["r2"] <= 1.0
