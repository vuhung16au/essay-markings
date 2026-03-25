"""FastAPI application for the PTE essay marker backend."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.schemas import EssayRequest, EssayResponse
from services.llm_service import LLMServiceError, grade_essay


app = FastAPI(title="PTE Essay Marker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "PTE Essay Marker API"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "phase": "backend_api"}


@app.post("/api/grade-essay", response_model=EssayResponse)
async def grade_essay_endpoint(request: EssayRequest) -> EssayResponse:
    try:
        result = await grade_essay(request.question, request.essay)
        return EssayResponse.model_validate(result)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc
