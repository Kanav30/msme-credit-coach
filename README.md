# MSME Credit Score Improvement Coach

An AI-guided coaching app that helps MSMEs understand their CIBIL MSME Rank (CMR),
tells them what's holding their score back, and tracks logged actions over time
to predict when they'll hit the score a lender needs — without creating or
replacing any official credit score.

> Note: this repo originally started as a dual-view (owner + lender) alternate-data
> scoring platform. That was pivoted after a compliance check — only RBI-licensed
> Credit Information Companies can issue scores used in lending decisions — see
> `docs/PROJECT_PITCH.md` for the current direction.

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
- [ ] Phase 1 — Diagnostic Engine
- [ ] Phase 2 — Action Plan + Self-Logging
- [ ] Phase 3 — Trajectory Prediction Model
- [ ] Phase 4 — Alternate Data Enrichment (stretch goal)
- [ ] Phase 5 — Real User Testing
- [ ] Phase 6 — Polish, Docs, Demo, Pitch Prep

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
