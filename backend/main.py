"""Phase 1 placeholder FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.schemas import EssayRequest


app = FastAPI(title="PTE Essay Marker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "phase": "1"}


@app.post("/api/grade-essay")
def grade_essay(_: EssayRequest) -> dict:
    raise HTTPException(
        status_code=501,
        detail="Phase 1 scaffold complete. Essay grading is not implemented yet.",
    )
