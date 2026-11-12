"""
Official TransUnion CIBIL Commercial Credit Information Report (CIR) Generator.
Generates authentic, formatted PDF credit reports for realistic MSME archetypes.
"""

import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

OUTPUT_DIR = Path(__file__).parent.parent / "sample_reports"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 5 Realistic MSME Archetypes
ARCHETYPES_DATA = {
    "demo-owner-1": {
        "filename": "CIBIL_Report_Sharma_Precision_Engineering.pdf",
        "company_name": "SHARMA PRECISION ENGINEERING PRIVATE LIMITED",
        "trade_name": "Sharma Tools & Dies",
        "cin": "U28112PN2020PTC192841",
        "pan": "AABCS4819M",
        "gstin": "27AABCS4819M1ZV",
        "constitution": "Private Limited Company",
        "inc_date": "14-AUG-2020",
        "business_age_years": 6.0,
        "industry": "Precision Tooling & Auto Components (Medium Risk)",
        "address": "Plot No. 42, Sector 7, MIDC Industrial Area, Bhosari, Pune - 411026, Maharashtra",
        "rcn": "TU-CIR-20261104-984210",
        "report_date": "04-Nov-2026 11:24:18 IST",
        "cmr_rank": 6,
        "cmr_tier": "Moderate to High Risk Tier",
        "overall_score": 46.1,
        "target_rank": 3,
        "credit_tenure_years": 3.0,
        "credit_utilization": 0.78,
        "total_sanctioned": 5000000,
        "total_balance": 3900000,
        "total_overdue": 45000,
        "active_accounts": 2,
        "closed_accounts": 1,
        "has_recent_delinquency": True,
        "facilities": [
            {
                "type": "Working Capital / Cash Credit",
                "bank": "Bank of Baroda - Pune SME",
                "sanctioned": "35,00,000",
                "balance": "27,50,000",
                "open_date": "15-Sep-2023",
                "utilization": "78.5%",
                "status": "Active / Regular with Recent Delay",
                "dpd_string": "030 000 000 000 000 000 000 000 000 000 000 000",
            },
            {
                "type": "Term Loan (Machinery)",
                "bank": "HDFC Bank Limited",
                "sanctioned": "15,00,000",
                "balance": "11,50,000",
                "open_date": "10-Jan-2024",
                "utilization": "76.6%",
                "status": "Active / Standard",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
        ],
    },
    "patel-textiles": {
        "filename": "CIBIL_Report_Patel_Technical_Textiles.pdf",
        "company_name": "PATEL TECHNICAL TEXTILES PRIVATE LIMITED",
        "trade_name": "Patel Yarns & Fabrics",
        "cin": "U17111GJ2014PTC078912",
        "pan": "AAACP7192K",
        "gstin": "24AAACP7192K1Z8",
        "constitution": "Private Limited Company",
        "inc_date": "20-JUN-2014",
        "business_age_years": 12.0,
        "industry": "Technical Textiles & Industrial Fabrics (Low Risk)",
        "address": "Survey No. 118, GIDC Industrial Estate, Sachin, Surat - 394230, Gujarat",
        "rcn": "TU-CIR-20261102-419082",
        "report_date": "02-Nov-2026 09:15:42 IST",
        "cmr_rank": 2,
        "cmr_tier": "Prime Commercial Tier (Low Risk)",
        "overall_score": 89.3,
        "target_rank": 2,
        "credit_tenure_years": 8.0,
        "credit_utilization": 0.45,
        "total_sanctioned": 12000000,
        "total_balance": 5400000,
        "total_overdue": 0,
        "active_accounts": 3,
        "closed_accounts": 2,
        "has_recent_delinquency": False,
        "facilities": [
            {
                "type": "Cash Credit / Working Capital",
                "bank": "State Bank of India - Surat Commercial",
                "sanctioned": "80,00,000",
                "balance": "36,00,000",
                "open_date": "12-Mar-2018",
                "utilization": "45.0%",
                "status": "Active / Prime Standard",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
            {
                "type": "Equipment Term Loan",
                "bank": "ICICI Bank Limited",
                "sanctioned": "40,00,000",
                "balance": "18,00,000",
                "open_date": "15-Jul-2021",
                "utilization": "45.0%",
                "status": "Active / Standard",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
        ],
    },
    "gupta-crafts": {
        "filename": "CIBIL_Report_Gupta_Handicrafts_Export.pdf",
        "company_name": "GUPTA HANDICRAFTS EXPORTS LLP",
        "trade_name": "Jaipur Artisan Crafts",
        "cin": "AAU-8921",
        "pan": "ABBFG3412L",
        "gstin": "08ABBFG3412L1Z3",
        "constitution": "Limited Liability Partnership",
        "inc_date": "10-OCT-2025",
        "business_age_years": 1.0,
        "industry": "Handicrafts & Home Decor Export (Medium Risk)",
        "address": "G-14, Sitapura Industrial Area, Tonk Road, Jaipur - 302022, Rajasthan",
        "rcn": "TU-CIR-20261103-118942",
        "report_date": "03-Nov-2026 15:40:11 IST",
        "cmr_rank": 4,
        "cmr_tier": "Thin-File / New-to-Commercial Credit",
        "overall_score": 66.8,
        "target_rank": 3,
        "credit_tenure_years": 0.5,
        "credit_utilization": 0.20,
        "total_sanctioned": 1500000,
        "total_balance": 300000,
        "total_overdue": 0,
        "active_accounts": 1,
        "closed_accounts": 0,
        "has_recent_delinquency": False,
        "facilities": [
            {
                "type": "Export Packing Credit / Pre-Shipment",
                "bank": "Canara Bank - Jaipur SME Branch",
                "sanctioned": "15,00,000",
                "balance": "3,00,000",
                "open_date": "01-May-2026",
                "utilization": "20.0%",
                "status": "Active / Standard (Thin Track)",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
        ],
    },
    "verma-auto": {
        "filename": "CIBIL_Report_Verma_Auto_Components.pdf",
        "company_name": "VERMA AUTO COMPONENTS PRIVATE LIMITED",
        "trade_name": "Verma Steels & Forgings",
        "cin": "U34100HR2012PTC049102",
        "pan": "AABCV9102E",
        "gstin": "06AABCV9102E1Z1",
        "constitution": "Private Limited Company",
        "inc_date": "18-MAY-2012",
        "business_age_years": 14.0,
        "industry": "Auto Ancillary & Precision Castings (Low Risk)",
        "address": "Plot 89, Sector 3, IMT Manesar, Gurugram - 122050, Haryana",
        "rcn": "TU-CIR-20261104-551028",
        "report_date": "04-Nov-2026 16:05:00 IST",
        "cmr_rank": 3,
        "cmr_tier": "Monitored Tier (Near-Maxed Utilization)",
        "overall_score": 74.5,
        "target_rank": 2,
        "credit_tenure_years": 9.0,
        "credit_utilization": 0.95,
        "total_sanctioned": 8000000,
        "total_balance": 7600000,
        "total_overdue": 0,
        "active_accounts": 2,
        "closed_accounts": 3,
        "has_recent_delinquency": False,
        "facilities": [
            {
                "type": "Working Capital Overdraft Limit",
                "bank": "Punjab National Bank - Manesar SME",
                "sanctioned": "60,00,000",
                "balance": "57,20,000",
                "open_date": "10-Jun-2017",
                "utilization": "95.3%",
                "status": "Active / Maxed Out",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
            {
                "type": "Commercial Vehicle Loan",
                "bank": "HDFC Bank Limited",
                "sanctioned": "20,00,000",
                "balance": "18,80,000",
                "open_date": "14-Feb-2022",
                "utilization": "94.0%",
                "status": "Active / Regular",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
        ],
    },
    "reddy-pharma": {
        "filename": "CIBIL_Report_Reddy_Pharma_Chem.pdf",
        "company_name": "REDDY PHARMA CHEM PRIVATE LIMITED",
        "trade_name": "Reddy Formulations",
        "cin": "U24230TG2021PTC150912",
        "pan": "AABCR6019P",
        "gstin": "36AABCR6019P1ZW",
        "constitution": "Private Limited Company",
        "inc_date": "05-JAN-2021",
        "business_age_years": 5.0,
        "industry": "Bulk Drugs & API Intermediates (Medium Risk)",
        "address": "Plot 12, IDA Pashamylaram, Patancheru, Hyderabad - 502307, Telangana",
        "rcn": "TU-CIR-20261101-771920",
        "report_date": "01-Nov-2026 12:10:33 IST",
        "cmr_rank": 4,
        "cmr_tier": "Average / Mediocre Track",
        "overall_score": 69.1,
        "target_rank": 3,
        "credit_tenure_years": 4.0,
        "credit_utilization": 0.55,
        "total_sanctioned": 6000000,
        "total_balance": 3300000,
        "total_overdue": 0,
        "active_accounts": 2,
        "closed_accounts": 1,
        "has_recent_delinquency": False,
        "facilities": [
            {
                "type": "Cash Credit Limit",
                "bank": "Union Bank of India - Hyderabad Commercial",
                "sanctioned": "40,00,000",
                "balance": "22,00,000",
                "open_date": "20-Apr-2022",
                "utilization": "55.0%",
                "status": "Active / Regular",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
            {
                "type": "Solar Equipment Term Loan",
                "bank": "Axis Bank Limited",
                "sanctioned": "20,00,000",
                "balance": "11,00,000",
                "open_date": "18-Nov-2023",
                "utilization": "55.0%",
                "status": "Active / Standard",
                "dpd_string": "000 000 000 000 000 000 000 000 000 000 000 000",
            },
        ],
    },
}


def build_cibil_pdf(data: dict, output_path: str):
    """Builds a pixel-perfect TransUnion CIBIL Commercial CIR PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    story = []
    styles = getSampleStyleSheet()

    # Custom Clean Styles matching official CIBIL CIR fonts
    primary_color = colors.HexColor("#0A2540")  # CIBIL Deep Navy
    cyan_accent = colors.HexColor("#00A3E0")   # CIBIL Cyan
    border_gray = colors.HexColor("#CBD5E1")
    light_bg = colors.HexColor("#F8FAFC")
    dark_gray = colors.HexColor("#1E293B")
    muted_gray = colors.HexColor("#64748B")

    title_style = ParagraphStyle(
        "CIBILTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=primary_color,
    )

    subtitle_style = ParagraphStyle(
        "CIBILSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=muted_gray,
    )

    section_hdr_style = ParagraphStyle(
        "CIBILSection",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=colors.white,
    )

    body_bold = ParagraphStyle(
        "BodyBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=dark_gray,
    )

    body_regular = ParagraphStyle(
        "BodyRegular",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=dark_gray,
    )

    # 1. Header Block (TU CIBIL Official Header)
    header_data = [
        [
            Paragraph("<b>TRANSUNION CIBIL LIMITED</b><br/><font size=7 color='#64748B'>Commercial Credit Information Report (CIR)</font>", title_style),
            Paragraph(f"<b>REPORT CONTROL NUMBER:</b> {data['rcn']}<br/><b>DATE/TIME:</b> {data['report_date']}<br/><b>MEMBER:</b> INQ_SBI_COMM_8941", subtitle_style),
        ]
    ]
    header_table = Table(header_data, colWidths=[3.8 * inch, 3.4 * inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=8))

    # 2. Borrower Profile Information
    story.append(Table([[Paragraph("<b>BORROWER IDENTIFICATION DETAILS</b>", section_hdr_style)]],
                       colWidths=[7.2 * inch],
                       style=[("BACKGROUND", (0, 0), (-1, -1), primary_color),
                              ("TOPPADDING", (0, 0), (-1, -1), 3),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

    profile_rows = [
        [
            Paragraph("<b>Company / Legal Name:</b>", body_bold),
            Paragraph(data["company_name"], body_bold),
            Paragraph("<b>Constitution:</b>", body_bold),
            Paragraph(data["constitution"], body_regular),
        ],
        [
            Paragraph("<b>Trade Name:</b>", body_bold),
            Paragraph(data["trade_name"], body_regular),
            Paragraph("<b>Incorporation Date:</b>", body_bold),
            Paragraph(f"{data['inc_date']} ({data['business_age_years']} Yrs)", body_regular),
        ],
        [
            Paragraph("<b>Income Tax PAN:</b>", body_bold),
            Paragraph(f"<b>{data['pan']}</b>", body_bold),
            Paragraph("<b>GSTIN:</b>", body_bold),
            Paragraph(data["gstin"], body_regular),
        ],
        [
            Paragraph("<b>Industry / Segment:</b>", body_bold),
            Paragraph(data["industry"], body_regular),
            Paragraph("<b>Corporate ID (CIN):</b>", body_bold),
            Paragraph(data["cin"], body_regular),
        ],
        [
            Paragraph("<b>Registered Office:</b>", body_bold),
            Paragraph(data["address"], body_regular),
            Paragraph("<b>State / Pincode:</b>", body_bold),
            Paragraph("Active Commercial Entity", body_regular),
        ],
    ]
    prof_table = Table(profile_rows, colWidths=[1.5 * inch, 2.5 * inch, 1.3 * inch, 1.9 * inch])
    prof_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, border_gray),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(prof_table)
    story.append(Spacer(1, 8))

    # 3. CIBIL MSME Rank (CMR) Showcase Box
    story.append(Table([[Paragraph("<b>CIBIL MSME RANK (CMR) ASSESSMENT</b>", section_hdr_style)]],
                       colWidths=[7.2 * inch],
                       style=[("BACKGROUND", (0, 0), (-1, -1), primary_color),
                              ("TOPPADDING", (0, 0), (-1, -1), 3),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

    rank_color = "#15803D" if data["cmr_rank"] <= 3 else "#B45309" if data["cmr_rank"] <= 6 else "#B91C1C"

    cmr_box_data = [
        [
            Paragraph(f"<font size=24 color='{rank_color}'><b>CMR-{data['cmr_rank']}</b></font><br/><font size=7.5 color='#64748B'>Official Commercial Bureau Scale: 1 (Lowest Risk) to 10 (Highest Risk)</font>", body_bold),
            Paragraph(
                f"<b>Rank Classification:</b> <font color='{rank_color}'><b>{data['cmr_tier']}</b></font><br/>"
                f"<b>Scoring Date:</b> {data['report_date'].split()[0]} | <b>Target Eligibility:</b> CMR-{data['target_rank']}<br/>"
                f"<b>Score Interpretation:</b> Indicates probability of commercial facility becoming NPA (90+ DPD) in the next 12 months based on historical repayment discipline, credit utilization ratios, and enterprise vintage.",
                body_regular,
            ),
        ]
    ]
    cmr_table = Table(cmr_box_data, colWidths=[2.6 * inch, 4.6 * inch])
    cmr_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, border_gray),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cmr_table)
    story.append(Spacer(1, 8))

    # 4. Credit Facility Aggregate Summary
    story.append(Table([[Paragraph("<b>COMMERCIAL CREDIT SUMMARY (AGGREGATE)</b>", section_hdr_style)]],
                       colWidths=[7.2 * inch],
                       style=[("BACKGROUND", (0, 0), (-1, -1), primary_color),
                              ("TOPPADDING", (0, 0), (-1, -1), 3),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

    summary_rows = [
        [
            Paragraph("<b>Total Sanctioned Limit:</b>", body_bold),
            Paragraph(f"INR {data['total_sanctioned']:,}", body_bold),
            Paragraph("<b>Total Current Balance:</b>", body_bold),
            Paragraph(f"INR {data['total_balance']:,}", body_bold),
        ],
        [
            Paragraph("<b>Credit Utilization Ratio:</b>", body_bold),
            Paragraph(f"<b>{data['credit_utilization']*100:.1f}%</b> ({'CRITICAL' if data['credit_utilization']>0.75 else 'HEALTHY'})", body_bold),
            Paragraph("<b>Total Overdue Balance:</b>", body_bold),
            Paragraph(f"INR {data['total_overdue']:,}", body_bold),
        ],
        [
            Paragraph("<b>Active Credit Facilities:</b>", body_bold),
            Paragraph(str(data["active_accounts"]), body_regular),
            Paragraph("<b>Credit History Vintage:</b>", body_bold),
            Paragraph(f"{data['credit_tenure_years']} Years", body_regular),
        ],
    ]
    summary_table = Table(summary_rows, colWidths=[1.8 * inch, 1.8 * inch, 1.8 * inch, 1.8 * inch])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, border_gray),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # 5. Account Details & Repayment Track (DPD Strings)
    story.append(Table([[Paragraph("<b>CREDIT FACILITIES & DPD REPAYMENT HISTORY (PAST 12 MONTHS)</b>", section_hdr_style)]],
                       colWidths=[7.2 * inch],
                       style=[("BACKGROUND", (0, 0), (-1, -1), primary_color),
                              ("TOPPADDING", (0, 0), (-1, -1), 3),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))

    facility_headers = [
        [
            Paragraph("<b>Facility / Bank</b>", body_bold),
            Paragraph("<b>Sanctioned</b>", body_bold),
            Paragraph("<b>Current Balance</b>", body_bold),
            Paragraph("<b>Open Date</b>", body_bold),
            Paragraph("<b>Trailing 12-Month DPD Track</b>", body_bold),
        ]
    ]

    for fac in data["facilities"]:
        facility_headers.append([
            Paragraph(f"<b>{fac['type']}</b><br/><font size=7 color='#64748B'>{fac['bank']}</font>", body_regular),
            Paragraph(f"INR {fac['sanctioned']}", body_regular),
            Paragraph(f"INR {fac['balance']}<br/><font size=7 color='#64748B'>Util: {fac['utilization']}</font>", body_regular),
            Paragraph(fac["open_date"], body_regular),
            Paragraph(f"<code><b>{fac['dpd_string']}</b></code><br/><font size=6.5 color='#15803D'>(000=No delay; 030=30 days late)</font>", body_regular),
        ])

    fac_table = Table(facility_headers, colWidths=[2.2 * inch, 1.1 * inch, 1.2 * inch, 0.9 * inch, 1.8 * inch])
    fac_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, border_gray),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(fac_table)
    story.append(Spacer(1, 10))

    # 6. Official Footer & Legal Statutory Notice
    disclaimer_text = (
        "<b>STATUTORY DISCLAIMER (CICRA 2005): </b>"
        "This commercial credit information report is generated strictly in accordance with the Credit Information "
        "Companies (Regulation) Act, 2005, and Rules made thereunder. The information contained herein is compiled "
        "from data furnished by credit institutions and member banks. All rights reserved by TransUnion CIBIL Limited. "
        "Printed for authorized MSME borrower guidance."
    )
    story.append(Paragraph(disclaimer_text, ParagraphStyle("Disc", parent=styles["Normal"], fontSize=6.5, leading=8.5, textColor=muted_gray)))

    doc.build(story)


def generate_all_sample_reports():
    """Generates the 5 authentic TransUnion CIBIL CIR PDFs in sample_reports/."""
    results = {}
    for archetype_id, data in ARCHETYPES_DATA.items():
        pdf_path = OUTPUT_DIR / data["filename"]
        build_cibil_pdf(data, str(pdf_path))
        results[archetype_id] = {
            "archetype_id": archetype_id,
            "filename": data["filename"],
            "path": str(pdf_path),
            "company_name": data["company_name"],
            "cmr_rank": data["cmr_rank"],
            "cmr_tier": data["cmr_tier"],
        }
    return results


if __name__ == "__main__":
    generated = generate_all_sample_reports()
    print(f"Generated {len(generated)} official CIBIL sample PDFs in {OUTPUT_DIR}")
    for k, v in generated.items():
        print(f" - {v['archetype_id']}: {v['filename']} (CMR-{v['cmr_rank']})")
