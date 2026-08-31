# OnboardingBuddy: AI Personalized Onboarding Platform

**OnboardingBuddy** is an enterprise-grade onboarding platform that automates the creation of personalized, role-based onboarding roadmaps for new hires. It leverages custom LLM agents and a grounded RAG (Retrieval-Augmented Generation) engine to index company handbook files (`kb_docs/`) and generate tailored task checklists and learning plans.

## System Architecture

```
                       ┌──────────────────────────────────────────────────────────┐
                       │                     KNOWLEDGE BASE                       │
                       │  kb_docs/ (Handbooks, RACI, Tools Matrix, Role Guides)  │
                       └────────────────────────────┬─────────────────────────────┘
                                                    │
                                                    ▼
                       ┌──────────────────────────────────────────────────────────┐
                       │                 DOCUMENT RAG & INDEX ENGINE              │
                       │  - Markdown Chunking & Section Parsing                   │
                       │  - Hybrid BM25 & Semantic Search Engine                  │
                       │  - Metadata Tagger (Role, Dept, BU, Tools, Policies)    │
                       └────────────────────────────┬─────────────────────────────┘
                                                    │
                 ┌──────────────────────────────────┼─────────────────────────────────┐
                 ▼                                  ▼                                 ▼
 ┌───────────────────────────────┐  ┌───────────────────────────────┐  ┌───────────────────────────────┐
 │     ORG EXPERT AGENT          │  │    LEARNING EXPERT AGENT      │  │   GROUNDED Q&A CHATBOT AGENT  │
 │ - Org Chart & Hierarchy       │  │ - Drafts Role Learning Plans  │  │ - Strict KB Grounding         │
 │ - BU / Dept / Team Mapping    │  │ - Persists to .md Files       │  │ - Manager Escalation Fallback │
 │ - RACI & Roles Taxonomy       │  │ - Reuses / Generates Cache    │  │ - Missing Query Feedback Log  │
 └───────────────┬───────────────┘  └───────────────┬───────────────┘  └───────────────┬───────────────┘
                 │                                  │                                 │
                 └─────────────────┬────────────────┘                                 │
                                   ▼                                                  │
                 ┌───────────────────────────────────┐                                │
                 │  ONBOARDING PLAN GENERATOR AGENT  │                                │
                 │  - Standard 6-Phase Framework     │                                │
                 │  - Tool Access Checklist (SLA/App)│                                │
                 │  - Phased Roadmap (D1/W1/M1/M3)   │                                │
                 └─────────────────┬─────────────────┘                                │
                                   │                                                  │
                                   ▼                                                  ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   FASTAPI APPLICATION BACKEND                                      │
 │   - RESTful APIs for Onboarding, Tasks, Chat, Learning Plans, KB Search, Analytics, Feedback Logs  │
 │   - SQLite Database Persistence + File-based Storage (Plans & Logs)                                │
 └─────────────────────────────────────────────────┬──────────────────────────────────────────────────┘
                                                   │
                                                   ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │                                   REACT + TAILWIND CSS FRONTEND                                    │
 │   ┌──────────────────────────────────────────────┐  ┌────────────────────────────────────────────┐ │
 │   │             ADMIN / MANAGER PORTAL           │  │              NEW JOINER PORTAL             │ │
 │   │ - New Joiner Onboarding Creator Form         │  │ - Phased Step-by-Step Interactive Checklist│ │
 │   │ - AI Plan Preview & Live Editor              │  │ - Deep KB Document Section Links & Modal   │ │
 │   │ - Analytics & Team Progress Dashboard        │  │ - Real-Time Progress Ring & Milestones     │ │
 │   │ - Learning Plans Repository (.md view/edit)  │  │ - Grounded AI Chatbot with Manager Esc     │ │
 │   │ - Missing Information Feedback Log Inspector │  │ - Quick Role Switcher for Seamless Testing │ │
 │   └──────────────────────────────────────────────┘  └────────────────────────────────────────────┘ │
 └────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Module Descriptions
- **Backend Service**: Built on **FastAPI** to expose REST APIs for joiner creation, onboarding plan adjustments, chat interactions, and management logs.
- **Frontend App**: Built on **React** with **Vite** and **TailwindCSS**, rendering user-friendly dashboards for managers and clear milestone guides for new hires.
- **Org Expert Agent**: Evaluates company documentation to catalog Business Units, Departments, Teams, and roles.
- **Learning Expert Agent**: Outlines customizable role curriculum files (30-60-90 Day) for different departments.
- **Plan Generator Agent**: Reviews access parameters (e.g. tools matrix) and maps them to SLAs and required approvals.
- **Grounded Q&A Chatbot**: A secure RAG chat buddy that references policy documents with precise citations and falls back to manager escalation if the information is missing.

---

## Directory Structure

```text
onboarding_buddy/
├── backend/                  # FastAPI Application Backend
│   ├── app/
│   │   ├── agents/           # Specialized LLM Agents
│   │   ├── api/              # REST Endpoints / Routers
│   │   ├── db/               # SQLite and Pydantic schemas
│   │   └── rag/              # BM25 + Semantic search indexer
│   ├── data/                 # SQLite DB and JSON backups
│   ├── tests/                # Pytest unit tests
│   └── run.py                # Backend startup script
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── api/              # Client API methods
│   │   ├── components/       # Portal modals, lists, and forms
│   │   └── App.jsx           # Root UI dashboard wrapper
│   └── package.json          # Node dependencies
├── requirements.txt          # Global backend dependencies
└── start_servers.py          # Unified system startup script
```

## Live Cloud Run Deployment

The full-stack application is deployed on **Google Cloud Run** with continuous 24/7 availability and public HTTPS access:

| Resource | Public URL | Description |
| :--- | :--- | :--- |
| **Frontend Web App** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app](https://onboarding-buddy-517395366109.europe-southwest1.run.app) | Full React UI with Admin & Joiner dashboards |
| **Interactive API Docs** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app/docs](https://onboarding-buddy-517395366109.europe-southwest1.run.app/docs) | Interactive Swagger UI (OpenAPI specification) |
| **Health Check** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app/health](https://onboarding-buddy-517395366109.europe-southwest1.run.app/health) | System uptime check (`{"status":"healthy"}`) |
| **REST API Base** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app/api/joiners](https://onboarding-buddy-517395366109.europe-southwest1.run.app/api/joiners) | Backend API endpoints |

---

## 🚀 Step-by-Step Setup & Run Guide

### Option A: Local Development Setup

Follow these steps to configure and run OnboardingBuddy locally on your development machine.

#### Step 1: Prerequisites
Make sure you have the following installed:
* **Python 3.10+** (`python --version`)
* **Node.js 18+ & npm** (`node -v` and `npm -v`)
* **Google Gemini API Key** (or Vertex AI default credentials)

#### Step 2: Clone & Navigate
```bash
git clone <repository-url>
cd onboarding_buddy
```

#### Step 3: Set Up Python Backend Dependencies
Create a virtual environment (recommended) and install backend packages:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

#### Step 5: Configure Environment Variables
Set your Gemini API key and GCP project settings in your terminal session or create a `.env` file in the `backend/` directory:
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your-gemini-api-key"
$env:GOOGLE_CLOUD_PROJECT="onboarding-agent-507110"
$env:GOOGLE_CLOUD_REGION="europe-southwest1"

# Linux / macOS
export GEMINI_API_KEY="your-gemini-api-key"
export GOOGLE_CLOUD_PROJECT="onboarding-agent-507110"
export GOOGLE_CLOUD_REGION="europe-southwest1"
```

#### Step 6: Start Local Development Servers
You can run both backend and frontend servers simultaneously using the root startup script:
```bash
python start_servers.py
```

*Alternatively, run each server in separate terminal windows:*
* **Backend Terminal**:
  ```bash
  cd backend
  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```
* **Frontend Terminal**:
  ```bash
  cd frontend
  npm run dev
  ```

#### Step 7: Access Local Applications
* **Frontend Web App**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
* **Backend API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Backend Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### Option B: Local Production Docker Container

To run the complete production bundle (FastAPI + compiled React SPA) inside a single container:

#### Step 1: Build Container
```bash
docker build -t onboarding-buddy .
```

#### Step 2: Run Container
```bash
docker run -d \
  -p 8080:8080 \
  -e GEMINI_API_KEY="your-gemini-api-key" \
  -e GOOGLE_CLOUD_PROJECT="onboarding-agent-507110" \
  --name onboarding-buddy-app \
  onboarding-buddy
```
Access the application at [http://localhost:8080](http://localhost:8080).

---

### Option C: Google Cloud Run Deployment (24/7 Hosting)

Follow these steps to deploy the unified multi-stage application to **Google Cloud Run** with continuous 24/7 uptime.

#### Step 1: Authenticate with Google Cloud
```bash
gcloud auth login
```

#### Step 2: Set Active Project & Region
```bash
gcloud config set project onboarding-agent-507110
gcloud config set run/region europe-southwest1
```

#### Step 3: Enable Required Cloud APIs
Ensure the Cloud Run, Cloud Build, and Artifact Registry APIs are active:
```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

#### Step 4: Deploy Service (24/7 Always-On Configuration)
Deploy directly from source code using the root `Dockerfile`:
```bash
gcloud run deploy onboarding-buddy \
  --source . \
  --region europe-southwest1 \
  --project onboarding-agent-507110 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10 \
  --no-cpu-throttling \
  --memory 512Mi \
  --cpu 1 \
  --port 8080
```

#### Key Deployment Flags Explained:
* `--source .`: Automatically builds and packages the application container via Cloud Build.
* `--min-instances 1`: Guarantees at least 1 warm instance runs **24/7**, eliminating cold starts.
* `--no-cpu-throttling`: Keeps background threads and task timers active outside request lifecycles.
* `--allow-unauthenticated`: Provides public HTTPS access to the web dashboard and REST APIs.
* `--port 8080`: Standard Cloud Run listening port.

#### Step 5: (Optional) Set Environment Secrets on Cloud Run
If providing an API key directly to your Cloud Run service:
```bash
gcloud run services update onboarding-buddy \
  --region europe-southwest1 \
  --set-env-vars GEMINI_API_KEY="your-gemini-api-key"
```

#### Step 6: Verify Live Deployment
Test the deployed Cloud Run service:
```bash
# Health check
curl https://onboarding-buddy-517395366109.europe-southwest1.run.app/health

# Joiners list
curl https://onboarding-buddy-517395366109.europe-southwest1.run.app/api/joiners
```

---

## 🔄 The Feedback Loop

When employees ask the Q&A Chatbot a question that isn't answered in the Knowledge Base:
1. The chatbot responds with a manager escalation prompt.
2. It logs the unanswered query to the **Missing Information Feedback Center**.
3. Managers see these pending queries on their dashboard.
4. Managers can choose to **Resolve & Add to KB** (updating policies) or **Delete Query** if it is duplicate/spam.

---

## 🧪 Automated Verification & Testing

To run the automated test suite locally:
```bash
# Run pytest backend unit tests
cd backend && python -m pytest

# Run End-to-End integration test (against local or Cloud Run)
python e2e_verification.py
```


