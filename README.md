# MSME Credit Score Improvement Coach

An AI-guided coaching platform that helps Indian MSMEs understand their **CIBIL MSME Rank (CMR 1 to 10)**, identifies what is holding their score back, prioritizes actionable improvements, tracks weekly discipline streaks, and projects when they will achieve bank loan eligibility — **without creating or replacing any official credit score**.

> **Regulatory Compliance Note (CICRA 2005):**
> Under Indian law, only 4 RBI-licensed Credit Information Companies (TransUnion CIBIL, Experian, Equifax, CRIF High Mark) are legally authorized to compute credit scores used in lending decisions. This product never computes a competing score. It interprets official bureau reports (CIR), coaches the business owner on prioritized fixes, and forecasts when they will meet formal lending criteria.

---

## Key Features

1. **Official CIBIL Report (PDF) Ingestion**:
   - **Upload & Auto-Parse**: Upload official TransUnion CIBIL Commercial CIR reports (.pdf). Extracts RCN, company identity, CMR rank, credit utilization, DPD repayment conduct, and credit vintage.
   - **Pre-Generated Realistic Samples**: Includes 5 authentic CIBIL sample PDFs generated with ReportLab matching the exact layout and data structures issued by TransUnion CIBIL.
2. **Transparent Factor Diagnostic**:
   - Deconstructs the 4 bureau factors: Payment History (~40%), Credit Utilization (~25%), Credit Tenure (~20%), and Firm Profile (~15%).
   - **Actionability Weighting**: Prioritizes fast-moving levers (utilization) over slow-moving ones (tenure).
3. **Weekly Habit & Streak Tracker**:
   - Logs micro-actions (e.g. balance paydowns, NACH autopay mandate, bureau dispute filing) with a weekly streak counter to build verified borrower discipline.
4. **Trajectory Forecasting**:
   - **Deterministic Simulator**: Month-by-month projection showing the exact timeline to target loan eligibility rank (e.g. CMR-3).
   - **Random Forest ML Surrogate**: Cross-validated with $R^2 \approx 0.93$.
5. **Decoupled Alternate Data Signals**:
   - Supplementary early-warning indicators based on GST return regularity and UPI cash flow consistency.
6. **Daily Habits & Micro-Action Tracker**:
   - Daily financial hygiene checklist (5 positive borrower daily habits with local storage persistence), active weekly streak counter, and 1-click preset action logger.
7. **Structured 3-Tier Factor Playbooks**:
   - Transparent factor breakdown with 7-Day Quick Wins, 30–90 Day Milestones, and Costly Mistakes to Avoid.
8. **What-If Scenario Sandbox**:
   - Interactive sliders and discipline toggles to simulate different turnaround paths.
9. **Modern High-Contrast Navy & Hot Pink Theme**:
   - Deep navy (`#0F1B3D` background, `#15244E` cards), warm light beige / soft ivory text (`#FAF7F2`), and vibrant hot pink (`#FF3D8B`) contrast highlights, CTAs, flame streaks, and active states.

---

## Repo Structure

```
msme-financial-health-card/
├── docs/                                # Technical walkthrough, pitch, phase plan, interview kit
│   ├── PROJECT_WALKTHROUGH.md
│   ├── PROJECT_PITCH.md
│   ├── PHASE_PLAN.md
│   └── PHASE5_TESTING_KIT.md
├── ml/                                  # Data science, simulation & ML engine
│   ├── src/
│   │   ├── feature_engineering.py       # Diagnostic engine, scoring rules & action plan
│   │   ├── trajectory_simulator.py      # Month-by-month trajectory simulator
│   │   ├── trajectory_model.py          # Random Forest ML surrogate
│   │   └── alternate_data.py            # Phase 4 GST/UPI supplementary signals
│   └── notebooks/
│       ├── 00_phase0_python_basics.py   # Baseline risk ML workflow
│       ├── 01_phase1_diagnostic_test.py # 5 archetype validation tests
│       └── demo_cli.py                  # Terminal interview CLI runner
├── backend/                             # FastAPI REST API & Ingestion Engine
│   ├── app/
│   │   ├── core/
│   │   │   ├── logging_store.py         # Persistent SQLite user & action storage
│   │   │   ├── cibil_parser.py          # CIBIL Commercial CIR PDF parser
│   │   │   └── cibil_generator.py       # Authentic ReportLab CIBIL CIR generator
│   │   ├── routers/
│   │   │   ├── auth.py                  # Signup, login, and 1-click demo access
│   │   │   ├── cibil.py                 # CIBIL PDF upload, samples & streaming
│   │   │   └── owner.py                 # Owner diagnostic & prediction endpoints
│   │   ├── sample_reports/              # 5 generated TransUnion CIBIL sample PDFs
│   │   └── main.py                      # FastAPI initialization & CORS
│   └── requirements.txt
└── frontend/                            # React 19 + Vite + Vanilla CSS SPA
    ├── src/
    │   ├── components/
    │   │   ├── LandingPage.jsx          # Educational landing page & user guide
    │   │   ├── AuthPage.jsx             # Signup, login & 1-click demo access
    │   │   ├── CibilReportTab.jsx       # PDF upload, sample download & inspection
    │   │   ├── ScoreGauge.jsx           # Radial CMR rank meter (1 to 10)
    │   │   ├── FactorCard.jsx           # 4 factor cards with 3-tier actionable playbooks
    │   │   ├── DailyActionTracker.jsx   # Daily habit checklist & action log timeline
    │   │   ├── StreakTracker.jsx        # Habit streak counter & event timeline
    │   │   ├── TrajectoryChart.jsx      # Month-by-month SVG projection curve
    │   │   ├── AlternateDataCard.jsx    # GST & UPI sliders
    │   │   ├── WhatIfSandbox.jsx        # Interactive scenario sandbox
    │   │   └── Navbar.jsx               # Navigation & profile pill
    │   ├── api.js                       # Frontend REST client
    │   ├── App.jsx                      # App controller & view routing
    │   └── index.css                    # Navy, Light Beige & Hot Pink theme
    └── package.json
```

---

## Current Status

- [x] Phase 0 — Foundations (Credit risk modeling, exploratory data analysis)
- [x] Phase 1 — Diagnostic Engine (4 factor breakdown & actionability ranking)
- [x] Phase 2 — Action Plan & Habit Tracking (Prescriptions & SQLite weekly streaks)
- [x] Phase 3 — Trajectory Forecasting Model (Deterministic simulator + Random Forest ML)
- [x] Phase 4 — Decoupled Alternate Data Signals (GST regularity & UPI stability)
- [x] Phase 5 — Real User Testing Kit & 5 Archetypes (Interview script & CLI)
- [x] Phase 6 — Minimalist Frontend, Ingestion & Polish (CIBIL PDF parser, light beige UI, landing & auth)
- [x] Phase 7 — Borrower-Centric Pivot (Score Clarity, 3-Tier Factor Playbooks, Daily Habit Checklist & Logging Engine)
- [x] Phase 8 — Enterprise Cloud Database Migration (TiDB Cloud Serverless MySQL on AWS Singapore with TLS/SSL)
- [x] Phase 9 — Full-Stack Cloud Deployment & ETE Academic Release (Render Backend + Vercel Frontend + ETE Rubrics Mapping)

---

## Production Cloud Deployment

The application is deployed across free-tier, production-ready cloud services:

| Component | Platform | Region / Host | Protocol |
| :--- | :--- | :--- | :--- |
| **Frontend SPA** | **Vercel** | Global Edge CDN | HTTPS (Port 443) |
| **Backend REST API** | **Render.com** | Singapore (`ap-southeast-1`) | HTTPS (Port 443) |
| **Relational Database** | **TiDB Cloud Serverless** | AWS Singapore (`ap-southeast-1`) | MySQL Wire + TLS (Port 4000) |

Detailed deployment instructions: [`docs/CLOUD_DEPLOYMENT_GUIDE.md`](docs/CLOUD_DEPLOYMENT_GUIDE.md)

---

## ETE Evaluation Rubrics & Viva Voce Defense

This project conforms strictly to the **PBL-III End-Term Evaluation Criteria**:
1. **Implementation & Methodology Adopted** (5-factor mathematical model, Ridge regression ML, TiDB Serverless schema).
2. **Outcome Status** (Live working cloud demonstration, unit tests, BCNF normalization).
3. **Presentation** (Structured 8-10 minute pitch script and diagrammatic walkthrough).
4. **Viva Voce (Q&A)** (Detailed answers on CICRA 2005 compliance, mathematical convexity, and database design).

Comprehensive guide: [`docs/ETE_EVALUATION_AND_VIVA_GUIDE.md`](docs/ETE_EVALUATION_AND_VIVA_GUIDE.md)

---

## Quickstart

### 1. Start the Backend API (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- API Docs: `http://127.0.0.1:8000/docs`

### 2. Start the Frontend (Vite + React)
```bash
cd frontend
npm install
npm run dev
```
- Open in browser: `http://localhost:5173/`

### 3. Generate or Inspect CIBIL Sample Reports
```bash
python backend/app/core/cibil_generator.py
```
This generates 5 authentic sample CIBIL CIR PDFs in `backend/app/sample_reports/`.

---

## Documentation Links
- Full technical walkthrough: [`docs/PROJECT_WALKTHROUGH.md`](docs/PROJECT_WALKTHROUGH.md)
- Product pitch & competitive positioning: [`docs/PROJECT_PITCH.md`](docs/PROJECT_PITCH.md)
- Phase roadmap & completion details: [`docs/PHASE_PLAN.md`](docs/PHASE_PLAN.md)
- Testing interview guide & script: [`docs/PHASE5_TESTING_KIT.md`](docs/PHASE5_TESTING_KIT.md)
