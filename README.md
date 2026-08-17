# MSME Financial Health Card

A portable, dual-view, explainable financial health score for MSMEs — built on alternate data (GST, UPI, EPFO, Udyam) and designed to sit as a neutral scoring layer within India's ULI/OCEN/Account Aggregator ecosystem.

Full project pitch, UML, user flow: [`docs/PROJECT_PITCH.md`](docs/PROJECT_PITCH.md)
Detailed phase roadmap: [`docs/PHASE_PLAN.md`](docs/PHASE_PLAN.md)

## Repo structure

```
msme-financial-health-card/
├── docs/               # Pitch doc, phase plan, diagrams
├── ml/                 # Data, notebooks, feature engineering, model training
│   ├── data/
│   ├── notebooks/
│   └── src/
├── backend/            # FastAPI backend — owner & lender API views
│   └── app/
│       ├── routers/    # owner.py, lender.py
│       ├── models/
│       └── core/
└── frontend/           # React dashboards (owner view + lender view) — built in Phase 4
```

## Current status

- [x] Phase 0 — Foundations (repo scaffold + learning starter)
- [ ] Phase 1 — Data Foundation
- [ ] Phase 2 — Core Scoring Model
- [ ] Phase 3 — Explainability + Prescriptive Layer
- [ ] Phase 4 — Dual-View Platform
- [ ] Phase 5 — Trust & Compliance Layer
- [ ] Phase 6 — Testing & Refinement
- [ ] Phase 7 — Documentation, Demo & Pitch Prep

## Quickstart

### ML environment (start here — Phase 0/1 work happens here)
```bash
cd ml
python -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python notebooks/00_phase0_python_basics.py
```

### Backend (comes into play from Phase 4 onward)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# visit http://127.0.0.1:8000/docs for the auto-generated API docs
```

## License
TBD — add one once you're ready to make the repo public (MIT is a common default for student/portfolio projects).
