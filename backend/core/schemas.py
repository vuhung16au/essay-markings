"""Pydantic schemas used by the backend API."""

from pydantic import BaseModel, ConfigDict, Field


class EssayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1)
    essay: str = Field(min_length=1)


class ScoreDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int
    max: int


class FeedbackDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    form: str
    grammar: str
    spelling: str


class ScoreBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: ScoreDetail
    development_structure_coherence: ScoreDetail
    form: ScoreDetail
    grammar: ScoreDetail
    linguistic_range: ScoreDetail
    spelling: ScoreDetail
    vocabulary: ScoreDetail


class EssayResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scores: ScoreBundle
    feedback: FeedbackDetail
    good_points: list[str]
    improvements: list[str]
