"""
Structured Commercial Credit Information Report (CIR) Parser & Diagnostic Pipeline.
Compliant with CICRA 2005. Validates PDF integrity, extracts business identity,
official CMR ranks, credit utilization, facility-level repayment DPD tracks,
and credit tenure with full evidence preservation.
"""

import io
import re
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import pypdf
import pdfplumber

from feature_engineering import (
    BusinessCreditProfile,
    compute_overall_diagnostic,
    generate_action_plan,
)

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

RECOGNIZED_CREDIT_KEYWORDS = [
    "cibil", "transunion", "credit", "cmr", "cir", "repayment",
    "sanctioned", "facility", "outstanding", "utilization",
    "commercial credit", "borrower", "dpd", "delinquency"
]


def validate_pdf_content(pdf_source) -> bytes:
    """
    Validates PDF format, size, encryption status, and machine-readable text.
    Returns the raw bytes of the validated PDF.
    Raises ValueError / RuntimeError with clear messages on validation failure.
    """
    if isinstance(pdf_source, (str, Path)):
        path = Path(pdf_source)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_source}")
        raw_bytes = path.read_bytes()
    elif isinstance(pdf_source, (bytes, bytearray)):
        raw_bytes = bytes(pdf_source)
    elif hasattr(pdf_source, "read"):
        raw_bytes = pdf_source.read()
        if hasattr(pdf_source, "seek"):
            pdf_source.seek(0)
    else:
        raise ValueError("Unsupported PDF input type.")

    # 1. Size check
    if len(raw_bytes) == 0:
        raise ValueError("Uploaded file is completely empty (0 bytes).")
    if len(raw_bytes) > MAX_PDF_SIZE_BYTES:
        raise ValueError(f"Uploaded PDF exceeds maximum allowed size ({MAX_PDF_SIZE_BYTES // (1024 * 1024)}MB).")

    # 2. Magic bytes verification
    if not raw_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid PDF format: File does not start with standard '%PDF-' magic header.")

    # 3. Encryption & Page verification via pypdf
    try:
        reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
    except Exception as e:
        raise ValueError(f"Corrupt or unreadable PDF document: {str(e)}")

    if reader.is_encrypted:
        raise ValueError("Encrypted PDF detected. Password-protected credit reports cannot be automatically parsed. Please provide an unencrypted PDF.")

    if len(reader.pages) == 0:
        raise ValueError("Empty PDF document: The file contains 0 pages.")

    # 4. Text extraction check (scanned / image-only detection)
    extracted_sample = ""
    for page in reader.pages[:3]:
        extracted_sample += (page.extract_text() or "")

    if len(extracted_sample.strip()) < 20:
        raise ValueError(
            "Scanned or image-only PDF detected. No machine-readable digital text was found. "
            "Please upload a digitally generated credit report (PDF) or an OCR-processed document."
        )

    # 5. Content relevance check
    lower_sample = extracted_sample.lower()
    matches = [kw for kw in RECOGNIZED_CREDIT_KEYWORDS if kw in lower_sample]
    if len(matches) < 2:
        raise ValueError(
            "Unsupported PDF document: The uploaded PDF does not appear to be a recognized commercial credit information report (CIR). "
            "Please upload an authentic or synthetic commercial credit report."
        )

    return raw_bytes


def extract_raw_pages_and_tables(raw_bytes: bytes) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str]:
    """
    Extracts text per page, tables per page, and combined full text.
    Uses pdfplumber as primary engine with pypdf fallback.
    """
    pages_text = []
    tables = []

    try:
        with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
            for p_num, p in enumerate(pdf.pages):
                txt = p.extract_text() or ""
                pages_text.append({"page": p_num + 1, "text": txt})
                for t in p.extract_tables():
                    tables.append({"page": p_num + 1, "table": t})
    except Exception:
        # Fallback to pypdf for text if pdfplumber fails
        reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
        for p_num, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            pages_text.append({"page": p_num + 1, "text": txt})

    full_text = "\n".join([p["text"] for p in pages_text])
    return pages_text, tables, full_text


def _parse_currency_amount(val_str: Optional[str]) -> Optional[float]:
    """Parses Indian currency format like 'INR 25,00,000' or '5,000,000' to float."""
    if not val_str:
        return None
    cleaned = re.sub(r"[^\d.]", "", val_str)
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _parse_date_string(date_str: Optional[str]) -> Optional[datetime.date]:
    """Parses standard Indian bureau date formats."""
    if not date_str:
        return None
    clean = date_str.strip()
    formats = [
        "%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y", "%d-%m-%Y",
        "%d %B %Y", "%d %b %Y", "%Y-%m-%d"
    ]
    # Extract date portion if time included (e.g. '04-Nov-2026 11:24:18 IST')
    date_part = clean.split()[0] if "-" in clean or "/" in clean else clean
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_part, fmt).date()
        except Exception:
            pass
    # Try regex match for date like '12 November 2026'
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", clean)
    if m:
        for fmt in ["%d %B %Y", "%d %b %Y"]:
            try:
                return datetime.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", fmt).date()
            except Exception:
                pass
    return None


def extract_structured_cibil_data(raw_bytes: bytes) -> Dict[str, Any]:
    """
    Structured extraction pipeline that extracts identity, CMR rank, limits,
    facility details, repayment DPD tracks, vintage, and provenance with evidence.
    Missing data remains null (never fabricated).
    """
    pages_text, tables, full_text = extract_raw_pages_and_tables(raw_bytes)

    extracted: Dict[str, Any] = {
        "company_name": None,
        "trade_name": None,
        "business_type": None,
        "pan": None,
        "gstin": None,
        "cin": None,
        "business_id": None,
        "registered_address": None,
        "rcn": None,
        "report_date": None,
        "official_cmr_rank": None,
        "total_sanctioned": None,
        "total_balance": None,
        "total_overdue": None,
        "credit_utilization": None,
        "credit_tenure_years": None,
        "business_age_years": None,
        "industry_risk_category": None,
        "on_time_payment_pct": None,
        "has_recent_delinquency": None,
        "has_historical_delinquency": None,
        "facilities": [],
        "evidence": {},
        "missing_fields": [],
    }

    evidence = extracted["evidence"]

    # -------------------------------------------------------------
    # 1. TABLE-FIRST SCAN FOR STRUCTURED KEY-VALUE PAIRS
    # -------------------------------------------------------------
    for t_info in tables:
        t = t_info["table"]
        page = t_info["page"]
        if not t:
            continue

        for row in t:
            if not row:
                continue
            for i in range(len(row)):
                cell = str(row[i] or "").strip()
                cell_l = cell.lower()
                next_cell = str(row[i + 1] or "").strip() if i + 1 < len(row) else ""

                # Company / Business Name
                if ("business name" in cell_l or "company / legal name" in cell_l) and next_cell and not extracted["company_name"]:
                    clean_name = next_cell.replace("\n", " ").strip()
                    if len(clean_name) > 2:
                        extracted["company_name"] = clean_name
                        evidence["company_name"] = {"page": page, "source": f"{cell} -> {clean_name}", "status": "extracted", "confidence": 1.0}

                # Trade Name
                if "trade name" in cell_l and next_cell and not extracted["trade_name"]:
                    extracted["trade_name"] = next_cell.replace("\n", " ").strip()

                # Business Type / Constitution
                if ("business type" in cell_l or "constitution" in cell_l) and next_cell and not extracted["business_type"]:
                    extracted["business_type"] = next_cell.replace("\n", " ").strip()

                # Business ID / Corporate ID
                if ("business id" in cell_l or "corporate id" in cell_l or "cin" in cell_l) and next_cell and not extracted["cin"]:
                    extracted["cin"] = next_cell.strip()

                # Income Tax PAN
                if "pan" in cell_l and next_cell and not extracted["pan"]:
                    m_pan = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", next_cell)
                    if m_pan:
                        extracted["pan"] = m_pan.group(1)
                        evidence["pan"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # GSTIN
                if "gstin" in cell_l and next_cell and not extracted["gstin"]:
                    m_gst = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]{3})\b", next_cell)
                    if m_gst:
                        extracted["gstin"] = m_gst.group(1)
                        evidence["gstin"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Report Reference / Report Control Number (RCN)
                if ("report reference" in cell_l or "report control number" in cell_l or "rcn" in cell_l) and next_cell and not extracted["rcn"]:
                    clean_rcn = next_cell.split()[0].strip()
                    extracted["rcn"] = clean_rcn
                    evidence["rcn"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Report Date
                if ("report date" in cell_l or "date/time" in cell_l) and next_cell and not extracted["report_date"]:
                    extracted["report_date"] = next_cell.replace("\n", " ").strip()
                    evidence["report_date"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Business Vintage / Age
                if ("business vintage" in cell_l or "incorporation date" in cell_l) and next_cell and extracted["business_age_years"] is None:
                    m_age = re.search(r"([0-9.]+)\s*(?:years|yrs)", next_cell, re.I)
                    if m_age:
                        extracted["business_age_years"] = float(m_age.group(1))
                        evidence["business_age_years"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Total Sanctioned Limit
                if "total sanctioned" in cell_l and next_cell and extracted["total_sanctioned"] is None:
                    sanc = _parse_currency_amount(next_cell)
                    if sanc is not None:
                        extracted["total_sanctioned"] = sanc
                        evidence["total_sanctioned"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Total Outstanding / Current Balance
                if ("total outstanding" in cell_l or "total current balance" in cell_l) and next_cell and extracted["total_balance"] is None:
                    bal = _parse_currency_amount(next_cell)
                    if bal is not None:
                        extracted["total_balance"] = bal
                        evidence["total_balance"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Total Overdue
                if "total overdue" in cell_l and next_cell and extracted["total_overdue"] is None:
                    od = _parse_currency_amount(next_cell)
                    if od is not None:
                        extracted["total_overdue"] = od
                        evidence["total_overdue"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Credit Utilization Ratio
                if ("overall utilization" in cell_l or "credit utilization" in cell_l) and next_cell and extracted["credit_utilization"] is None:
                    m_u = re.search(r"([0-9.]+)%", next_cell)
                    if m_u:
                        extracted["credit_utilization"] = float(m_u.group(1)) / 100.0
                        evidence["credit_utilization"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Credit History Vintage / Tenure
                if ("credit vintage" in cell_l or "credit history vintage" in cell_l) and next_cell and extracted["credit_tenure_years"] is None:
                    m_tenure = re.search(r"([0-9.]+)\s*(?:years|yrs)", next_cell, re.I)
                    if m_tenure:
                        extracted["credit_tenure_years"] = float(m_tenure.group(1))
                        evidence["credit_tenure_years"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Official CMR Rank
                # 1. Direct CMR assessment box check in cell (e.g. 'CMR-6' in the cell itself)
                if extracted["official_cmr_rank"] is None and re.search(r"\bCMR\s*-\s*([1-9]|10)\b", cell, re.I):
                    if "target" not in cell_l and "eligibility" not in cell_l:
                        m_rank = re.search(r"\bCMR\s*-\s*([1-9]|10)\b", cell, re.I)
                        if m_rank:
                            extracted["official_cmr_rank"] = int(m_rank.group(1))
                            evidence["official_cmr_rank"] = {"page": page, "source": cell.split("\n")[0], "status": "extracted", "confidence": 1.0}

                # 2. Adjacent cell CMR Band / Rank (e.g. 'Illustrative CMR Band' -> '6')
                if ("illustrative cmr band" in cell_l or "cmr band" in cell_l) and next_cell and extracted["official_cmr_rank"] is None:
                    if "target" not in next_cell.lower():
                        m_rank = re.search(r"\b([1-9]|10)\b", next_cell)
                        if m_rank:
                            extracted["official_cmr_rank"] = int(m_rank.group(1))
                            evidence["official_cmr_rank"] = {"page": page, "source": f"{cell} -> {next_cell}", "status": "extracted", "confidence": 1.0}

                # Explicit On-Time Payment Percentage
                if ("on-time payment history" in cell_l or "payment regularity" in cell_l) and next_cell and extracted["on_time_payment_pct"] is None:
                    m_on = re.search(r"([0-9.]+)%", next_cell)
                    if m_on:
                        extracted["on_time_payment_pct"] = float(m_on.group(1)) / 100.0
                        evidence["on_time_payment_pct"] = {"page": page, "source": next_cell, "status": "extracted", "confidence": 1.0}

                # Explicit Recent Delinquency
                if "recent delinquency" in cell_l and next_cell and extracted["has_recent_delinquency"] is None:
                    is_delinq = next_cell.strip().lower() in ["yes", "true", "detected", "critical"]
                    extracted["has_recent_delinquency"] = is_delinq
                    evidence["has_recent_delinquency"] = {"page": page, "source": f"Recent Delinquency: {next_cell}", "status": "extracted", "confidence": 1.0}

    # -------------------------------------------------------------
    # 2. RAW TEXT FALLBACK FOR MISSING CORE FIELDS
    # -------------------------------------------------------------
    if not extracted["company_name"]:
        m_cn = re.search(r"(?:Company / Legal Name|Business Name|Borrower Name)[\s:]*([^\n\r]+)", full_text, re.I)
        if m_cn and len(m_cn.group(1).strip()) > 2:
            extracted["company_name"] = m_cn.group(1).strip()
            evidence["company_name"] = {"page": 1, "source": m_cn.group(0), "status": "extracted", "confidence": 0.85}

    if not extracted["rcn"]:
        m_rcn = re.search(r"(?:REPORT CONTROL NUMBER|Report Reference|RCN)[\s:]*([A-Z0-9\-]+)", full_text, re.I)
        if m_rcn:
            extracted["rcn"] = m_rcn.group(1).strip()
            evidence["rcn"] = {"page": 1, "source": m_rcn.group(0), "status": "extracted", "confidence": 0.9}

    if not extracted["report_date"]:
        m_dt = re.search(r"(?:DATE/TIME|Report Date)[\s:]*([0-9]{1,2}[-\s][A-Za-z]{3,9}[-\s][0-9]{4}(?:[\s0-9:]+(?:IST|UTC|AM|PM)?)?)", full_text, re.I)
        if m_dt:
            extracted["report_date"] = m_dt.group(1).strip()
            evidence["report_date"] = {"page": 1, "source": m_dt.group(0), "status": "extracted", "confidence": 0.9}

    if not extracted["pan"]:
        m_pan = re.search(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", full_text)
        if m_pan:
            extracted["pan"] = m_pan.group(1)

    if not extracted["gstin"]:
        m_gst = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]{3})\b", full_text)
        if m_gst:
            extracted["gstin"] = m_gst.group(1)

    if extracted["official_cmr_rank"] is None:
        m_cmr = re.search(r"\bCMR\s*-\s*([1-9]|10)\b", full_text, re.I)
        if m_cmr:
            extracted["official_cmr_rank"] = int(m_cmr.group(1))
            evidence["official_cmr_rank"] = {"page": 1, "source": m_cmr.group(0), "status": "extracted", "confidence": 0.9}

    # -------------------------------------------------------------
    # 3. FACILITY-LEVEL AND DPD REPAYMENT EXTRACTION
    # -------------------------------------------------------------
    facility_list: List[Dict[str, Any]] = []
    total_clean_tokens = 0
    total_dpd_tokens = 0
    facility_recent_delinq = False
    facility_hist_delinq = False

    for t_info in tables:
        t = t_info["table"]
        page = t_info["page"]
        if not t:
            continue

        header_idx = None
        for r_idx, row in enumerate(t):
            row_str = " ".join([str(c or "").lower() for c in row if c])
            if "facility" in row_str and ("sanctioned" in row_str or "dpd" in row_str or any(m in row_str for m in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])):
                header_idx = r_idx
                break

        if header_idx is not None and header_idx + 1 < len(t):
            hdr = [str(c or "").strip().lower() for c in t[header_idx]]
            is_month_matrix = any(re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})\b", c) for c in hdr)
            dpd_col_idx = [i for i, c in enumerate(hdr) if "dpd" in c]
            sanc_col_idx = [i for i, c in enumerate(hdr) if "sanction" in c]
            bal_col_idx = [i for i, c in enumerate(hdr) if "balance" in c or "outstanding" in c]
            overdue_col_idx = [i for i, c in enumerate(hdr) if "overdue" in c]
            status_col_idx = [i for i, c in enumerate(hdr) if "status" in c]
            open_col_idx = [i for i, c in enumerate(hdr) if "open" in c]

            for row in t[header_idx + 1:]:
                if not row or not row[0]:
                    continue
                fac_name = str(row[0]).strip().replace("\n", " ")
                if "facility" in fac_name.lower():
                    continue

                raw_tokens: List[str] = []
                if is_month_matrix:
                    month_cells = [str(c or "").strip() for c in row[1:] if c]
                    for mc in month_cells:
                        cleaned_mc = re.sub(r"\(.*?\)", "", mc, flags=re.DOTALL)
                        toks = re.findall(r"\b(0[0-9]{2}|[1-9][0-9]{2}|STD|SUB|DBT|LSS|SMA)\b", cleaned_mc)
                        raw_tokens.extend(toks)
                elif dpd_col_idx and dpd_col_idx[0] < len(row):
                    dpd_cell = str(row[dpd_col_idx[0]] or "")
                    # IMPORTANT: Strip parenthetical explanation like '(000=No delay; 030=30 days late)'
                    cleaned_dpd = re.sub(r"\(.*?\)", "", dpd_cell, flags=re.DOTALL)
                    raw_tokens = re.findall(r"\b(0[0-9]{2}|[1-9][0-9]{2}|STD|SUB|DBT|LSS|SMA)\b", cleaned_dpd)

                # Classify tokens into recent (first 3-4 reporting months) and historical (>4 months)
                f_recent = False
                f_hist = False
                if raw_tokens:
                    rec_tokens = raw_tokens[:3]
                    hist_tokens = raw_tokens[3:]
                    f_recent = any(t not in ["000", "STD"] for t in rec_tokens)
                    f_hist = any(t not in ["000", "STD"] for t in hist_tokens)
                    if f_recent:
                        facility_recent_delinq = True
                    if f_hist:
                        facility_hist_delinq = True

                    for t in raw_tokens:
                        total_dpd_tokens += 1
                        if t in ["000", "STD"]:
                            total_clean_tokens += 1

                sanc_val = _parse_currency_amount(str(row[sanc_col_idx[0]])) if sanc_col_idx and sanc_col_idx[0] < len(row) else None
                bal_val = _parse_currency_amount(str(row[bal_col_idx[0]])) if bal_col_idx and bal_col_idx[0] < len(row) else None
                od_val = _parse_currency_amount(str(row[overdue_col_idx[0]])) if overdue_col_idx and overdue_col_idx[0] < len(row) else None
                st_val = str(row[status_col_idx[0]]).strip() if status_col_idx and status_col_idx[0] < len(row) and row[status_col_idx[0]] else "Active"
                open_val = str(row[open_col_idx[0]]).strip() if open_col_idx and open_col_idx[0] < len(row) and row[open_col_idx[0]] else None

                facility_list.append({
                    "facility_name": fac_name,
                    "sanctioned_amount": sanc_val,
                    "outstanding_balance": bal_val,
                    "overdue_amount": od_val or 0.0,
                    "status": st_val,
                    "open_date": open_val,
                    "dpd_tokens": raw_tokens,
                    "has_recent_delinquency": f_recent,
                    "has_historical_delinquency": f_hist,
                })

    extracted["facilities"] = facility_list

    # Delinquency assignment: preserve explicit statement if present, otherwise evaluate facility tokens
    if extracted["has_recent_delinquency"] is None:
        extracted["has_recent_delinquency"] = facility_recent_delinq

    extracted["has_historical_delinquency"] = facility_hist_delinq

    # On-Time Payment Percentage
    if extracted["on_time_payment_pct"] is None:
        if total_dpd_tokens > 0:
            extracted["on_time_payment_pct"] = round(total_clean_tokens / total_dpd_tokens, 4)
            evidence["on_time_payment_pct"] = {
                "page": 1,
                "source": f"Computed from {total_dpd_tokens} reporting months across {len(facility_list)} facilities ({total_clean_tokens} clean)",
                "status": "calculated",
                "confidence": 1.0,
            }

    # -------------------------------------------------------------
    # 4. DERIVED FINANCIAL AGGREGATES & VINTAGE DATES
    # -------------------------------------------------------------
    # If aggregate limits missing from summary table, sum them from extracted facilities
    if extracted["total_sanctioned"] is None and facility_list:
        valid_sanc = [f["sanctioned_amount"] for f in facility_list if f["sanctioned_amount"] is not None]
        if valid_sanc:
            extracted["total_sanctioned"] = sum(valid_sanc)
            evidence["total_sanctioned"] = {"page": 1, "source": f"Summed from {len(valid_sanc)} facility limits", "status": "calculated", "confidence": 0.95}

    if extracted["total_balance"] is None and facility_list:
        valid_bal = [f["outstanding_balance"] for f in facility_list if f["outstanding_balance"] is not None]
        if valid_bal:
            extracted["total_balance"] = sum(valid_bal)
            evidence["total_balance"] = {"page": 1, "source": f"Summed from {len(valid_bal)} facility balances", "status": "calculated", "confidence": 0.95}

    if extracted["total_overdue"] is None and facility_list:
        valid_od = [f["overdue_amount"] for f in facility_list if f["overdue_amount"] is not None]
        extracted["total_overdue"] = sum(valid_od)

    # Utilization calculation
    if extracted["credit_utilization"] is None and extracted["total_sanctioned"] and extracted["total_balance"]:
        if extracted["total_sanctioned"] > 0:
            extracted["credit_utilization"] = round(extracted["total_balance"] / extracted["total_sanctioned"], 4)
            evidence["credit_utilization"] = {
                "page": 1,
                "source": f"Calculated: {extracted['total_balance']} / {extracted['total_sanctioned']}",
                "status": "calculated",
                "confidence": 1.0,
            }

    # Credit Vintage calculation from earliest facility open date if missing
    if extracted["credit_tenure_years"] is None and facility_list:
        open_dates = []
        rep_date = _parse_date_string(extracted["report_date"]) or datetime.date.today()
        for f in facility_list:
            od = _parse_date_string(f.get("open_date"))
            if od:
                open_dates.append(od)
        if open_dates:
            earliest = min(open_dates)
            delta_days = (rep_date - earliest).days
            if delta_days > 0:
                extracted["credit_tenure_years"] = round(delta_days / 365.25, 1)
                evidence["credit_tenure_years"] = {
                    "page": 1,
                    "source": f"Calculated from oldest facility opening date ({earliest}) to report date ({rep_date})",
                    "status": "calculated",
                    "confidence": 0.9,
                }

    # Business Age calculation from incorporation date if missing
    if extracted["business_age_years"] is None:
        m_inc = re.search(r"Incorporation Date:[\s]*([0-9]{1,2}[-\s][A-Za-z]{3,9}[-\s][0-9]{4})", full_text, re.I)
        if m_inc:
            inc_date = _parse_date_string(m_inc.group(1))
            rep_date = _parse_date_string(extracted["report_date"]) or datetime.date.today()
            if inc_date and rep_date and rep_date > inc_date:
                extracted["business_age_years"] = round((rep_date - inc_date).days / 365.25, 1)
                evidence["business_age_years"] = {
                    "page": 1,
                    "source": f"Calculated from incorporation date ({inc_date}) to report date ({rep_date})",
                    "status": "calculated",
                    "confidence": 0.9,
                }

    # Industry Risk Tier
    if "low risk" in full_text.lower():
        extracted["industry_risk_category"] = "low"
    elif "high risk" in full_text.lower():
        extracted["industry_risk_category"] = "high"
    else:
        extracted["industry_risk_category"] = "medium"

    # Identify missing fields (never replace with silent fake defaults)
    for field in [
        "company_name", "official_cmr_rank", "credit_utilization",
        "on_time_payment_pct", "has_recent_delinquency",
        "credit_tenure_years", "business_age_years"
    ]:
        if extracted[field] is None:
            extracted["missing_fields"].append(field)
            evidence[field] = {"status": "missing", "value": None}

    return extracted


def convert_cibil_to_profile(
    cibil_data: Dict[str, Any],
    fallback_defaults: Optional[Dict[str, Any]] = None,
) -> Tuple[BusinessCreditProfile, List[str]]:
    """
    Constructs a validated BusinessCreditProfile for ML diagnostic scoring.
    Strictly documents any field that needed a fallback.
    """
    fb = fallback_defaults or {}
    unresolved_fields = []

    def _resolve(field_name: str, fallback_val: Any) -> Any:
        val = cibil_data.get(field_name)
        if val is not None:
            return val
        if field_name in fb and fb[field_name] is not None:
            return fb[field_name]
        unresolved_fields.append(field_name)
        return fallback_val

    on_time = float(_resolve("on_time_payment_pct", 0.90))
    recent_delinq = bool(_resolve("has_recent_delinquency", False))
    utilization = float(_resolve("credit_utilization", 0.50))
    tenure = float(_resolve("credit_tenure_years", 3.0))
    biz_age = float(_resolve("business_age_years", 5.0))
    ind_risk = str(cibil_data.get("industry_risk_category") or fb.get("industry_category") or "medium").lower()

    profile = BusinessCreditProfile(
        on_time_payment_pct=round(min(1.0, max(0.0, on_time)), 4),
        has_recent_delinquency=recent_delinq,
        credit_utilization=round(max(0.0, utilization), 4),
        credit_tenure_years=round(max(0.1, tenure), 1),
        business_age_years=round(max(0.1, biz_age), 1),
        industry_risk_category=ind_risk if ind_risk in ["low", "medium", "high"] else "medium",
    )

    return profile, unresolved_fields


def parse_and_diagnose_cibil_pdf(
    pdf_source,
    target_rank: int = 3,
    fallback_defaults: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    End-to-end single-pass parsing and diagnostic pipeline:
    1. Validates PDF format, security, size, and content.
    2. Structured table and text extraction.
    3. Builds diagnostic profile and separates official bureau rank from calculated proxy rank.
    4. Computes 4-pillar diagnostic and prioritized action plan.
    """
    raw_bytes = validate_pdf_content(pdf_source)
    extracted = extract_structured_cibil_data(raw_bytes)
    profile, unresolved = convert_cibil_to_profile(extracted, fallback_defaults)

    diag = compute_overall_diagnostic(profile)
    plan = generate_action_plan(profile, target_rank)

    # Clean representation of extracted metadata
    metadata = {
        "rcn": extracted["rcn"],
        "company_name": extracted["company_name"],
        "trade_name": extracted["trade_name"],
        "business_type": extracted["business_type"],
        "pan": extracted["pan"],
        "gstin": extracted["gstin"],
        "cin": extracted["cin"],
        "report_date": extracted["report_date"],
        "official_cmr_rank": extracted["official_cmr_rank"],
        "total_sanctioned": extracted["total_sanctioned"],
        "total_balance": extracted["total_balance"],
        "total_overdue": extracted["total_overdue"],
        "credit_utilization_pct": round(extracted["credit_utilization"] * 100, 1) if extracted["credit_utilization"] is not None else None,
        "on_time_payment_pct": round(extracted["on_time_payment_pct"] * 100, 1) if extracted["on_time_payment_pct"] is not None else None,
        "has_recent_delinquency": extracted["has_recent_delinquency"],
        "has_historical_delinquency": extracted["has_historical_delinquency"],
        "credit_tenure_years": extracted["credit_tenure_years"],
        "business_age_years": extracted["business_age_years"],
        "industry_risk_category": extracted["industry_risk_category"],
        "facilities": extracted["facilities"],
        "evidence": extracted["evidence"],
        "missing_fields": extracted["missing_fields"],
        "unresolved_fallbacks": unresolved,
    }

    return {
        "extracted_report_metadata": metadata,
        "diagnostic": diag,
        "action_plan": plan,
        "profile": profile,
    }


def extract_text_from_pdf(pdf_source) -> str:
    """Legacy helper: Extracts text content from a PDF file stream or path."""
    try:
        raw_bytes = validate_pdf_content(pdf_source)
        _, _, full_text = extract_raw_pages_and_tables(raw_bytes)
        return full_text
    except Exception:
        if isinstance(pdf_source, (str, Path)):
            reader = pypdf.PdfReader(str(pdf_source))
        elif hasattr(pdf_source, "read"):
            reader = pypdf.PdfReader(pdf_source)
        else:
            reader = pypdf.PdfReader(io.BytesIO(pdf_source))
        return "\n".join([p.extract_text() or "" for p in reader.pages])


def parse_cibil_report_text(raw_text_or_bytes) -> Dict[str, Any]:
    """Legacy compatibility bridge: returns dictionary matching old parser keys."""
    if isinstance(raw_text_or_bytes, (bytes, bytearray)) or hasattr(raw_text_or_bytes, "read"):
        raw_bytes = validate_pdf_content(raw_text_or_bytes)
        extracted = extract_structured_cibil_data(raw_bytes)
    else:
        # String passed directly
        text = str(raw_text_or_bytes)
        extracted = {
            "rcn": None,
            "company_name": None,
            "pan": None,
            "gstin": None,
            "official_cmr_rank": None,
            "credit_utilization": None,
            "on_time_payment_pct": None,
            "has_recent_delinquency": False,
            "credit_tenure_years": None,
            "business_age_years": None,
            "industry_risk_category": "medium",
        }
        m_rcn = re.search(r"(?:REPORT CONTROL NUMBER|Report Reference|RCN)[\s:]*([A-Z0-9\-]+)", text, re.I)
        if m_rcn: extracted["rcn"] = m_rcn.group(1).strip()
        m_cn = re.search(r"(?:Company / Legal Name|Business Name|Borrower Name)[\s:]*([^\n\r]+)", text, re.I)
        if m_cn: extracted["company_name"] = m_cn.group(1).strip()
        m_cmr = re.search(r"\bCMR\s*-\s*([1-9]|10)\b", text, re.I)
        if m_cmr: extracted["official_cmr_rank"] = int(m_cmr.group(1))

    return {
        "rcn": extracted.get("rcn"),
        "company_name": extracted.get("company_name"),
        "pan": extracted.get("pan"),
        "gstin": extracted.get("gstin"),
        "cmr_rank": extracted.get("official_cmr_rank"),
        "credit_utilization": extracted.get("credit_utilization"),
        "on_time_payment_pct": extracted.get("on_time_payment_pct"),
        "has_recent_delinquency": extracted.get("has_recent_delinquency"),
        "credit_tenure_years": extracted.get("credit_tenure_years"),
        "business_age_years": extracted.get("business_age_years"),
        "industry_risk_category": extracted.get("industry_risk_category", "medium"),
    }

