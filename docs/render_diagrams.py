"""
Generate clean, professional architectural diagrams, flowcharts, UML diagrams,
and mathematical curves for the PBL-III Project Report.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

DIAGRAMS_DIR = Path(__file__).resolve().parent / "diagrams"
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)


def generate_utilization_curve():
    """Plots the Piecewise Non-Linear Credit Utilization Curve."""
    u_vals = np.linspace(0, 1.10, 500)
    scores = []
    for u in u_vals:
        if u <= 0.30:
            s = 100.0
        elif u <= 0.60:
            s = 100.0 - ((u - 0.30) / 0.30) * 30.0
        elif u <= 0.75:
            s = 70.0 - ((u - 0.60) / 0.15) * 30.0
        elif u <= 1.00:
            s = 40.0 - ((u - 0.75) / 0.25) * 40.0
        else:
            s = 0.0
        scores.append(s)

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')

    # Plot zones
    ax.axvspan(0, 0.30, alpha=0.15, color='#10B981', label='Optimal Zone (≤ 30%): 100 pts')
    ax.axvspan(0.30, 0.60, alpha=0.15, color='#3B82F6', label='Normal Working Range (30–60%): 70–100 pts')
    ax.axvspan(0.60, 0.75, alpha=0.18, color='#F59E0B', label='Monitored Danger Zone (60–75%): 40–70 pts')
    ax.axvspan(0.75, 1.10, alpha=0.20, color='#EF4444', label='Critical Distress (> 75%): < 40 pts')

    # Curve
    ax.plot(u_vals * 100, scores, color='#0F1B3D', linewidth=2.8, label='Piecewise Score Curve S_util(u)')

    # Highlight point 78% -> 44 pts (from the real Sharma Engineering screenshot)
    ax.plot(78, 44, marker='o', markersize=8, color='#FF3D8B', zorder=5)
    ax.annotate('Sharma Precision (78% Util → 44/100)\nTop Priority Action!',
                xy=(78, 44), xytext=(52, 22),
                arrowprops=dict(facecolor='#FF3D8B', edgecolor='#FF3D8B', arrowstyle='->', lw=1.8),
                fontsize=9.5, fontweight='bold', color='#FF3D8B',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF0F5', edgecolor='#FF3D8B', alpha=0.9))

    ax.set_title('Piecewise Non-Linear Credit Utilization Function S_util(u)', fontsize=12, fontweight='bold', pad=12, color='#0F1B3D')
    ax.set_xlabel('Credit Utilization Ratio u (%)', fontsize=10.5, fontweight='bold', labelpad=8)
    ax.set_ylabel('Utilization Sub-Score (0–100)', fontsize=10.5, fontweight='bold', labelpad=8)
    ax.set_xlim(0, 110)
    ax.set_ylim(-5, 105)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

    out_path = DIAGRAMS_DIR / "fig_utilization_curve.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_architecture_flowchart():
    """Generates the System Architecture Flowchart."""
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Helper for boxes
    def draw_box(x, y, w, h, title, items, header_bg='#0F1B3D', body_bg='#F8FAFC', border='#0F1B3D'):
        # Header
        box_hdr = patches.FancyBboxPatch((x, y + h - 4.5), w, 4.5, boxstyle="round,pad=0.2",
                                         facecolor=header_bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(box_hdr)
        ax.text(x + w / 2, y + h - 2.3, title, color='#FFFFFF', fontsize=9.5, fontweight='bold',
                ha='center', va='center')
        # Body
        box_bdy = patches.FancyBboxPatch((x, y), w, h - 4.5, boxstyle="round,pad=0.2",
                                         facecolor=body_bg, edgecolor=border, linewidth=1.2)
        ax.add_patch(box_bdy)
        for i, text in enumerate(items):
            ax.text(x + 1.5, y + h - 7.5 - (i * 3.2), f"• {text}", color='#1E293B', fontsize=8, va='center')

    # Layer 1: Ingestion
    draw_box(4, 70, 26, 25, "1. INGESTION LAYER",
             ["TransUnion CIBIL CIR (PDF)", "PyPDF Stream Reader", "Regex Tokenizer & Parser", "Extracts Limits, DPD, Vintage"])

    # Layer 2: Diagnostic & Priority Engine
    draw_box(37, 70, 26, 25, "2. DIAGNOSTIC ENGINE",
             ["Payment History (40% Weight)", "Revolving Utilization (25%)", "Credit Vintage (20%)", "Firm Profile (15%)", "Headroom Priority Index"])

    # Layer 3: Trajectory Forecasting
    draw_box(70, 70, 26, 25, "3. TRAJECTORY ENGINE",
             ["Monthly Markov State Simulator", "Random Forest Surrogate (R²=0.93)", "Simulates Utilization Effort (-8%)", "Estimates Months to CMR-3"])

    # Layer 4: Persistence
    draw_box(18, 20, 30, 32, "4. DATABASE PERSISTENCE",
             ["MySQL Server 8.0 (Port 3306)", "Database: msme_credit_coach", "5 Normalized Relational Tables", "users, profiles, reports, actions", "Resilient SQLite Fallback"],
             header_bg='#1E3A8A', body_bg='#F0F9FF', border='#1E3A8A')

    # Layer 5: Web UI
    draw_box(56, 20, 38, 32, "5. REACT 19 + TAILWIND WEBAPP",
             ["CIBIL MSME Rank Gauge (CMR 1–10)", "4 Factor Diagnostic Cards", "Hot Pink Top-Priority Action Badge", "Daily Habit Logger & ISO Streaks", "Interactive What-If Sandbox"],
             header_bg='#FF3D8B', body_bg='#FFF0F5', border='#FF3D8B')

    # Connective arrows
    def draw_arrow(x1, y1, x2, y2, color='#0F1B3D'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor=color, edgecolor=color, arrowstyle='->', lw=1.8))

    draw_arrow(30, 82.5, 37, 82.5)  # Ingestion -> Diagnostic
    draw_arrow(63, 82.5, 70, 82.5)  # Diagnostic -> Trajectory
    draw_arrow(50, 70, 35, 52)      # Diagnostic -> Database
    draw_arrow(75, 70, 75, 52)      # Trajectory -> UI
    draw_arrow(48, 36, 56, 36)      # Database -> UI

    ax.text(50, 97, "MSME CREDIT COACH — END-TO-END SYSTEM ARCHITECTURE",
            fontsize=12, fontweight='bold', color='#0F1B3D', ha='center', va='center')

    out_path = DIAGRAMS_DIR / "fig_architecture_flowchart.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_uml_sequence_diagram():
    """Generates UML Sequence Diagram."""
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    actors = [
        ("MSME Owner", 10),
        ("React Frontend", 32),
        ("FastAPI Backend", 54),
        ("Diagnostic Engine", 74),
        ("MySQL Database", 92)
    ]

    # Draw lifelines
    for name, x in actors:
        # Header box
        box = patches.FancyBboxPatch((x - 8, 88), 16, 8, boxstyle="round,pad=0.2",
                                     facecolor='#0F1B3D', edgecolor='#0F1B3D')
        ax.add_patch(box)
        ax.text(x, 92, name, color='#FFFFFF', fontsize=8.5, fontweight='bold', ha='center', va='center')
        # Dashed line
        ax.plot([x, x], [12, 88], linestyle='--', color='#94A3B8', linewidth=1.2)

    # Messages
    steps = [
        (10, 32, 80, "1. Upload CIBIL CIR PDF", True),
        (32, 54, 70, "2. POST /cibil/upload (Multipart)", True),
        (54, 74, 60, "3. Extract Parameters & Run Scoring", True),
        (74, 54, 50, "4. Return Scores & Headroom Priority", False),
        (54, 92, 40, "5. INSERT Report & UPSERT Profile", True),
        (92, 54, 30, "6. Transaction Committed (ACID)", False),
        (54, 32, 22, "7. JSON Diagnostic & Playbooks", False),
        (32, 10, 14, "8. Render CMR Gauge & Priority Badge", False)
    ]

    for x1, x2, y, msg, is_call in steps:
        color = '#0F1B3D' if is_call else '#FF3D8B'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(facecolor=color, edgecolor=color, arrowstyle='->', lw=1.5,
                                    linestyle='solid' if is_call else 'dashed'))
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y + 2.2, msg, fontsize=7.5, fontweight='bold', color=color, ha='center', va='bottom')

    ax.text(50, 98, "UML SEQUENCE DIAGRAM: CIBIL CIR UPLOAD & DIAGNOSTIC FLOW",
            fontsize=11, fontweight='bold', color='#0F1B3D', ha='center', va='center')

    out_path = DIAGRAMS_DIR / "fig_uml_sequence_diagram.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_uml_class_diagram():
    """Generates UML Class Diagram."""
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_class(x, y, w, h, name, attrs, methods):
        # Header
        hdr = patches.Rectangle((x, y + h - 5), w, 5, facecolor='#0F1B3D', edgecolor='#0F1B3D')
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - 2.5, name, color='#FFFFFF', fontsize=8.5, fontweight='bold', ha='center', va='center')
        # Body
        body = patches.Rectangle((x, y), w, h - 5, facecolor='#F8FAFC', edgecolor='#0F1B3D', linewidth=1.2)
        ax.add_patch(body)
        # Separator line
        sep_y = y + h - 5 - (len(attrs) * 2.8) - 1.5
        for i, a in enumerate(attrs):
            ax.text(x + 1, y + h - 7 - (i * 2.8), a, fontsize=7, color='#1E293B', va='center')
        ax.plot([x, x + w], [sep_y, sep_y], color='#CBD5E1', linewidth=1)
        for j, m in enumerate(methods):
            ax.text(x + 1, sep_y - 2.5 - (j * 2.8), m, fontsize=7, color='#0369A1', va='center')

    draw_class(5, 50, 26, 42, "User",
               ["+ String owner_id", "+ String full_name", "+ String business_name", "+ String phone", "+ String email", "+ String password_hash"],
               ["+ authenticate(pwd): bool", "+ register(): User"])

    draw_class(37, 50, 30, 42, "BusinessCreditProfile",
               ["+ float on_time_payment_pct", "+ bool has_recent_delinquency", "+ float credit_utilization", "+ float credit_tenure_years", "+ float business_age_years", "+ String industry_risk_tier"],
               ["+ compute_diagnostic(): Result", "+ get_cmr_rank(): int"])

    draw_class(72, 50, 24, 42, "TrajectorySimulator",
               ["+ int max_months = 24", "+ float paydown_rate = 0.08", "+ float payment_rate = 0.03"],
               ["+ simulate(profile, effort): Traj", "+ predict_months_to_target(): int"])

    draw_class(15, 6, 32, 34, "HabitLogger",
               ["+ int action_id", "+ String owner_id", "+ String factor", "+ String description", "+ DateTime logged_at"],
               ["+ log_action(factor, desc): Action", "+ compute_streak_weeks(): int"])

    draw_class(55, 6, 36, 34, "DatabaseAdapter (MySQL / SQLite)",
               ["+ String host = 127.0.0.1:3306", "+ String database = msme_credit_coach", "+ bool sqlite_fallback_active"],
               ["+ get_connection(): Connection", "+ save_profile(profile): void", "+ save_cibil_report(rep): void"])

    ax.text(50, 97, "UML CLASS DIAGRAM: CORE BACKEND & SCORING ENTITIES",
            fontsize=11, fontweight='bold', color='#0F1B3D', ha='center', va='center')

    out_path = DIAGRAMS_DIR / "fig_uml_class_diagram.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


def generate_uml_er_diagram():
    """Generates UML Entity-Relationship Diagram for MySQL Schema."""
    fig, ax = plt.subplots(figsize=(9.5, 5.8), dpi=300)
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def draw_table(x, y, w, h, name, fields):
        hdr = patches.Rectangle((x, y + h - 5), w, 5, facecolor='#0F1B3D', edgecolor='#0F1B3D')
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - 2.5, name, color='#FFFFFF', fontsize=8.5, fontweight='bold', ha='center', va='center')
        bdy = patches.Rectangle((x, y), w, h - 5, facecolor='#F8FAFC', edgecolor='#0F1B3D', linewidth=1.2)
        ax.add_patch(bdy)
        for i, f in enumerate(fields):
            color = '#B91C1C' if 'PK' in f else ('#0369A1' if 'FK' in f else '#1E293B')
            fontw = 'bold' if ('PK' in f or 'FK' in f) else 'normal'
            ax.text(x + 1.2, y + h - 7.5 - (i * 2.8), f, fontsize=7.2, color=color, fontweight=fontw, va='center')

    # Users Table (Center Left)
    draw_table(5, 45, 26, 45, "users",
               ["id (BIGINT, PK)", "owner_id (VARCHAR, UK)", "full_name (VARCHAR)", "business_name (VARCHAR)",
                "phone (VARCHAR, UK)", "email (VARCHAR, UK)", "password_hash (VARCHAR)", "target_rank (TINYINT)",
                "industry_category (ENUM)", "created_at (DATETIME)"])

    # Business Credit Profiles (Top Center)
    draw_table(38, 55, 30, 40, "business_credit_profiles",
               ["id (BIGINT, PK)", "owner_id (VARCHAR, FK)", "on_time_payment_pct (DECIMAL)",
                "has_recent_delinquency (BOOL)", "credit_utilization (DECIMAL)", "credit_tenure_years (DECIMAL)",
                "estimated_cmr_rank (TINYINT)", "overall_proxy_score (DECIMAL)", "source (ENUM)"])

    # CIBIL CIR Reports (Top Right)
    draw_table(73, 55, 24, 40, "cibil_cir_reports",
               ["id (BIGINT, PK)", "owner_id (VARCHAR, FK)", "filename (VARCHAR)", "rcn (VARCHAR)",
                "company_name (VARCHAR)", "pan (VARCHAR)", "cmr_rank (TINYINT)", "total_sanctioned (DECIMAL)",
                "extracted_payload (JSON)"])

    # Logged Actions (Bottom Center)
    draw_table(38, 8, 28, 35, "logged_actions",
               ["id (BIGINT, PK)", "owner_id (VARCHAR, FK)", "factor (ENUM)", "description (TEXT)", "logged_at (DATETIME)"])

    # Alternate Signals (Bottom Right)
    draw_table(71, 8, 26, 35, "alternate_data_signals",
               ["id (BIGINT, PK)", "owner_id (VARCHAR, FK)", "gst_filing_regularity (DECIMAL)",
                "upi_inflow_stability (DECIMAL)", "signal_tier (VARCHAR)", "recorded_at (DATETIME)"])

    # Connector lines
    def draw_rel(x1, y1, x2, y2, label="1 : N"):
        ax.plot([x1, x2], [y1, y2], color='#FF3D8B', linewidth=1.8)
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y, label, fontsize=7.5, fontweight='bold', color='#FF3D8B',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#FFF0F5', edgecolor='#FF3D8B'))

    draw_rel(31, 72, 38, 72, "1 : 1")   # users -> profiles
    draw_rel(68, 75, 73, 75, "1 : N")   # profiles -> reports
    draw_rel(31, 52, 38, 30, "1 : N")   # users -> actions
    draw_rel(66, 25, 71, 25, "1 : 1")   # actions -> alternate signals

    ax.text(50, 97, "MYSQL 8.0 RELATIONAL ENTITY-RELATIONSHIP (ER) DIAGRAM",
            fontsize=11, fontweight='bold', color='#0F1B3D', ha='center', va='center')

    out_path = DIAGRAMS_DIR / "fig_uml_er_diagram.png"
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    generate_utilization_curve()
    generate_architecture_flowchart()
    generate_uml_sequence_diagram()
    generate_uml_class_diagram()
    generate_uml_er_diagram()
    print("All diagrams generated successfully!")
