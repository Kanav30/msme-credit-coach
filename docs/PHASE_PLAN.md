# Phase Plan — MSME Credit Score Improvement Coach

### Roadmap & Completion Status

---

### [x] Phase 0 — Foundations & Risk Vocabulary (Completed)
- Python data science stack: `pandas`, `numpy`, `matplotlib`, `scikit-learn`.
- Exploratory data analysis & baseline classification models ([`00_phase0_python_basics.py`](../ml/notebooks/00_phase0_python_basics.py)).
- Domain research: Commercial CIBIL MSME Rank (CMR 1 to 10) vs personal CIBIL (300 to 900), CICRA 2005 regulatory compliance boundaries.

---

### [x] Phase 1 — Diagnostic & Actionability Engine (Completed)
- Rule-based proxy diagnostic breakdown using the 4 publicly documented CMR factors:
  - Payment History (~40%)
  - Credit Utilization (~25%)
  - Credit Tenure (~20%)
  - Firm Profile (~15%)
- Gap-to-target calculator mapping 0–100 scores to CMR-1 through CMR-10.
- **Actionability Weighting Algorithm**: Ranks fixes by realistic speed to improve (fast levers like utilization vs gradual levers like tenure) rather than misleading raw headroom.
- Verified on 5 realistic MSME archetypes ([`01_phase1_diagnostic_test.py`](../ml/notebooks/01_phase1_diagnostic_test.py)).

---

### [x] Phase 2 — Prescriptive Action Plan & Habit Tracking (Completed)
- Dynamic recommendation engine generating specific, numbers-based advice text per factor.
- Self-logging feature with persistent SQLite storage (`logged_actions` in `app_data.db`).
- Weekly calendar habit streak counter (tracking consecutive Monday–Sunday periods of logged actions).

---

### [x] Phase 3 — Trajectory Forecasting Model (Completed)
- **Deterministic Trajectory Simulator** ([`trajectory_simulator.py`](../ml/src/trajectory_simulator.py)): Month-by-month projection accounting for active balance paydowns (-8%/mo) and clean payment streaks (+3%/mo, delinquency aged out in 3 mos).
- **Random Forest ML Surrogate** ([`trajectory_model.py`](../ml/src/trajectory_model.py)): Trained on 3,000 synthetic simulation trajectories ($R^2 \approx 0.93$, $\text{MAE} \approx 1.5$) to provide rapid approximations.
- Verified that active effort drives the forecast (different answers before and after actions are logged).

---

### [x] Phase 4 — Decoupled Alternate Data Signals (Completed)
- Trailing 6-month GST filing regularity + UPI cash flow stability index ([`alternate_data.py`](../ml/src/alternate_data.py)).
- Strictly decoupled from the bureau rank calculation per CICRA 2005 rules, serving as an early cash-flow signal.

---

### [x] Phase 5 — Real User Testing Kit & Archetypes (Completed)
- Interactive CLI interview runner ([`demo_cli.py`](../ml/notebooks/demo_cli.py)) and structured questionnaire kit ([`PHASE5_TESTING_KIT.md`](PHASE5_TESTING_KIT.md)) for Chartered Accountants (CAs) and MSME promoters.
- 5 comprehensive business scenarios calibrated from public bureau thresholds (Struggling, Healthy, Thin-file, Maxed-out utilization, Mediocre).

---

### [x] Phase 6 — Minimalist UI, Ingestion, & Product Delivery (Completed)
- **TransUnion CIBIL CIR PDF Ingestion**:
  - ReportLab generator creating authentic commercial CIBIL CIR reports across all 5 archetypes ([`cibil_generator.py`](../backend/app/core/cibil_generator.py)).
  - PDF parser ([`cibil_parser.py`](../backend/app/core/cibil_parser.py)) extracting RCN, CMR rank, utilization, DPD repayment history, and tenure directly from bureau files.
- **Minimalist Light Beige Frontend (`#F5F5F0`)**:
  - Crisp white cards with warm borders; removed all dark neon "cyber/AI" styling.
  - Interactive CIBIL Report Tab with live PDF upload, sample downloads, and instant scenario loading.
  - Radial CMR Rank gauge, prioritized action checklist, habit streak tracker, and trajectory projection chart.
  - Educational Product Landing Page explaining the MSME credit gap, problem statement, and 4-step user guide.
  - Full Authentication System (Signup, Login, and 1-Click Instant Demo Login).
  - What-If Scenario Sandbox with live recalculation.

---

### [x] Phase 7 — Borrower-First Refocus: Credit Score Diagnostics, Multi-Step Tips & Daily Logs (Completed)
- **Lender Audit Decommissioning**:
  - Completely purged lender audit views (`LenderView.jsx`, `backend/app/routers/lender.py`, and `/lender` endpoints).
  - Redirected 100% of application value toward empowering MSME promoters and accountants directly.
- **Daily Credit Habit & Action Logging Engine**:
  - Interactive daily checklist (`DailyActionTracker.jsx`) tracking 5 fundamental credit hygiene habits (utilization sweep, NACH balance check, on-time vendor settlement, bureau dispute audit).
  - Weekly streak counter, category filtering, and 1-click preset action logging.
  - Full local storage persistence for daily completed habits alongside backend SQLite historical tracking.
- **Structured Multi-Step Improvement Playbook**:
  - Transformed factor cards (`FactorCard.jsx`) from simple text recommendations into a 3-part structured roadmap:
    - ⚡ **7-Day Quick Win**: Immediate action to stabilize the factor right now.
    - 🎯 **30–90 Day Target**: Sustainable operational milestone to lock in rank improvements.
    - ⚠️ **Mistakes to Avoid**: Critical warning flags (e.g. closing oldest credit line, high end-of-month utilization spikes).
  - 1-Click action logging directly from factor cards to update streaks and trajectory projections in real-time.

---

### [x] Phase 8 — Enterprise Cloud Database Migration (Completed)
- **TiDB Cloud Serverless Architecture**:
  - Migrated from local storage to distributed NewSQL **TiDB Cloud Serverless** cluster in AWS Singapore (`ap-southeast-1`, Port 4000).
  - Enforced TLS/SSL encryption in transit (`MYSQL_SSL=true`).
  - Implemented 5 normalized relational tables (BCNF): `users`, `business_credit_profiles`, `cibil_cir_reports`, `logged_actions`, `alternate_data_signals`.
  - Added connection pooling, automatic failover resilience, and parameterized SQL statements preventing injection.

---

### [x] Phase 9 — Full-Stack Cloud Deployment & ETE Academic Release (Completed)
- **Production Cloud Hosting**:
  - **FastAPI Backend on Render**: Continuous deployment pipeline with automated health checks, Uvicorn asynchronous workers, and cloud database integration.
  - **React SPA on Vercel**: Global edge CDN delivery with Vite compilation, SPA client routing rewrites, and environment variable configuration.
- **Academic ETE Rubrics Alignment**:
  - Authored comprehensive ETE Rubrics & Viva Voce Guide ([`docs/ETE_EVALUATION_AND_VIVA_GUIDE.md`](ETE_EVALUATION_AND_VIVA_GUIDE.md)) addressing all 4 official assessment criteria.
  - Authored complete Cloud Deployment Guide ([`docs/CLOUD_DEPLOYMENT_GUIDE.md`](CLOUD_DEPLOYMENT_GUIDE.md)).
  - Generated full academic project report in `.docx` format with embedded UML, mathematical curves, and institutional branding.
