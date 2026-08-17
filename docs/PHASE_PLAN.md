# Phase-Wise Implementation Plan

### Phase 0 — Foundations (Weeks 1–4)
- Learn Python data stack: pandas, numpy, matplotlib, scikit-learn basics
- Study credit risk fundamentals: default, PD, AUC-ROC, precision/recall, class imbalance
- Read RBI/SIDBI MSME reports; understand AA / OCEN / ULI architecture
- Rebuild 2–3 public credit-risk notebooks (e.g. Home Credit Default Risk) yourself
- Study Jocata/Perfios public materials for competitive positioning context

### Phase 1 — Data Foundation (Weeks 5–8)
- Design synthetic dataset simulating GST filing patterns, UPI transaction velocity/volatility, EPFO contributions, Udyam registration completeness
- Define the 4 scoring pillars and their underlying raw features
- Build data cleaning/preprocessing pipeline

### Phase 2 — Core Scoring Model (Weeks 9–14)
- Feature engineering per pillar (see `ml/src/feature_engineering.py`)
- Baseline: logistic regression, upgrade to Random Forest / XGBoost / LightGBM
- Handle class imbalance (SMOTE / class weighting)
- Evaluate with AUC-ROC, precision-recall, report honestly, don't chase 90%
- Build weighted aggregate score from the 4 pillars

### Phase 3 — Explainability + Prescriptive Layer (Weeks 15–18)
- Integrate SHAP for per-prediction explainability
- Build rule-based mapping: weak feature to plain-language improvement tip
- User-test explanations for actual understandability

### Phase 4 — Dual-View Platform (Weeks 19–26)
- Backend API: role-based endpoints (see `backend/app/routers/owner.py` and `lender.py`)
- Owner dashboard (React): health card + prescriptive tips
- Lender dashboard (React): risk tier, PD, SHAP panel, audit trail
- Mock AA/consent-flow simulation
- Auth + role-based access control

### Phase 5 — Trust & Compliance Layer (Weeks 27–32)
- Score certification: digital signing/hashing for tamper-proof scores
- Consent audit trail
- Bias/fairness testing across synthetic segments

### Phase 6 — Testing & Refinement (Weeks 33–40)
- Synthetic MSME personas walked through the full flow
- Feedback from a CA/bank/NBFC contact if possible
- UI/UX polish

### Phase 7 — Documentation, Demo & Pitch Prep (Weeks 41–48)
- Deploy live demo
- Write up methodology (doubles as report material)
- Demo video + slide deck
- Target relevant fintech/MSME hackathons for external validation
