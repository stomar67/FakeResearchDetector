from fastapi import FastAPI

app = FastAPI(
    title="FakeResearchDetector",
    description="Evidence-Grounded Claim Verification System for Research Integrity",
    version="0.1.0",
)

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}