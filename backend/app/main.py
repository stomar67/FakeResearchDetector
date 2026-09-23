from fastapi import FastAPI

from .routers.papers import router as papers_router


app = FastAPI(
    title="FakeResearchDetector",
    description="Evidence-Grounded Claim Verification System for Research Integrity",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(papers_router)