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
    """
    Regression Test for Akyrus Synthetic Report:
    - official_cmr_rank = null
    - illustrative_cmr_rank = 6
    - exactly two facilities
    - facility names are Cash Credit and Term Loan
    - total sanctioned = 25,00,000
    - total outstanding = 17,50,000
    - total overdue = 0
    - utilization = 70%
    - on-time payment = 96%
    - no recent delinquency
    """
    if not USER_UPLOADED_PDF.exists():
        pytest.skip("User uploaded PDF not found at exact path")

    result = cibil_parser.parse_and_diagnose_cibil_pdf(str(USER_UPLOADED_PDF))
    meta = result["extracted_report_metadata"]

    assert meta["company_name"] == "Akyrus Productions"
    assert meta["official_cmr_rank"] is None, "Synthetic Akyrus report must have official_cmr_rank = null"
    assert meta["illustrative_cmr_rank"] == 6, "Illustrative CMR Band 6 must be captured"
    assert meta["rank_source"] == "illustrative_demo_band"

    # Exactly 2 facilities (no duplicates from repayment history table)
    facilities = meta["facilities"]
    assert len(facilities) == 2, f"Expected exactly 2 facilities, got {len(facilities)}"
    assert [f["facility_name"] for f in facilities] == ["Cash Credit", "Term Loan"]

    # Facility 1: Cash Credit (20L limit, 14L outstanding)
    cc = facilities[0]
    assert cc["sanctioned_amount"] == 2000000.0
    assert cc["outstanding_balance"] == 1400000.0
    assert cc["overdue_amount"] == 0.0

    # Facility 2: Term Loan (5L limit, 3.5L outstanding)
    tl = facilities[1]
    assert tl["sanctioned_amount"] == 500000.0
    assert tl["outstanding_balance"] == 350000.0
    assert tl["overdue_amount"] == 0.0

    assert meta["total_sanctioned"] == 2500000.0
    assert meta["total_balance"] == 1750000.0
    assert meta["total_overdue"] == 0.0
    assert meta["credit_utilization_pct"] == 70.0
    assert meta["on_time_payment_pct"] == 96.0
    assert meta["has_recent_delinquency"] is False
    assert meta["credit_tenure_years"] == 5.0
    assert meta["business_age_years"] == 7.0
    assert meta["rcn"] == "DEMO-AP-2026-11012"


def test_akyrus_upload_and_dashboard_api_synchronization():
    """
    Verify upload response AND dashboard API responses stay in sync:
    - Refreshes profile from saved report
    - Confirms identical values appear on extraction response and dashboard
    - Does not display older profile or target rank as current rank
    - Does not show fabricated official CMR
    """
    if not USER_UPLOADED_PDF.exists():
        pytest.skip("User uploaded PDF not found at exact path")

    import uuid
    uid = uuid.uuid4().hex[:8]
    signup_res = client.post("/auth/signup", json={
        "full_name": "Akyrus Founder",
        "business_name": "Akyrus Productions",
        "phone": f"+91{uuid.uuid4().int % 10000000000:010d}",
        "email": f"akyrus_{uid}@production.in",
        "password": "Password123!",
        "target_rank": 2,
    })
    assert signup_res.status_code == 200
    token = signup_res.json()["token"]
    owner_id = signup_res.json()["user"]["owner_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload Akyrus PDF
    with open(USER_UPLOADED_PDF, "rb") as f:
        upload_res = client.post(
            f"/cibil/upload/{owner_id}",
            files={"file": ("Akyrus_Productions_Synthetic_Credit_Report.pdf", f, "application/pdf")},
            headers=headers,
        )
    assert upload_res.status_code == 200
    up_data = upload_res.json()
    up_meta = up_data["extracted_report_metadata"]

    assert up_meta["official_cmr_rank"] is None
    assert up_meta["illustrative_cmr_rank"] == 6
    assert len(up_meta["facilities"]) == 2
    assert up_meta["total_sanctioned"] == 2500000.0
    assert up_meta["total_balance"] == 1750000.0
    assert up_meta["credit_utilization_pct"] == 70.0

    # Verify Dashboard Diagnostic API Response
    diag_res = client.get(f"/owner/diagnostic/{owner_id}", headers=headers)
    assert diag_res.status_code == 200
    diag = diag_res.json()
    assert diag["has_data"] is True
    assert diag["official_cmr_rank"] is None, "Official CMR must be null in dashboard for synthetic demo report"
    assert diag["illustrative_cmr_rank"] == 6
    assert diag["estimated_cmr_rank"] == up_data["diagnostic"]["estimated_cmr_rank"]
    assert diag["overall_score"] == up_data["diagnostic"]["overall_score"]

    # Verify Owner Profile API Response
    prof_res = client.get(f"/owner/profile/{owner_id}", headers=headers)
    assert prof_res.status_code == 200
    prof = prof_res.json()
    assert prof["has_data"] is True
    assert prof["official_cmr_rank"] is None
    assert prof["illustrative_cmr_rank"] == 6
    assert prof["metadata"]["name"] == "Akyrus Productions"
    assert prof["metadata"]["target_rank"] == 2, "Target rank preserved and never used as current rank"
    assert prof["profile"]["credit_utilization"] == 0.70
    assert prof["profile"]["on_time_payment_pct"] == 0.96

    # Verify Profiles list endpoint
    list_res = client.get("/owner/profiles", headers=headers)
    assert list_res.status_code == 200
    active_prof = [p for p in list_res.json()["profiles"] if p["owner_id"] == owner_id][0]
    assert active_prof["official_cmr_rank"] is None
    assert active_prof["illustrative_cmr_rank"] == 6
    assert active_prof["credit_utilization"] == 0.70


def test_context_aware_cmr_matrix_variations():
    """
    Tests edge cases for CMR context awareness:
    - Report with explicit official CMR
    - Report with no CMR
    - Report with only Target CMR
    - Report with both official and illustrative mentions
    - Ambiguous CMR references
    """
    # 1. Genuine / Official CMR report (Sharma)
    sharma_path = OUTPUT_DIR / ARCHETYPES_DATA["demo-owner-1"]["filename"]
    res_sharma = cibil_parser.parse_and_diagnose_cibil_pdf(sharma_path)
    assert res_sharma["extracted_report_metadata"]["official_cmr_rank"] == 6
    assert res_sharma["extracted_report_metadata"]["illustrative_cmr_rank"] is None
    assert res_sharma["extracted_report_metadata"]["rank_source"] == "official_bureau_assessment"

    # 2. Synthetic Illustrative CMR report (Akyrus)
    res_akyrus = cibil_parser.parse_and_diagnose_cibil_pdf(str(USER_UPLOADED_PDF))
    assert res_akyrus["extracted_report_metadata"]["official_cmr_rank"] is None
    assert res_akyrus["extracted_report_metadata"]["illustrative_cmr_rank"] == 6
    assert res_akyrus["extracted_report_metadata"]["rank_source"] == "illustrative_demo_band"

    # 3. Text variation tests using extract_structured_cibil_data helper
    from unittest.mock import patch

    # A: Report with only Target CMR
    with patch("app.core.cibil_parser.extract_raw_pages_and_tables") as mock_extract:
        mock_extract.return_value = (
            [{"page": 1, "text": "Target Eligibility: CMR-2 for commercial credit. Credit limit INR 50,00,000."}],
            [],
            "Target Eligibility: CMR-2 for commercial credit. Credit limit INR 50,00,000."
        )
        extracted = cibil_parser.extract_structured_cibil_data(b"%PDF-1.4\n...")
        assert extracted["official_cmr_rank"] is None
        assert extracted["illustrative_cmr_rank"] is None
        assert extracted["rank_source"] == "target_only"

    # B: Report with both official and illustrative mentions
    with patch("app.core.cibil_parser.extract_raw_pages_and_tables") as mock_extract:
        t_off = [
            ["CIBIL MSME RANK (CMR) ASSESSMENT", None],
            ["CMR-5\nOfficial Commercial Bureau Scale", "Assessment Details"]
        ]
        t_ill = [
            ["Illustrative CMR Band", "4"]
        ]
        mock_extract.return_value = (
            [{"page": 1, "text": "Official Assessment CMR-5. Illustrative CMR Band: 4."}],
            [{"page": 1, "table": t_off}, {"page": 1, "table": t_ill}],
            "Official Assessment CMR-5. Illustrative CMR Band: 4."
        )
        extracted = cibil_parser.extract_structured_cibil_data(b"%PDF-1.4\n...")
        assert extracted["official_cmr_rank"] == 5
        assert extracted["illustrative_cmr_rank"] == 4
        assert extracted["rank_source"] == "official_and_illustrative"

    # C: Report with ambiguous CMR reference
    with patch("app.core.cibil_parser.extract_raw_pages_and_tables") as mock_extract:
        mock_extract.return_value = (
            [{"page": 1, "text": "Historical CMR performance benchmark discussed with auditor."}],
            [],
            "Historical CMR performance benchmark discussed with auditor."
        )
        extracted = cibil_parser.extract_structured_cibil_data(b"%PDF-1.4\n...")
        assert extracted["official_cmr_rank"] is None
        assert extracted["illustrative_cmr_rank"] is None
        assert extracted["rank_source"] == "ambiguous"
        assert extracted["needs_manual_review"] is True

    # D: Report with no CMR mentioned at all
    with patch("app.core.cibil_parser.extract_raw_pages_and_tables") as mock_extract:
        mock_extract.return_value = (
            [{"page": 1, "text": "Financial health statement. Total Sanctioned Limit: INR 10,00,000."}],
            [],
            "Financial health statement. Total Sanctioned Limit: INR 10,00,000."
        )
        extracted = cibil_parser.extract_structured_cibil_data(b"%PDF-1.4\n...")
        assert extracted["official_cmr_rank"] is None
        assert extracted["illustrative_cmr_rank"] is None
        assert extracted["rank_source"] == "not_found"
        assert extracted["needs_manual_review"] is False


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
