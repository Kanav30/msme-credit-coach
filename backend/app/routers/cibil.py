"""
Router for CIBIL report uploads, sample downloads, and PDF extraction.
"""

import sys
import os
import io
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from app.routers import owner
import logging_store as store
from cibil_parser import parse_and_diagnose_cibil_pdf, convert_cibil_to_profile, parse_cibil_report_text, extract_text_from_pdf
from cibil_generator import ARCHETYPES_DATA, OUTPUT_DIR, generate_all_sample_reports

router = APIRouter(prefix="/cibil", tags=["cibil"])

# Ensure sample reports exist
if not any(OUTPUT_DIR.glob("*.pdf")):
    generate_all_sample_reports()


@router.post("/upload/{owner_id}")
async def upload_cibil_report(owner_id: str, file: UploadFile = File(...)):
    """
    Accepts an official CIBIL Commercial Credit Information Report (CIR) in PDF format,
    extracts the CMR rank, utilization, repayment history (DPD), and tenure,
    and updates the active MSME profile.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files (.pdf) are supported for CIBIL report parsing.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        pdf_stream = io.BytesIO(contents)
        result = parse_and_diagnose_cibil_pdf(pdf_stream, target_rank=3)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse CIBIL PDF: {str(e)}")

    # Update active profile with parsed values
    raw_text = extract_text_from_pdf(io.BytesIO(contents))
    parsed = parse_cibil_report_text(raw_text)
    new_profile = convert_cibil_to_profile(parsed)
    owner._MOCK_PROFILES[owner_id] = new_profile

    # Persist report and profile into database
    try:
        meta = result.get("extracted_report_metadata", {})
        diag = result.get("diagnostic", {})
        store.save_cibil_report(
            owner_id=owner_id,
            filename=file.filename,
            rcn=meta.get("rcn"),
            company_name=meta.get("company_name"),
            pan=meta.get("pan"),
            gstin=meta.get("gstin"),
            cmr_rank=diag.get("estimated_cmr_rank") or 5,
            total_sanctioned=float(meta.get("total_sanctioned") or 0.0),
            total_balance=float(meta.get("total_balance") or 0.0),
            total_overdue=float(meta.get("total_overdue") or 0.0),
            extracted_payload=result,
        )
        store.save_business_profile(
            owner_id=owner_id,
            data={
                "on_time_payment_pct": new_profile.on_time_payment_pct,
                "has_recent_delinquency": new_profile.has_recent_delinquency,
                "credit_utilization": new_profile.credit_utilization,
                "credit_tenure_years": new_profile.credit_tenure_years,
                "business_age_years": new_profile.business_age_years,
                "industry_risk_category": new_profile.industry_risk_category,
                "estimated_cmr_rank": diag.get("estimated_cmr_rank"),
                "overall_proxy_score": diag.get("overall_score"),
                "source": "cibil_pdf",
            },
        )
    except Exception as e:
        print(f"[Warning] Could not persist CIBIL report to DB: {e}")

    return {
        "success": True,
        "message": f"Successfully parsed CIBIL report for {result['extracted_report_metadata']['company_name']}.",
        "filename": file.filename,
        "extracted_report_metadata": result["extracted_report_metadata"],
        "diagnostic": result["diagnostic"],
        "action_plan": result["action_plan"],
    }


@router.get("/samples")
def get_sample_reports_list():
    """Returns the list of 5 authentic TransUnion CIBIL CIR sample scenarios."""
    samples = []
    for archetype_id, data in ARCHETYPES_DATA.items():
        samples.append({
            "archetype_id": archetype_id,
            "filename": data["filename"],
            "company_name": data["company_name"],
            "cmr_rank": data["cmr_rank"],
            "cmr_tier": data["cmr_tier"],
            "credit_utilization": round(data["credit_utilization"] * 100, 1),
            "tenure_years": data["credit_tenure_years"],
            "business_age_years": data["business_age_years"],
            "has_recent_delinquency": data["has_recent_delinquency"],
            "download_url": f"/api/cibil/download-sample/{archetype_id}",
        })
    return {"samples": samples}


@router.get("/download-sample/{archetype_id}")
def download_sample_cibil_pdf(archetype_id: str):
    """Streams the official sample PDF report for the given archetype."""
    data = ARCHETYPES_DATA.get(archetype_id)
    if not data:
        raise HTTPException(status_code=404, detail="Sample archetype not found.")

    pdf_path = OUTPUT_DIR / data["filename"]
    if not pdf_path.exists():
        generate_all_sample_reports()

    return FileResponse(
        path=str(pdf_path),
        filename=data["filename"],
        media_type="application/pdf",
    )
