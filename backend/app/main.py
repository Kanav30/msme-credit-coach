from fastapi import FastAPI

from app.routers import owner

app = FastAPI(
    title="MSME Credit Score Improvement Coach API",
    version="0.1.0",
    description="Diagnostic + action-plan + trajectory prediction API. See docs/PROJECT_PITCH.md for design.",
)

app.include_router(owner.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "msme-credit-score-coach", "phase": "0 - foundations"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
