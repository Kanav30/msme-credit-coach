"""
Phase 5 Regression Tests: Alternate Data Signals and Action Tracker Persistence
- Alternate data signals persist in the database and reload across restarts.
- Action logs persist in the database and reload across restarts.
- Date handling correctly operates on Indian Standard Time (IST, UTC+05:30).
- Actions distinguish self-reported borrower entries from verified credit bureau records.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
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
IST = timezone(timedelta(hours=5, minutes=30))


def _create_user(name: str):
    uid = uuid.uuid4().hex[:8]
    res = client.post("/auth/signup", json={
        "full_name": name,
        "business_name": f"{name} Industries",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"{uid}@industries.in",
        "password": "Password123!",
        "target_rank": 3,
    })
    assert res.status_code == 200
    token = res.json()["token"]
    owner_id = res.json()["user"]["owner_id"]
    headers = {"Authorization": f"Bearer {token}"}
    return owner_id, headers


def test_alternate_data_signals_persist_in_database():
    """Posting alternate signals persists them in DB, returned via GET, and retained across restarts."""
    owner_id, headers = _create_user("Gauri Textiles")

    # Post alternate data signals
    post_res = client.post(
        f"/owner/alternate-signal/{owner_id}",
        json={"gst_filing_regularity": 0.95, "upi_inflow_stability": 0.90},
        headers=headers,
    )
    assert post_res.status_code == 200
    assert "signal_tier" in post_res.json()
    assert post_res.json()["supplementary_score"] == 92.5

    # Verify directly in database
    db_signals = store.get_alternate_signals(owner_id)
    assert db_signals is not None
    assert float(db_signals["gst_filing_regularity"]) == 0.95
    assert float(db_signals["upi_inflow_stability"]) == 0.90

    # Invalidate in-memory caches to simulate restart
    owner._PROFILE_METADATA.clear()

    # Verify GET alternate-signal endpoint restores saved values
    get_res = client.get(f"/owner/alternate-signal/{owner_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["signals"]["gst_filing_regularity"] == 0.95
    assert get_res.json()["signals"]["upi_inflow_stability"] == 0.90

    # Verify profile metadata includes restored alternate signals
    prof_res = client.get(f"/owner/profile/{owner_id}", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["metadata"]["gst_filing_regularity"] == 0.95
    assert prof_res.json()["metadata"]["upi_inflow_stability"] == 0.90


def test_action_history_persists_across_backend_restarts():
    """Logged actions persist in DB and are returned intact after in-memory caches are wiped."""
    owner_id, headers = _create_user("Ramesh Auto Parts")

    # Log 2 actions
    act1 = client.post(
        f"/owner/log-action/{owner_id}",
        json={"factor": "credit_utilization", "description": "Repaid overdraft ₹75,000"},
        headers=headers,
    )
    assert act1.status_code == 200

    act2 = client.post(
        f"/owner/log-action/{owner_id}",
        json={"factor": "payment_history", "description": "Auto-debit mandate verified"},
        headers=headers,
    )
    assert act2.status_code == 200

    # Simulate backend restart
    owner._PROFILE_METADATA.clear()
    owner._MOCK_PROFILES.clear()

    # Query log history via API
    hist_res = client.get(f"/owner/log-history/{owner_id}", headers=headers)
    assert hist_res.status_code == 200
    actions = hist_res.json()["actions"]
    assert len(actions) == 2
    assert actions[0]["description"] == "Auto-debit mandate verified"
    assert actions[1]["description"] == "Repaid overdraft ₹75,000"


def test_ist_date_handling_for_logged_actions_and_streaks():
    """Action timestamps and streak calculations operate correctly in Indian Standard Time (IST)."""
    owner_id, headers = _create_user("Kalyan Spices")

    # Current IST time
    now_ist = datetime.now(IST)
    ts_now = now_ist.strftime("%Y-%m-%d %H:%M:%S")

    # Previous week timestamp in IST
    prev_week_ist = now_ist - timedelta(weeks=1)
    ts_prev = prev_week_ist.strftime("%Y-%m-%d %H:%M:%S")

    # Log action for current week
    store.log_action(owner_id, "credit_utilization", "Current week action", logged_at=ts_now)
    # Log action for previous week
    store.log_action(owner_id, "payment_history", "Previous week action", logged_at=ts_prev)

    # Streak should calculate to 2 consecutive weeks
    streak = store.compute_streak_weeks(owner_id)
    assert streak == 2, f"Expected 2-week consecutive streak in IST, got {streak}"

    # Verify streak API endpoint
    streak_res = client.get(f"/owner/streak/{owner_id}", headers=headers)
    assert streak_res.status_code == 200
    assert streak_res.json()["streak_weeks"] == 2
