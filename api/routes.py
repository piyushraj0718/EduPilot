import hashlib
import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File

from api.schemas import (
    QuestionRequest,
    QuestionResponse,
    QuizRequest,
    LearnerAnalysisRequest,
    LearnerAnalysisResponse,
    DocumentUploadResponse
)

from rag.embeddings import get_embeddings
from rag.vector_store import load_vector_store, create_vector_store, save_vector_store
from rag.splitter import split_documents
from rag.topics import extract_topics

from langchain_community.document_loaders import PyPDFLoader

from agent.graph import create_graph

from quiz.generator import (
    Quiz,
    generate_quiz
)

from quiz.learner import analyze_performance


router = APIRouter()


@router.get("/")
def home():
    return {"message": "EduPilot API is running"}


@router.get("/health")
def health_check():
    return {"status": "healthy"}


# Document upload endpoint

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document."""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(status_code=400, detail="Empty file provided.")
        
        file_hash = hashlib.sha256(file_content).hexdigest()
        vectorstore_path = os.path.join("vectorstore", file_hash)
        index_path = os.path.join(vectorstore_path, "index.faiss")
        
        if os.path.exists(index_path):
            try:
                embeddings = get_embeddings()
                load_vector_store(embeddings, vectorstore_path)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(file_content)
                    temp_pdf_path = temp_file.name
                
                try:
                    documents = PyPDFLoader(temp_pdf_path).load()
                    page_count = len(documents)
                    topics = extract_topics(documents)
                    chunk_count = 0  # Unknown for existing stores
                finally:
                    if os.path.exists(temp_pdf_path):
                        os.unlink(temp_pdf_path)
                
                return DocumentUploadResponse(
                    file_hash=file_hash,
                    file_name=file.filename,
                    page_count=page_count,
                    chunk_count=chunk_count,
                    topics=topics
                )
            except Exception:
                pass
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_pdf_path = temp_file.name
        
        try:
            documents = PyPDFLoader(temp_pdf_path).load()
            page_count = len(documents)
            
            chunks = split_documents(documents)
            chunk_count = len(chunks)
            
            embeddings = get_embeddings()
            vector_store = create_vector_store(chunks, embeddings)
            save_vector_store(vector_store, vectorstore_path)
            
            topics = extract_topics(documents)
            
            return DocumentUploadResponse(
                file_hash=file_hash,
                file_name=file.filename,
                page_count=page_count,
                chunk_count=chunk_count,
                topics=topics
            )
        finally:
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to process document: {str(e)}")


def load_document_vector_store(file_hash):
    vectorstore_path = os.path.join("vectorstore", file_hash)
    index_path = os.path.join(vectorstore_path, "index.faiss")
    
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Study document not found.")
    
    embeddings = get_embeddings()
    return load_vector_store(embeddings, vectorstore_path)


@router.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        vector_store = load_document_vector_store(request.file_hash)
        agent_graph = create_graph(vector_store)
        
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
            "sources": result.get("sources", []),
            "tool": result["tool"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to process question: {str(e)}")


@router.post("/quiz/generate", response_model=Quiz)
def create_quiz(request: QuizRequest):
    try:
        vector_store = load_document_vector_store(request.file_hash)
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
        raise HTTPException(status_code=500, detail=f"Unable to generate quiz: {str(e)}")


@router.post("/quiz/analyze", response_model=LearnerAnalysisResponse)
def learner_analysis(request: LearnerAnalysisRequest):
    try:
        quiz = Quiz.model_validate(request.quiz)
        analysis = analyze_performance(quiz, request.result)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to analyze performance: {str(e)}")