# Database & Models Module

This module handles data persistence and schema definition for the OnboardingBuddy backend application.

## Components

- **`database.py`**:
  - Implements helper functions to connect to the SQLite database (`backend/data/onboarding.db`).
  - Contains database tables initialization routines (`init_db`).
  - Implements CRUD operations for new hires (users), onboarding plans, tasks, chat logs, and missing queries.
  - Syncs missing queries logs with a JSON backup file (`backend/data/missing_kb_queries.json`).

- **`models.py`**:
  - Defines the request and response Pydantic models for data validation.
  - Ensures clean schema contract mappings between the FastAPI routers and React client.
