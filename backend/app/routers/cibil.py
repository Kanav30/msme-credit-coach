"""
Router for CIBIL report uploads, sample downloads, and PDF extraction.
"""

import sys
import os
import io
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from app.routers import owner
try:
    from app.core import logging_store as store
    from app.core import security
except ModuleNotFoundError:
    import logging_store as store
    import security
from cibil_parser import parse_and_diagnose_cibil_pdf, convert_cibil_to_profile, parse_cibil_report_text, extract_text_from_pdf
from cibil_generator import ARCHETYPES_DATA, OUTPUT_DIR, generate_all_sample_reports

router = APIRouter(prefix="/cibil", tags=["cibil"])

# Ensure sample reports exist
if not any(OUTPUT_DIR.glob("*.pdf")):
    generate_all_sample_reports()


@router.post("/upload/{owner_id}")
async def upload_cibil_report(
    owner_id: str,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """
    Accepts an official or synthetic CIBIL Commercial Credit Information Report (CIR) in PDF format,
    validates format/integrity, extracts business identity, official CMR rank, facilities, and repayment DPD track,
    and updates the active MSME profile.
    """
    security.verify_owner_access(owner_id, current_user)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files (.pdf) are supported for commercial credit report parsing.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Uploaded PDF exceeds the maximum 10MB file size limit.")

    try:
        # Run single-pass validated extraction pipeline
        user_defaults = {
            "industry_category": current_user.get("industry_category", "medium"),
        }
        result = parse_and_diagnose_cibil_pdf(
            io.BytesIO(contents),
            target_rank=current_user.get("target_rank", 3),
            fallback_defaults=user_defaults,
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse commercial credit PDF: {str(e)}")

    meta = result.get("extracted_report_metadata", {})
    diag = result.get("diagnostic", {})
    new_profile = result.get("profile")

    # Update in-memory active profile
    owner._MOCK_PROFILES[owner_id] = new_profile

    # Persist report and profile into database with clear separation of official vs estimated CMR
    try:
        official_cmr = meta.get("official_cmr_rank")
        estimated_cmr = diag.get("estimated_cmr_rank")
        report_date = meta.get("report_date")

        store.save_cibil_report(
            owner_id=owner_id,
            filename=file.filename,
            rcn=meta.get("rcn"),
            company_name=meta.get("company_name"),
            pan=meta.get("pan"),
            gstin=meta.get("gstin"),
            official_cmr_rank=official_cmr,
            estimated_cmr_rank=estimated_cmr,
            report_date=report_date,
            data_provenance="user_upload",
            total_sanctioned=float(meta.get("total_sanctioned") or 0.0),
            total_balance=float(meta.get("total_balance") or 0.0),
            total_overdue=float(meta.get("total_overdue") or 0.0),
            extracted_payload=result,
        )
        store.save_business_profile(
            owner_id=owner_id,
            data={
                "on_time_payment_pct": new_profile.on_time_payment_pct if new_profile else None,
                "has_recent_delinquency": new_profile.has_recent_delinquency if new_profile else None,
                "credit_utilization": new_profile.credit_utilization if new_profile else None,
                "credit_tenure_years": new_profile.credit_tenure_years if new_profile else None,
                "business_age_years": new_profile.business_age_years if new_profile else None,
                "industry_risk_category": new_profile.industry_risk_category if new_profile else "medium",
                "estimated_cmr_rank": estimated_cmr,
                "overall_proxy_score": diag.get("overall_score"),
                "source": "cibil_pdf",
            },
        )
    except Exception as e:
        print(f"[Warning] Could not persist CIBIL report to DB: {e}")

    company_display = meta.get("company_name") or "Commercial Entity"
    return {
        "success": True,
        "message": f"Successfully parsed commercial credit report for {company_display}.",
        "filename": file.filename,
        "extracted_report_metadata": meta,
        "diagnostic": diag,
        "action_plan": result["action_plan"],
    }


@router.post("/load-sample/{owner_id}/{archetype_id}")
def load_cibil_sample(
    owner_id: str,
    archetype_id: str,
    current_user: Dict[str, Any] = Depends(security.get_current_user),
):
    """
    Loads and runs the exact same parsing and diagnosis pipeline on a pre-bundled sample scenario.
    Ensures frontend and backend contracts match and reuses standard validation.
    """
    security.verify_owner_access(owner_id, current_user)
    data = ARCHETYPES_DATA.get(archetype_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Sample archetype '{archetype_id}' not found.")

    pdf_path = OUTPUT_DIR / data["filename"]
    if not pdf_path.exists():
        generate_all_sample_reports()

    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        user_defaults = {
            "industry_category": current_user.get("industry_category", "medium"),
        }
        result = parse_and_diagnose_cibil_pdf(
            io.BytesIO(pdf_bytes),
            target_rank=data.get("target_rank", current_user.get("target_rank", 3)),
            fallback_defaults=user_defaults,
        )
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse sample scenario PDF: {str(e)}")

    meta = result.get("extracted_report_metadata", {})
    diag = result.get("diagnostic", {})
    new_profile = result.get("profile")

    owner._MOCK_PROFILES[owner_id] = new_profile

    try:
        official_cmr = meta.get("official_cmr_rank")
        estimated_cmr = diag.get("estimated_cmr_rank")

        store.save_cibil_report(
            owner_id=owner_id,
            filename=data["filename"],
            rcn=meta.get("rcn"),
            company_name=meta.get("company_name"),
            pan=meta.get("pan"),
            gstin=meta.get("gstin"),
            official_cmr_rank=official_cmr,
            estimated_cmr_rank=estimated_cmr,
            report_date=meta.get("report_date"),
            data_provenance=f"sample_{archetype_id}",
            total_sanctioned=float(meta.get("total_sanctioned") or 0.0),
            total_balance=float(meta.get("total_balance") or 0.0),
            total_overdue=float(meta.get("total_overdue") or 0.0),
            extracted_payload=result,
        )
        store.save_business_profile(
            owner_id=owner_id,
            data={
                "on_time_payment_pct": new_profile.on_time_payment_pct if new_profile else None,
                "has_recent_delinquency": new_profile.has_recent_delinquency if new_profile else None,
                "credit_utilization": new_profile.credit_utilization if new_profile else None,
                "credit_tenure_years": new_profile.credit_tenure_years if new_profile else None,
                "business_age_years": new_profile.business_age_years if new_profile else None,
                "industry_risk_category": new_profile.industry_risk_category if new_profile else "medium",
                "estimated_cmr_rank": estimated_cmr,
                "overall_proxy_score": diag.get("overall_score"),
                "source": "cibil_pdf",
            },
        )
    except Exception as e:
        print(f"[Warning] Could not persist sample CIBIL report to DB: {e}")

    return {
        "success": True,
        "message": f"Successfully loaded and parsed sample scenario for {meta.get('company_name', data['company_name'])}.",
        "filename": data["filename"],
        "extracted_report_metadata": meta,
        "diagnostic": diag,
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
