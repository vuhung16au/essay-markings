"""Pydantic schemas used by the backend API."""

from pydantic import BaseModel, ConfigDict, Field


class EssayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1)
    essay: str = Field(min_length=1)


class ScoreDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0)
    max: int = Field(gt=0)


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
    good_points: list[str] = Field(min_length=1, max_length=5)
    improvements: list[str] = Field(min_length=1, max_length=5)


class DeterministicSignals(BaseModel):
    model_config = ConfigDict(extra="forbid")

    word_count: int = Field(ge=0)
    paragraph_count: int = Field(ge=0)
    sentence_count: int = Field(ge=0)
    transition_hits: int = Field(ge=0)
    typo_hits: int = Field(ge=0)
    grammar_pattern_hits: int = Field(ge=0)
    generic_phrase_hits: int = Field(ge=0)
    prompt_keyword_overlap: int = Field(ge=0)
    prompt_coverage_ratio: float = Field(ge=0)
    all_caps_ratio: float = Field(ge=0)
    bullet_line_count: int = Field(ge=0)
    punctuation_count: int = Field(ge=0)


class DeterministicAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scores: ScoreBundle
    feedback: FeedbackDetail
    signals: DeterministicSignals
    summary: str
