from fastapi import FastAPI

from app.routers import owner, lender

app = FastAPI(
    title="MSME Financial Health Card API",
    version="0.1.0",
    description="Dual-view (owner + lender) scoring API. See docs/PROJECT_PITCH.md for design.",
)

app.include_router(owner.router)
app.include_router(lender.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "msme-financial-health-card", "phase": "0 - foundations"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
