# Backend

FastAPI service exposing the dual-view API:
- `/owner/*` — prescriptive health card view
- `/lender/*` — risk dashboard view

Currently stubbed (Phase 0). Gets wired to the actual scoring engine in Phase 4,
once `ml/` has a trained model + SHAP explainability layer to call into.

Run:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
