"""
Phase 2 Regression Tests: Database Reset and Persistence
- reset-profile removes all associated persisted records (business profile, reports, alternate signals, actions).
- Atomic transactions ensure all-or-nothing cleanups.
- Deleted records do NOT reappear after a backend restart (simulated by cache invalidation).
- Endpoints never report success if database operations fail.
"""

import os
import sys
from pathlib import Path
import pytest
import uuid
from unittest.mock import patch

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


def _setup_owner_with_full_persisted_state():
    uid = uuid.uuid4().hex[:8]
    res = client.post("/auth/signup", json={
        "full_name": "Reset Test Owner",
        "business_name": "Reset Testing Corp",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"reset_{uid}@reset.in",
        "password": "Password123!",
        "target_rank": 3,
    })
    assert res.status_code == 200
    token = res.json()["token"]
    owner_id = res.json()["user"]["owner_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Persist business profile
    client.post(
        f"/owner/profile/{owner_id}",
        json={
            "name": "Reset Testing Corp",
            "on_time_payment_pct": 0.85,
            "has_recent_delinquency": False,
            "credit_utilization": 0.55,
            "credit_tenure_years": 4.0,
            "business_age_years": 5.0,
            "industry_risk_category": "medium",
            "target_rank": 3,
        },
        headers=headers,
    )

    # 2. Persist CIBIL report
    store.save_cibil_report(
        owner_id=owner_id,
        filename="dummy_test_report.pdf",
        rcn="RCN-TEST-9999",
        company_name="Reset Testing Corp",
        pan="ABCDE1234F",
        gstin="27ABCDE1234F1Z5",
        cmr_rank=5,
        official_cmr_rank=5,
        total_sanctioned=5000000.0,
        total_balance=2500000.0,
        total_overdue=0.0,
        extracted_payload={},
        illustrative_cmr_rank=None,
        rank_source="official_bureau",
        report_date="2026-11-01",
        data_provenance="test_suite",
    )

    # 3. Persist alternate signals
    store.save_alternate_signals(owner_id, 0.92, 0.88, "High Cash-Flow Stability")

    # 4. Persist logged actions
    store.log_action(owner_id, "credit_utilization", "Paid down ₹1,00,000 of working capital loan")
    store.log_action(owner_id, "payment_history", "Verified monthly NACH auto-debit")

    return owner_id, headers


def test_reset_profile_removes_all_persisted_records():
    """reset-profile clears business profiles, CIBIL reports, alternate data signals, and action logs."""
    owner_id, headers = _setup_owner_with_full_persisted_state()

    # Pre-condition: verify data exists in DB
    assert store.get_business_profile(owner_id) is not None
    assert len(store.get_cibil_reports(owner_id)) >= 1
    assert store.get_alternate_signals(owner_id) is not None
    assert len(store.get_actions(owner_id)) >= 2

    # Execute reset
    res = client.post(f"/owner/reset-profile/{owner_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "cleared"

    # Post-condition: all records in DB must be deleted
    assert store.get_business_profile(owner_id) is None
    assert len(store.get_cibil_reports(owner_id)) == 0
    assert store.get_alternate_signals(owner_id) is None
    assert len(store.get_actions(owner_id)) == 0


def test_deleted_records_do_not_reappear_after_backend_restart():
    """Simulating restart (wiping in-memory state) confirms deleted records do not reappear."""
    owner_id, headers = _setup_owner_with_full_persisted_state()

    # Reset
    res = client.post(f"/owner/reset-profile/{owner_id}", headers=headers)
    assert res.status_code == 200

    # Simulate restart by completely purging in-memory registries
    owner._MOCK_PROFILES.clear()
    owner._PROFILE_METADATA.clear()

    # Fetch profile via API
    prof_res = client.get(f"/owner/profile/{owner_id}", headers=headers)
    assert prof_res.status_code == 200
    prof_data = prof_res.json()

    assert prof_data["has_data"] is False, "Profile must remain in unpopulated placeholder state"
    assert prof_data["profile"] is None
    assert prof_data["official_cmr_rank"] is None
    assert prof_data["illustrative_cmr_rank"] is None

    # Fetch log history via API
    hist_res = client.get(f"/owner/log-history/{owner_id}", headers=headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()["actions"]) == 0


def test_reset_profile_never_reports_success_on_database_failure():
    """If database transaction fails, reset-profile surfaces a 500 error instead of false success."""
    owner_id, headers = _setup_owner_with_full_persisted_state()

    with patch.object(store, "reset_owner_data", side_effect=RuntimeError("Simulated Disk I/O Failure")):
        res = client.post(f"/owner/reset-profile/{owner_id}", headers=headers)
        assert res.status_code == 500
        assert "Simulated Disk I/O Failure" in res.json()["detail"]
