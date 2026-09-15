from typing import Any, Literal

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str
    file_hash: str
    source: Literal["AUTO", "PDF", "WEB"] = "AUTO"


class QuestionResponse(BaseModel):
    answer: str
    sources: list[int]
    tool: str


class QuizRequest(BaseModel):
    file_hash: str
    number_of_questions: int
    difficulty: str
    topic: str


class LearnerAnalysisRequest(BaseModel):
    quiz: dict[str, Any]
    result: dict[str, Any]


class LearnerAnalysisResponse(BaseModel):
    weak_topics: Any
    recommendation: str