# Implementation Plan: AI Personalized Onboarding Platform (OnboardingBuddy)

Build a full-stack, enterprise-grade AI Onboarding web application that generates personalized, phased onboarding roadmaps for new hires based on company knowledge base documents (`kb_docs/`) and metadata parameters (Role, Team, Department, Business Unit).

---

## 1. System Architecture & Component Design

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
                ┌─────────────────────────────────┼─────────────────────────────────┐
                ▼                                 ▼                                 ▼
┌───────────────────────────────┐ ┌───────────────────────────────┐ ┌───────────────────────────────┐
│     ORG EXPERT AGENT          │ │    LEARNING EXPERT AGENT      │ │   GROUNDED Q&A CHATBOT AGENT  │
│ - Org Chart & Hierarchy       │ │ - Drafts Role Learning Plans  │ │ - Strict KB Grounding         │
│ - BU / Dept / Team Mapping    │ │ - Persists to .md Files       │ │ - Manager Escalation Fallback │
│ - RACI & Roles Taxonomy       │ │ - Reuses / Generates Cache    │ │ - Missing Query Feedback Log  │
└───────────────┬───────────────┘ └───────────────┬───────────────┘ └───────────────┬───────────────┘
                │                                 │                                 │
                └─────────────────┬───────────────┘                                 │
                                  ▼                                                 │
                ┌───────────────────────────────────┐                               │
                │  ONBOARDING PLAN GENERATOR AGENT  │                               │
                │  - Standard 6-Phase Framework     │                               │
                │  - Tool Access Checklist (SLA/App)│                               │
                │  - Phased Roadmap (D1/W1/M1/M3)   │                               │
                └─────────────────┬─────────────────┘                               │
                                  │                                                 │
                                  ▼                                                 ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 FASTAPI APPLICATION BACKEND                                        │
│  - RESTful APIs for Onboarding, Tasks, Chat, Learning Plans, KB Search, Analytics, Feedback Logs  │
│  - SQLite Database Persistence + File-based Storage (Plans & Logs)                               │
└─────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 REACT + TAILWIND CSS FRONTEND                                     │
│  ┌──────────────────────────────────────────────┐ ┌──────────────────────────────────────────────┐│
│  │             ADMIN / MANAGER PORTAL           │ │              NEW JOINER PORTAL               ││
│  │ - New Joiner Onboarding Creator Form         │ │ - Phased Step-by-Step Interactive Checklist   ││
│  │ - AI Plan Preview & Live Editor              │ │ - Deep KB Document Section Links & Modal     ││
│  │ - Analytics & Team Progress Dashboard        │ │ - Real-Time Progress Ring & Milestones       ││
│  │ - Learning Plans Repository (.md view/edit)  │ │ - Grounded AI Chatbot with Manager Escalation││
│  │ - Missing Information Feedback Log Inspector │ │ - Quick Role Switcher for Seamless Testing   ││
│  └──────────────────────────────────────────────┘ └──────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Database Schema & File Storage

### SQLite Schema (`backend/data/onboarding.db`)
1. **`users`**
   - `id` (TEXT, PK): UUID
   - `name` (TEXT)
   - `email` (TEXT, UNIQUE)
   - `role` (TEXT)
   - `team` (TEXT)
   - `department` (TEXT)
   - `business_unit` (TEXT)
   - `seniority` (TEXT)
   - `start_date` (TEXT)
   - `status` (TEXT): `'active' | 'draft' | 'completed'`
   - `created_at` (TEXT), `updated_at` (TEXT)

2. **`onboarding_plans`**
   - `id` (TEXT, PK): UUID
   - `user_id` (TEXT, FK -> users.id)
   - `status` (TEXT): `'draft' | 'published' | 'archived'`
   - `overview` (TEXT): Summary of objectives and expectations
   - `created_at` (TEXT), `updated_at` (TEXT)

3. **`onboarding_tasks`**
   - `id` (TEXT, PK): UUID
   - `plan_id` (TEXT, FK -> onboarding_plans.id)
   - `phase` (TEXT): `'Phase 1: Welcome (Day 1-2)' | 'Phase 2: Bearings (Week 1)' | 'Phase 3: Learning (Month 1)' | 'Phase 4: Hands Dirty (Days 30-50)' | 'Phase 5: Ready to Own (Days 61-89)' | 'Phase 6: Finish Line (Day 90)'`
   - `title` (TEXT)
   - `description` (TEXT)
   - `category` (TEXT): `'access_setup' | 'reading' | 'training' | 'meeting' | 'deliverable'`
   - `tool_name` (TEXT, nullable)
   - `provisioning_channel` (TEXT, nullable)
   - `required_approvals` (TEXT, nullable)
   - `sla` (TEXT, nullable)
   - `kb_doc_reference` (TEXT, nullable): Document filename and section
   - `is_completed` (INTEGER): 0 or 1
   - `completed_at` (TEXT, nullable)
   - `order_index` (INTEGER)

4. **`chat_messages`**
   - `id` (TEXT, PK)
   - `user_id` (TEXT)
   - `role` (TEXT): `'user' | 'assistant'`
   - `content` (TEXT)
   - `citations` (TEXT): JSON string of referenced document sections
   - `is_missing_info` (INTEGER): 1 if model fell back to manager escalation
   - `created_at` (TEXT)

5. **`missing_information_feedback`**
   - `id` (TEXT, PK)
   - `user_id` (TEXT, nullable)
   - `user_name` (TEXT, nullable)
   - `user_role` (TEXT, nullable)
   - `query` (TEXT)
   - `context_bu` (TEXT, nullable)
   - `timestamp` (TEXT)
   - `status` (TEXT): `'pending' | 'resolved'`
   - `resolution_notes` (TEXT, nullable)

### File-Based Persistence
- **Organization Expert Knowledge Base**: `backend/data/org_knowledge.json` (persisted structured org graph, BUs, departments, teams, roles, RACI, reporting hierarchies, and scan metadata)
- **Role Learning Plans**: `backend/data/learning_plans/<role_slug>.md`
- **Missing Information Export**: `backend/data/missing_kb_queries.json`
- **Knowledge Base Index Cache**: `backend/data/kb_index.json`

---

## 3. Core Agents & AI RAG Engine Design

### 1. Document Processing & RAG Engine (`backend/app/rag/`)
- Parses all Markdown files in `kb_docs/`.
- Extracts headers, tables, tool matrices, training codes (e.g., `SEC-101`, `CMP-101`, `EHS-101`, `DATA-101`, `GTM-PITCH-101`), SLAs, and RACI matrices.
- Indexes chunks with BM25 keyword matching + semantic token similarity + metadata filters (by BU, Department, Role).
- Provides exact source pointers: file name, section title, line range, and excerpt.

### 2. Organization Expert Agent (`backend/app/agents/org_expert.py`)
- **Persistent Knowledge Graph**:
  * Scans and parses `01_ORG_STRUCTURE.md`, `03_ROLES_RESPONSIBILITIES.md`, `05_GO_TO_MARKET_STRUCTURE.md`, etc., extracting Business Units, Departments, Teams, Roles, Hierarchies, RACI, and Cross-BU Synergies.
  * Persists this structured model to `backend/data/org_knowledge.json` so it does NOT re-create the organization for each joiner.
- **On-Demand KB Scan & Change Detection**:
  * Exposes a `scan_knowledge_base()` trigger (accessible via API `POST /api/agents/org-expert/scan` and Admin UI button).
  * Analyzes document checksums/timestamps, detects additions or modifications to the organizational structure, merges changes, updates the graph, and records `last_scanned_at` and change logs.
- **Org Query & Context Provider**:
  * Serves instant org structure queries, reporting lines, team overviews, and cross-functional linkages to the Onboarding Generator and Q&A Chatbot.

### 3. Learning Expert Agent (`backend/app/agents/learning_expert.py`)
- Checks if a markdown learning plan exists in `backend/data/learning_plans/<role_slug>.md`.
- If cached, loads the plan.
- If not cached, dynamically synthesizes a structured `.md` learning plan tailored to Role, Seniority, Team, Department, BU, and KB guidelines.
- Saves the markdown file to disk for instant future reuse.

### 4. Onboarding Plan Generator Agent (`backend/app/agents/plan_generator.py`)
- Standard 6-Phase Framework:
  * **Phase 1: Welcome & IT Access (Days 1–2 / Day 1)**
  * **Phase 2: Bearings & Team Alignment (Days 3–5 / Week 1)**
  * **Phase 3: Learning & Compliance (Days 6–29 / Month 1)**
  * **Phase 4: Hands Dirty & Mentored Execution (Days 30–50)**
  * **Phase 5: Ready to Own & Autonomy (Days 61–89)**
  * **Phase 6: Finish Line & 90-Day Review (Day 90)**
- Ingests tool access rules from `10_ROLE_TOOLS_ACCESS_MATRIX.md` (e.g. ServiceNow channel, Approver, SLA).
- Pairs reading assignments and training modules (`08_PHASE_3_...`, `06_COMMERCIAL...`).
- Generates structured JSON with actionable checklist items, KB links, and milestones.

### 5. Grounded Q&A Chatbot Agent (`backend/app/agents/qa_chatbot.py`)
- Ingests user query + joiner profile context.
- Retrieves most relevant KB chunks using RAG engine.
- If relevant context exists and answers the query: responds with clear, helpful answer and explicit citations.
- If relevant context is missing or low-confidence:
  * Politeness fallback: *"I'm sorry, I don't have information on that in our current company knowledge base. Please reach out directly to your manager for guidance on this."*
  * Saves the unanswered query to `missing_kb_queries.json` and database for HR/Admin visibility.

---

## 4. User Interface & Experience Specifications

### Admin / Manager Portal
- **New Joiner Onboarding Creator**:
  * Clean form with smart dropdowns / suggestions for Roles, Teams, Departments, and BUs.
  * "Generate AI Plan" action with live progress spinner.
- **Plan Preview & Live Editor**:
  * Edit task titles, descriptions, categories, tool access SLAs, and document links.
  * Add custom tasks or remove default ones before finalizing.
  * "Publish Plan" button to make it active for the new joiner.
- **Analytics & Management Dashboard**:
  * Summary cards: Total Joiners, Average Completion %, Active Plans, Pending Tool Requests.
  * Progress list of all joiners with visual progress bar, status pills, and last active timestamp.
- **Knowledge Base & Feedback Inspector**:
  * Live search and view of indexed KB documents.
  * Missing Information Feedback table with queries submitted by employees that lacked KB coverage, with options to mark as resolved (add to KB) or permanently delete.
- **Learning Plans Viewer**:
  * Markdown previewer and editor for stored `learning_plans/*.md`.

### New Joiner Portal
- **Phased Interactive Checklist**:
  * Visual phase tabs (Day 1 / Welcome, Week 1 / Bearings, Month 1 / Learning, 30-60-90 Days).
  * Interactive checkboxes that persist progress in real-time.
  * Category tags (IT Access, Reading, Training, Meeting, Deliverable) with color coding.
  * Tool Access drawer showing ServiceNow request path, required approvers, and SLA countdown.
- **Knowledge Base Document Viewer Modal**:
  * Clicking "View Source Doc" on any task opens an in-app viewer displaying the markdown file with the matching section highlighted.
- **Interactive Q&A Chatbot Widget**:
  * Chat panel with suggested quick questions ("What tools do I need on Day 1?", "Who is my EVP?", "What is V2G?", "What are our core operating principles?").
  * Grounded answers with clickable document badges.
  * Fallback notification when a question triggers manager escalation and feedback recording.
- **Quick Switcher**:
  * Top navigation bar allows instantly switching between Joiner and Manager views, or switching between test personas (Account Executive, Marketing Analyst, Product Owner, Tech Recruiter, Solar Project Manager, Graduate Trainee, and custom created employees).

---

## 5. Implementation Steps

### Phase 1: Knowledge Base Completion & Enrichment
- Enrich incomplete KB files (`01_ORG_STRUCTURE.md`, `04_ROLE_BASED_LEARNING.md`, `05_GO_TO_MARKET_STRUCTURE.md`, `07_GLOBAL_ONBOARDING_FRAMEWORK.md`, `08_PHASE_3_DEPARTMENTAL_CURRICULUM.md`) with comprehensive clean-tech enterprise organization, role tracks, curriculum codes, and frameworks consistent with existing files.

### Phase 2: Python Backend Development (`backend/`)
- Setup FastAPI project structure, dependencies (`fastapi`, `uvicorn`, `pydantic`, `sqlite3`, etc.).
- Build Document Parser & RAG Engine (`rag/indexer.py`, `rag/retriever.py`).
- Implement Specialist Agents (`agents/org_expert.py`, `agents/learning_expert.py`, `agents/plan_generator.py`, `agents/qa_chatbot.py`).
- Create SQLite persistence layer (`db/database.py`, `db/models.py`).
- Implement REST API routes (`/api/joiners`, `/api/plans`, `/api/tasks`, `/api/chat`, `/api/kb`, `/api/agents/learning-expert`, `/api/feedback`).
- Pre-seed database with default joiners matching the existing KB profiles.

### Phase 3: Modern React Frontend (`frontend/`)
- Initialize Vite + React + Tailwind CSS project with Lucide React icons.
- Build UI Components:
  * App Header & Persona Switcher
  * Admin / Manager Portal (New Joiner Form, AI Plan Review/Editor, Dashboard Analytics, Feedback Inspector, Learning Plan Viewer)
  * New Joiner Portal (Phased Checklist, Progress Bar, Tool Access Badges, KB Source Doc Viewer Modal, Grounded AI Chatbot)
- Connect Frontend to FastAPI backend via API client.

### Phase 4: Verification & End-to-End Testing
- Test RAG search against all KB documents.
- Test plan generation for existing roles and novel roles.
- Verify learning plans are generated and saved to `.md` files.
- Test Q&A Chatbot with grounded answers and citations.
- Test Q&A Chatbot with unanswerable questions to verify polite manager fallback and recording to `missing_kb_queries.json`.
- Test task checking and progress calculation.
- Test Admin edit and creation workflow.

### Phase 5: Production Containerization & Cloud Run Deployment
- Created multi-stage `Dockerfile`:
  * **Stage 1 (Node 20 Alpine)**: Compiles React + Vite frontend into optimized production bundle (`dist/`).
  * **Stage 2 (Python 3.11 Slim)**: Installs backend requirements, packages FastAPI server, and serves static files from `frontend/dist`.
- Updated `backend/app/main.py` with SPA fallback routing and `/assets` static mount.
- Configured `.dockerignore` for clean build context.
- Provisioned GCP Cloud Run service `onboarding-buddy` in region `europe-southwest1` (project `onboarding-agent-507110`).
- Enabled `--min-instances 1` and `--no-cpu-throttling` for 24/7 continuous operation.
- Verified live service endpoints (`/`, `/health`, `/docs`, `/api/joiners`).

---

## 6. Live Deployment & Endpoints

| Endpoint | URL | Status |
| :--- | :--- | :--- |
| **Web UI & Dashboard** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app](https://onboarding-buddy-517395366109.europe-southwest1.run.app) | `200 OK` (Active) |
| **Swagger OpenAPI Docs** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app/docs](https://onboarding-buddy-517395366109.europe-southwest1.run.app/docs) | `200 OK` (Active) |
| **Health Check** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app/health](https://onboarding-buddy-517395366109.europe-southwest1.run.app/health) | `200 OK` (`{"status":"healthy"}`) |
| **Joiners API** | [https://onboarding-buddy-517395366109.europe-southwest1.run.app/api/joiners](https://onboarding-buddy-517395366109.europe-southwest1.run.app/api/joiners) | `200 OK` (Active) |

---

## 7. Verification Plan & Results

### Automated Tests
- Unit test suite (`pytest backend/tests`): **12/12 Passed**
- End-to-end integration test (`python e2e_verification.py`): **All 7 Phases Passed**
- Cloud Run health & endpoint tests: **Verified 200 OK** on public HTTPS domain.

### Manual Verification Completed
- Tested manager joiner creation and AI preview.
- Tested task toggle and real-time progress calculations.
- Tested grounded chat queries and citation badge verification.
- Tested manager escalation and missing info logging.

