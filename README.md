# EduPilot — AI Study & Assessment Assistant

EduPilot is an AI-powered study assistant that helps students learn from their own study material, practice with quizzes, and understand where they need to improve.

The project started as a simple PDF question-answering system and evolved into a small AI application with a FastAPI backend, Streamlit frontend, RAG pipeline, tool-using agent, quiz generation, and learner analysis.

## What EduPilot can do

### 1. Ask questions about a PDF
Upload a PDF and ask questions about its content.

EduPilot:
- extracts the PDF text
- splits it into chunks
- creates embeddings
- stores them in FAISS
- retrieves the most relevant sections
- generates an answer using the LLM
- shows the source pages used for the answer

### 2. Use different tools automatically

For each question, the agent decides which capability is appropriate:

- **PDF** — answer from the uploaded study material
- **Calculator** — solve numerical expressions
- **Web** — retrieve current information

This routing is implemented using **LangGraph** rather than manually checking the question type with simple conditionals.

### 3. Generate quizzes

Users can generate quizzes from the uploaded PDF by selecting:
- number of questions
- difficulty
- topic

### 4. Analyze quiz performance

After submitting a quiz, EduPilot evaluates the answers and produces learner-focused feedback, including:
- score
- incorrect answers
- weak topics
- recommendations for further study

---

## How it works

```text
                    ┌─────────────────────┐
                    │   Streamlit UI      │
                    │   Learn / Practice  │
                    │   Progress          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐    ┌────────────┐    ┌──────────┐
        │    RAG   │    │ LangGraph  │    │  Quiz    │
        │ Pipeline │    │   Agent    │    │  System  │
        └────┬─────┘    └─────┬──────┘    └────┬─────┘
             │                │                │
             ▼                ▼                ▼
        ┌──────────┐    ┌────────────┐    ┌──────────┐
        │   Jina   │    │ PDF / Calc │    │ Evaluate │
        │Embeddings│    │ / Web Tool │    │ & Analyze│
        └────┬─────┘    └────────────┘    └──────────┘
             │
             ▼
        ┌──────────┐
        │   FAISS  │
        │ Vector DB│
        └──────────┘
```

## Tech stack

| Area | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| API validation | Pydantic |
| LLM | Groq |
| Agent / routing | LangGraph |
| LLM framework | LangChain |
| Embeddings | Jina AI Embeddings |
| Vector store | FAISS |
| PDF processing | PyPDF |
| Calculations | NumExpr |
| Web search | DuckDuckGo Search |
| Environment management | python-dotenv |
| Containerization | Docker |

---

## Why Jina + FAISS?

The original RAG setup used local sentence-transformer embeddings. During deployment, the embedding model added unnecessary memory pressure to the application.

I moved embeddings to **Jina's hosted embedding API** while keeping FAISS for vector storage.

This keeps the overall RAG architecture simple:

```text
PDF
 ↓
Text splitting
 ↓
Jina Embeddings
 ↓
FAISS
 ↓
Similarity Search
 ↓
LLM
 ↓
Answer + Source Pages
```

The change keeps the RAG architecture lightweight without introducing a separate hosted vector database.

---

## Project structure

```text
EduPilot/
│
├── app.py                  # Streamlit frontend
├── main.py                 # FastAPI application
├── llm.py                  # LLM configuration
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
│
├── api/
│   ├── routes.py           # API endpoints
│   └── schemas.py          # Pydantic request/response models
│
├── agent/
│   ├── graph.py            # LangGraph routing
│   └── tools.py            # Agent tools
│
├── rag/
│   ├── loader.py           # PDF loading
│   ├── splitter.py         # Document chunking
│   ├── embeddings.py       # Jina embedding wrapper
│   ├── vector_store.py     # FAISS operations
│   ├── retriever.py        # Retrieval logic
│   ├── prompts.py
│   ├── generator.py
│   └── topics.py
│
├── quiz/
│   ├── generator.py        # Quiz generation
│   ├── evaluator.py        # Answer evaluation
│   ├── learner.py          # Learner analysis
│   └── state.py
│
├── services/
│   ├── document_service.py
│   └── quiz_service.py
│
└── tests/
    ├── test_rag.py
    └── test_quiz.py
```

---

## Running locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd EduPilot
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=openai/gpt-oss-20b
JINA_API_KEY=your_jina_api_key
```

Do not commit `.env` or expose API keys publicly.

### 5. Start the FastAPI backend

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

### 6. Start the Streamlit frontend

Open another terminal:

```bash
streamlit run app.py
```

The frontend will normally open at:

```text
http://localhost:8501
```

---

## Docker

The project also includes Docker configuration for running the application in containers.

Build and start:

```bash
docker compose up --build
```

The services expose:

```text
FastAPI:   http://localhost:8000
Streamlit: http://localhost:8501
```

Stop the containers:

```bash
docker compose down
```

---

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic API information |
| GET | `/health` | Health check |
| POST | `/documents/upload` | Upload and process a PDF |
| POST | `/ask` | Ask a question |
| POST | `/quiz/generate` | Generate a quiz |
| POST | `/quiz/analyze` | Analyze quiz performance |

FastAPI also provides interactive API documentation at:

```text
http://localhost:8000/docs
```

---

## Main design decisions

### Backend separated from frontend

The application uses FastAPI for the backend and Streamlit for the user interface.

This keeps the core application logic independent from the UI and makes the API directly testable.

### Agent-based routing

Instead of forcing every question through the same RAG pipeline, LangGraph is used to route questions to the appropriate capability.

For example:

```text
"What is the definition of photosynthesis?"
        ↓
       PDF

"What is 25 × 48?"
        ↓
   Calculator

"Who is the current CEO of NVIDIA?"
        ↓
       Web
```

### Persistent document indexes

Uploaded PDFs are identified using a SHA-256 hash.

The hash is used as the vector-store directory name, allowing the application to reuse an existing FAISS index when the same document is uploaded again.

### Source-aware answers

For PDF questions, retrieved document chunks retain page metadata so the UI can show the pages used to generate the answer.

---

## Testing

The project has tests for the RAG and quiz components.

The application was also tested through the Dockerized setup, including:

- PDF upload
- PDF question answering
- source-page navigation
- calculator questions
- web questions
- quiz generation
- quiz submission
- learner analysis
- vector-store persistence

The main production user flows were also checked after deployment.

---

## Current limitations

This is a student-built project and is intentionally kept relatively simple.

Some current limitations include:

- FAISS is local rather than a managed production vector database.
- There is no authentication or user account system.
- Uploaded documents are not stored in a dedicated object-storage service.
- The web-search capability depends on external search availability.
- Free hosting can introduce cold starts and resource limits.
- The application is designed primarily for desktop/laptop use.

---

## Possible future improvements

Some directions I would explore next:

- user authentication and separate study profiles
- cloud object storage for uploaded documents
- a managed vector database such as pgvector, Qdrant, or Pinecone
- better document management and deletion
- richer learner progress tracking
- more quiz question types
- conversation history
- streaming model responses
- improved observability and error handling
- automated deployment and testing through CI/CD

---

## What I learned from building it

The most useful part of this project was not just getting a RAG pipeline to answer questions.

Building EduPilot involved working through practical problems around:

- separating frontend and backend responsibilities
- designing API contracts
- handling document ingestion
- choosing and changing embedding strategies
- managing vector-store persistence
- building tool-based agent routing
- handling deployment memory constraints
- debugging model/tool interactions
- containerizing the application
- validating the complete application instead of only testing individual functions

That process changed the project from a basic LLM demo into a more complete application that I could actually run and deploy.

---

## Author

**Piyush Raj**  
BSc Student, IIT Patna

Built as a portfolio project to explore RAG, LLM agents, backend APIs, and AI-assisted learning systems.
