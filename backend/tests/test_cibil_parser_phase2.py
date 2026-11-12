"""
Test Suite for Phase 2: PDF Parsing, Validation, and Commercial Credit Report Ingestion.
Verifies structured extraction, DPD isolation, absence of fabricated defaults,
separation of official CMR vs estimated proxy ranks, and sample report loading.
"""

import os
import sys
import io
import pytest
from pathlib import Path

# Configure test environment
os.environ["DB_ENGINE"] = "sqlite"

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ML_SRC_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "..", "ml", "src"))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, ML_SRC_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.core import cibil_parser, logging_store as store, security
from app.core.cibil_generator import ARCHETYPES_DATA, OUTPUT_DIR, generate_all_sample_reports

client = TestClient(app)

# Ensure sample reports exist
if not any(OUTPUT_DIR.glob("*.pdf")):
    generate_all_sample_reports()

USER_UPLOADED_PDF = Path(r"C:\Users\Kanav\.gemini\antigravity\brain\af8b518c-99e4-4ba2-a8c9-a79c0f790f1c\.user_uploaded\media_1794479902016_b47462d6.pdf")


def test_all_five_bundled_sample_pdfs_parse_accurately():
    """All 5 bundled sample PDFs parse with correctly extracted and validated fields."""
    expected_data = {
        "demo-owner-1": {"cmr": 6, "util": 78.0, "recent_delinq": True, "tenure": 3.0, "biz_age": 6.0},
        "patel-textiles": {"cmr": 2, "util": 45.0, "recent_delinq": False, "tenure": 8.0, "biz_age": 12.0},
        "gupta-crafts": {"cmr": 4, "util": 20.0, "recent_delinq": False, "tenure": 0.5, "biz_age": 1.0},
        "verma-auto": {"cmr": 3, "util": 95.0, "recent_delinq": False, "tenure": 9.0, "biz_age": 14.0},
        "reddy-pharma": {"cmr": 4, "util": 55.0, "recent_delinq": False, "tenure": 4.0, "biz_age": 5.0},
    }

    for arch_id, exp in expected_data.items():
        pdf_path = OUTPUT_DIR / ARCHETYPES_DATA[arch_id]["filename"]
        assert pdf_path.exists(), f"Sample PDF for {arch_id} must exist"

        result = cibil_parser.parse_and_diagnose_cibil_pdf(pdf_path)
        meta = result["extracted_report_metadata"]

        assert meta["official_cmr_rank"] == exp["cmr"], f"Failed CMR for {arch_id}"
        assert meta["credit_utilization_pct"] == exp["util"], f"Failed Util for {arch_id}"
        assert meta["has_recent_delinquency"] == exp["recent_delinq"], f"Failed Delinquency for {arch_id}"
        assert meta["credit_tenure_years"] == exp["tenure"], f"Failed Tenure for {arch_id}"
        assert meta["business_age_years"] == exp["biz_age"], f"Failed Biz Age for {arch_id}"
        assert len(meta["facilities"]) >= 1, f"Should extract facilities for {arch_id}"


def test_user_uploaded_akyrus_pdf_parses_accurately():
    """The user's uploaded synthetic report parses without falling back to fake defaults."""
    if not USER_UPLOADED_PDF.exists():
        pytest.skip("User uploaded PDF not found at exact path")

    result = cibil_parser.parse_and_diagnose_cibil_pdf(str(USER_UPLOADED_PDF))
    meta = result["extracted_report_metadata"]

    assert meta["company_name"] == "Akyrus Productions"
    assert meta["official_cmr_rank"] == 6
    assert meta["credit_utilization_pct"] == 70.0
    assert meta["credit_tenure_years"] == 5.0
    assert meta["business_age_years"] == 7.0
    assert meta["has_recent_delinquency"] is False
    assert meta["on_time_payment_pct"] >= 95.0
    assert meta["total_sanctioned"] == 2500000.0
    assert meta["total_balance"] == 1750000.0
    assert meta["rcn"] == "DEMO-AP-2026-11012"


def test_clean_repayment_scenarios_not_marked_delinquent():
    """Clean repayment scenarios do not get falsely marked delinquent by '030' in text/legend."""
    patel_path = OUTPUT_DIR / ARCHETYPES_DATA["patel-textiles"]["filename"]
    res = cibil_parser.parse_and_diagnose_cibil_pdf(patel_path)
    meta = res["extracted_report_metadata"]

    assert meta["has_recent_delinquency"] is False
    assert meta["on_time_payment_pct"] == 100.0


def test_historical_delay_distinguished_from_recent_delay():
    """Sharma report has recent 30-day delay, which is flagged as recent delinquency."""
    sharma_path = OUTPUT_DIR / ARCHETYPES_DATA["demo-owner-1"]["filename"]
    res = cibil_parser.parse_and_diagnose_cibil_pdf(sharma_path)
    meta = res["extracted_report_metadata"]

    assert meta["has_recent_delinquency"] is True
    assert meta["facilities"][0]["has_recent_delinquency"] is True
    # The second facility (term loan) has no delinquency
    assert meta["facilities"][1]["has_recent_delinquency"] is False


def test_unsupported_and_empty_pdfs_rejected_with_clean_errors():
    """Invalid, empty, or unsupported PDFs raise helpful errors and do not fabricate scores."""
    # 1. Empty PDF
    with pytest.raises(ValueError, match="empty"):
        cibil_parser.validate_pdf_content(b"")

    # 2. Corrupt / Non-PDF bytes
    with pytest.raises(ValueError, match="standard '%PDF-'"):
        cibil_parser.validate_pdf_content(b"This is not a PDF file")

    # 3. Size limit enforcement
    large_fake_pdf = b"%PDF-1.4\n" + (b"0" * (11 * 1024 * 1024))
    with pytest.raises(ValueError, match="maximum allowed size"):
        cibil_parser.validate_pdf_content(large_fake_pdf)


def test_official_and_estimated_ranks_kept_strictly_separate():
    """Official CMR rank from CIR and Coach estimated diagnostic proxy rank are kept separate."""
    sharma_path = OUTPUT_DIR / ARCHETYPES_DATA["demo-owner-1"]["filename"]
    res = cibil_parser.parse_and_diagnose_cibil_pdf(sharma_path)

    official_cmr = res["extracted_report_metadata"]["official_cmr_rank"]
    estimated_cmr = res["diagnostic"]["estimated_cmr_rank"]

    assert official_cmr == 6, "Official bureau rank in Sharma CIR is 6"
    assert estimated_cmr == 5, "Coach diagnostic estimated proxy rank is 5"
    assert official_cmr != estimated_cmr, "They must not be conflated"


def test_sample_report_loading_endpoint():
    """The /cibil/load-sample endpoint securely loads, parses, and persists a sample scenario."""
    import uuid
    uid = uuid.uuid4().hex[:8]
    # Create test user with unique credentials
    signup_res = client.post("/auth/signup", json={
        "full_name": "Test Tester",
        "business_name": "Test Engineering",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"tester_{uid}@example.com",
        "password": "Password123!",
        "target_rank": 3,
    })
    assert signup_res.status_code == 200
    token = signup_res.json()["token"]
    owner_id = signup_res.json()["user"]["owner_id"]

    # Load Patel Textiles sample
    headers = {"Authorization": f"Bearer {token}"}
    load_res = client.post(f"/cibil/load-sample/{owner_id}/patel-textiles", headers=headers)
    assert load_res.status_code == 200
    data = load_res.json()

    assert data["success"] is True
    assert data["extracted_report_metadata"]["company_name"] == "PATEL TECHNICAL TEXTILES PRIVATE LIMITED"
    assert data["extracted_report_metadata"]["official_cmr_rank"] == 2
    assert data["extracted_report_metadata"]["credit_utilization_pct"] == 45.0

    # Verify database persistence stored official CMR and estimated CMR separately
    reports = store.get_cibil_reports(owner_id)
    assert len(reports) >= 1
    latest = reports[0]
    assert latest["company_name"] == "PATEL TECHNICAL TEXTILES PRIVATE LIMITED"
    assert latest["cmr_rank"] == 2  # official CMR
    assert latest["official_cmr_rank"] == 2
    assert latest["data_provenance"] == "sample_patel-textiles"
