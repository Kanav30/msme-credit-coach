"""
Parser for TransUnion CIBIL Commercial Credit Information Reports (CIR / CMR).
Extracts company identification, official CMR rank, credit utilization,
repayment conduct (DPD history), and credit vintage directly from uploaded bureau PDFs.
"""

import re
from typing import Dict, Any, Optional
import pypdf
from feature_engineering import (
    BusinessCreditProfile,
    compute_overall_diagnostic,
    generate_action_plan,
)


def extract_text_from_pdf(pdf_file_path_or_bytes) -> str:
    """Extracts raw text content from a PDF file stream or path."""
    reader = pypdf.PdfReader(pdf_file_path_or_bytes)
    text_pages = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            text_pages.append(txt)
    return "\n".join(text_pages)


def parse_cibil_report_text(raw_text: str) -> Dict[str, Any]:
    """
    Parses key commercial credit metrics from raw CIBIL CIR text using
    structured pattern matching and domain heuristics.
    """
    data = {}

    # 1. Report Control Number (RCN)
    rcn_match = re.search(r"REPORT CONTROL NUMBER:\s*([A-Z0-9\-]+)", raw_text, re.IGNORECASE)
    data["rcn"] = rcn_match.group(1).strip() if rcn_match else "TU-CIR-UNKNOWN"

    # 2. Company / Legal Name
    name_match = re.search(r"Company / Legal Name:\s*([^\n\r]+)", raw_text, re.IGNORECASE)
    if name_match:
        data["company_name"] = name_match.group(1).strip()
    else:
        # Fallback check
        name_fallback = re.search(r"TRANSUNION CIBIL.*?\n([A-Z\s]{4,60}(?:LIMITED|LLP|PVT|PRIVATE))", raw_text)
        data["company_name"] = name_fallback.group(1).strip() if name_fallback else "Commercial MSME Entity"

    # 3. PAN & GSTIN
    pan_match = re.search(r"([A-Z]{5}[0-9]{4}[A-Z])", raw_text)
    data["pan"] = pan_match.group(1) if pan_match else None

    gstin_match = re.search(r"([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]{3})", raw_text)
    data["gstin"] = gstin_match.group(1) if gstin_match else None

    # 4. CIBIL MSME Rank (CMR 1 to 10)
    cmr_match = re.search(r"CMR\s*-\s*([1-9]|10)", raw_text, re.IGNORECASE)
    if cmr_match:
        data["cmr_rank"] = int(cmr_match.group(1))
    else:
        rank_match2 = re.search(r"Rank:\s*([1-9]|10)", raw_text, re.IGNORECASE)
        data["cmr_rank"] = int(rank_match2.group(1)) if rank_match2 else 5

    # 5. Credit Utilization Ratio
    util_match = re.search(r"Credit Utilization Ratio:\s*([0-9.]+)%", raw_text, re.IGNORECASE)
    if util_match:
        data["credit_utilization"] = float(util_match.group(1)) / 100.0
    else:
        # Fallback: Sanctioned vs Balance
        sanc_match = re.search(r"Total Sanctioned Limit:\s*INR\s*([0-9,]+)", raw_text, re.IGNORECASE)
        bal_match = re.search(r"Total Current Balance:\s*INR\s*([0-9,]+)", raw_text, re.IGNORECASE)
        if sanc_match and bal_match:
            sanc = float(sanc_match.group(1).replace(",", ""))
            bal = float(bal_match.group(1).replace(",", ""))
            data["credit_utilization"] = min(1.0, max(0.0, bal / sanc)) if sanc > 0 else 0.50
        else:
            data["credit_utilization"] = 0.55

    # 6. DPD Track & Recent Delinquency
    # Search for DPD tokens like '000', '030', '060', '090', 'SUB', 'DBT'
    dpd_blocks = re.findall(r"(?:0[0-9]{2}|[1-9][0-9]{2}|SUB|DBT|STD)(?:\s+(?:0[0-9]{2}|[1-9][0-9]{2}|SUB|DBT|STD)){3,}", raw_text)
    has_delinquency = False
    clean_count = 0
    total_months = 0

    if dpd_blocks:
        for block in dpd_blocks:
            tokens = block.strip().split()
            # Most recent 3 months are typically the first tokens
            recent_tokens = tokens[:3]
            for tok in recent_tokens:
                if tok not in ["000", "STD"]:
                    has_delinquency = True
            for tok in tokens:
                total_months += 1
                if tok in ["000", "STD"]:
                    clean_count += 1

    if "Recent Delay" in raw_text or "030" in raw_text:
        has_delinquency = True

    data["has_recent_delinquency"] = has_delinquency
    data["on_time_payment_pct"] = (clean_count / total_months) if total_months > 0 else (0.80 if has_delinquency else 0.98)

    # 7. Credit History Vintage / Tenure (Years)
    tenure_match = re.search(r"Credit History Vintage:\s*([0-9.]+)\s*Years", raw_text, re.IGNORECASE)
    if tenure_match:
        data["credit_tenure_years"] = float(tenure_match.group(1))
    else:
        data["credit_tenure_years"] = 3.5

    # 8. Business Age (Years)
    age_match = re.search(r"Incorporation Date:.*?\(([0-9.]+)\s*Yrs\)", raw_text, re.IGNORECASE)
    if age_match:
        data["business_age_years"] = float(age_match.group(1))
    else:
        data["business_age_years"] = 5.0

    # 9. Industry Risk Level
    if "low risk" in raw_text.lower():
        data["industry_risk_category"] = "low"
    elif "high risk" in raw_text.lower():
        data["industry_risk_category"] = "high"
    else:
        data["industry_risk_category"] = "medium"

    return data


def convert_cibil_to_profile(cibil_data: Dict[str, Any]) -> BusinessCreditProfile:
    """Instantiates a BusinessCreditProfile from parsed CIBIL report data."""
    return BusinessCreditProfile(
        on_time_payment_pct=round(cibil_data.get("on_time_payment_pct", 0.90), 2),
        has_recent_delinquency=bool(cibil_data.get("has_recent_delinquency", False)),
        credit_utilization=round(cibil_data.get("credit_utilization", 0.50), 3),
        credit_tenure_years=float(cibil_data.get("credit_tenure_years", 3.0)),
        business_age_years=float(cibil_data.get("business_age_years", 5.0)),
        industry_risk_category=cibil_data.get("industry_risk_category", "medium"),
    )


def parse_and_diagnose_cibil_pdf(pdf_file_path_or_bytes, target_rank: int = 3) -> Dict[str, Any]:
    """End-to-end pipeline: extracts PDF, parses CIBIL metrics, runs diagnostic & action plan."""
    raw_text = extract_text_from_pdf(pdf_file_path_or_bytes)
    parsed = parse_cibil_report_text(raw_text)
    profile = convert_cibil_to_profile(parsed)
    diag = compute_overall_diagnostic(profile)
    plan = generate_action_plan(profile, target_rank)

    return {
        "extracted_report_metadata": {
            "rcn": parsed["rcn"],
            "company_name": parsed["company_name"],
            "pan": parsed["pan"],
            "gstin": parsed["gstin"],
            "official_cmr_rank": parsed["cmr_rank"],
            "credit_utilization_pct": round(parsed["credit_utilization"] * 100, 1),
            "on_time_payment_pct": round(parsed["on_time_payment_pct"] * 100, 1),
            "has_recent_delinquency": parsed["has_recent_delinquency"],
            "credit_tenure_years": parsed["credit_tenure_years"],
            "business_age_years": parsed["business_age_years"],
            "industry_risk_category": parsed["industry_risk_category"],
        },
        "diagnostic": diag,
        "action_plan": plan,
    }
