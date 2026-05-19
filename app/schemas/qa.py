from typing import List, Optional

from pydantic import BaseModel, Field


class SourceChunk(BaseModel):
    source: str
    chunk_id: str
    content: str
    score: float = Field(default=0.0)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=None, ge=1, le=10)


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceChunk]
    elapsed_ms: int
    used_llm: bool


class ToolRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SummaryResponse(BaseModel):
    summary: str


class KeywordResponse(BaseModel):
    keywords: List[str]


class RecentLogItem(BaseModel):
    question: str
    answer: str
    elapsed_ms: int
    created_at: str
