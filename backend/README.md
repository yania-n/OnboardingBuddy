# OnboardingBuddy Backend

This is the backend API and agent system for OnboardingBuddy, built using **FastAPI**, **SQLite**, and **Google GenAI**. It generates personalized, phased onboarding tasks checklists for new joiners based on markdown documents in the company knowledge base stored in **Google Cloud Storage (GCS)**.

## Architecture & Modules

The backend is structured into modular packages under `app/`:

1. **`app/api`**: RESTful API routers that expose endpoints for:
   - `/api/joiners`: New Hire user profiles and management.
   - `/api/plans`: Personalized onboarding tasks checklists.
   - `/api/tasks`: Check/uncheck individual onboarding tasks or add custom tasks.
   - `/api/chat`: Grounded RAG conversation logs and chatbot query handler.
   - `/api/agents`: Specialist agents dashboard controls.
   - `/api/kb`: Listing and searching knowledge base documents.
   - `/api/feedback`: Management (viewing, resolving, deleting) of unanswered RAG queries.

2. **`app/db`**: Database utilities:
   - `database.py`: SQL/SQLite table creation and CRUD operations.
   - `models.py`: Pydantic Request/Response validation schemas.

3. **`app/agents`**: Specialized AI agent wrappers built using **Google GenAI SDK (`google-genai`)** & **Vertex AI (Gemini 3.6 Flash / `gemini-3.6-flash`)**:
   - `org_expert.py`: Scans handbook files to map BUs, Departments, and Teams.
   - `learning_expert.py`: Creates 30-60-90 day learning plans.
   - `plan_generator.py`: Assembles personalized roadmaps matching the company framework.
   - `qa_chatbot.py`: Handles grounded employee queries and records missing details.




4. **`app/rag`**: Document processing:
   - `parser.py`: Parses markdown files into section-level semantic chunks.
   - `indexer.py`: Embeds, indexes, and searches the parsed document chunks.

## Live Cloud Run Endpoints

- **Base API / UI**: `https://onboarding-buddy-517395366109.europe-southwest1.run.app`
- **Swagger API Documentation**: `https://onboarding-buddy-517395366109.europe-southwest1.run.app/docs`
- **Health Check**: `https://onboarding-buddy-517395366109.europe-southwest1.run.app/health`

---

## Getting Started

### Prerequisites

- Python 3.10+
- Google Gemini API Key (`GEMINI_API_KEY` environment variable)
- Google Cloud SDK (`gcloud`) for cloud deployment

### Installation & Run

1. Install dependencies from the root directory:
   ```bash
   pip install -r requirements.txt
   ```
2. Navigate to the backend directory and start the server:
   ```bash
   python run.py
   ```
   Or reload dynamically from root with PYTHONPATH set:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## Running Tests

Tests are written using `pytest`. Run tests inside the `backend` folder:
```bash
python -m pytest
```


