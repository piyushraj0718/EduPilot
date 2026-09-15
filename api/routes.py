import os

from fastapi import APIRouter, HTTPException

from api.schemas import (
    QuestionRequest,
    QuestionResponse,
    QuizRequest,
    LearnerAnalysisRequest,
    LearnerAnalysisResponse
)

from rag.embeddings import get_embeddings
from rag.vector_store import load_vector_store

from agent.graph import create_graph

from quiz.generator import (
    Quiz,
    generate_quiz
)

from quiz.learner import analyze_performance


router = APIRouter()


# =========================
# Basic endpoints
# =========================

@router.get("/")
def home():
    return {
        "message": "EduPilot API is running"
    }


@router.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================
# Helper
# =========================

def load_document_vector_store(file_hash):

    vectorstore_path = os.path.join(
        "vectorstore",
        file_hash
    )

    index_path = os.path.join(
        vectorstore_path,
        "index.faiss"
    )

    if not os.path.exists(index_path):
        raise HTTPException(
            status_code=404,
            detail="Study document not found."
        )

    embeddings = get_embeddings()

    return load_vector_store(
        embeddings,
        vectorstore_path
    )


# =========================
# Ask / Agent
# =========================

@router.post(
    "/ask",
    response_model=QuestionResponse
)
def ask_question(
    request: QuestionRequest
):

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        vector_store = load_document_vector_store(
            request.file_hash
        )

        agent_graph = create_graph(
            vector_store
        )

        result = agent_graph.invoke({
            "question": request.question,
            "source": request.source,
            "tool": "",
            "result": "",
            "answer": "",
            "sources": []
        })

        return {
            "answer": result["answer"],
            "sources": result.get(
                "sources",
                []
            ),
            "tool": result["tool"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to process question: {str(e)}"
        )


# =========================
# Quiz generation
# =========================

@router.post(
    "/quiz/generate",
    response_model=Quiz
)
def create_quiz(
    request: QuizRequest
):

    try:

        vector_store = load_document_vector_store(
            request.file_hash
        )

        quiz = generate_quiz(
            vector_store,
            request.number_of_questions,
            request.difficulty,
            request.topic
        )

        return quiz

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate quiz: {str(e)}"
        )


# =========================
# Learner analysis
# =========================

@router.post(
    "/quiz/analyze",
    response_model=LearnerAnalysisResponse
)
def learner_analysis(
    request: LearnerAnalysisRequest
):

    try:

        quiz = Quiz.model_validate(
            request.quiz
        )

        analysis = analyze_performance(
            quiz,
            request.result
        )

        return analysis

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to analyze performance: {str(e)}"
        )