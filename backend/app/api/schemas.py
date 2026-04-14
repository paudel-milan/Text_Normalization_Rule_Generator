"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Any


# ======================================================================
# Request Models
# ======================================================================

class GenerateRequest(BaseModel):
    locale: str = Field(..., description="Language locale code (e.g., hi_IN, ne_NP)")
    category: str = Field(..., description="Category name (e.g., cardinal, currency)")


class NormalizeRequest(BaseModel):
    locale: str = Field(..., description="Language locale code")
    category: str = Field(..., description="Category name")
    text: str = Field(..., description="Input text to normalize")


class ValidateRequest(BaseModel):
    locale: str = Field(..., description="Language locale code")
    category: str = Field(..., description="Category name")
    custom_tests: dict[str, list[str]] | None = Field(
        None,
        description="Optional custom test cases: {positive: [...], negative: [...]}",
    )


class SimulateRequest(BaseModel):
    locale: str = Field(..., description="Language locale code")
    category: str = Field(..., description="Category name")
    input_string: str = Field(..., description="String to simulate DFA against")


class ExportRequest(BaseModel):
    locale: str = Field(..., description="Language locale code")
    category: str = Field(..., description="Category name")


# ======================================================================
# Response Models
# ======================================================================

class RegexInfo(BaseModel):
    pattern: str
    valid: bool
    error: str | None = None


class DfaInfo(BaseModel):
    states: list[str]
    alphabet: list[str]
    transitions: dict[str, dict[str, str]]
    start_state: str
    accept_states: list[str]
    regex_source: str
    state_count: int


class SsmlInfo(BaseModel):
    template: str
    full_template: str
    interpret_as: str
    attributes: dict[str, str]
    example: str


class GenerateResponse(BaseModel):
    locale: str
    language: str
    category: str
    regex: RegexInfo
    dfa: DfaInfo
    ssml: SsmlInfo


class MatchInfo(BaseModel):
    matched_text: str
    span: list[int]
    groups: list[str | None] | None = None
    normalized_form: str
    ssml_form: str


class NormalizeResponse(BaseModel):
    original: str
    normalized: str
    ssml_output: str
    matches: list[MatchInfo]
    category: str
    locale: str
    pattern_used: str | None = None
    error: str | None = None


class TestResult(BaseModel):
    input: str
    expected: str
    actual: str
    passed: bool
    match_details: dict[str, Any] | None = None


class ValidateResponse(BaseModel):
    category: str
    pattern: str
    total_tests: int
    passed: int
    failed: int
    pass_rate: str | None = None
    results: list[TestResult]
    error: str | None = None


class LanguageInfo(BaseModel):
    locale: str
    language: str
    script: str
    categories: list[str]


class SimulateStepInfo(BaseModel):
    state: str
    input: str
    next_state: str | None
    status: str


class SimulateResponse(BaseModel):
    accepted: bool
    steps: list[SimulateStepInfo]
    final_state: str
    rejection_point: int | None = None
    dfa: DfaInfo | None = None
