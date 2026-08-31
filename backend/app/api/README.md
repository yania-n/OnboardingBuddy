# API Endpoints & Routers

This module implements the FastAPI routes (APIRouter) exposing RESTful operations to the React frontend.

## API Routers

- **`joiners.py`**: Handles creation, listing, retrieval, and deletion of user onboarding profiles.
- **`plans.py`**: Fetches user-specific plans, serves dashboard statistics, generates plan previews, and handles bulk updates.
- **`tasks.py`**: Toggles task completion statuses, adds custom tasks to specific plans, and deletes tasks.
- **`chat.py`**: Receives chatbot queries, triggers the grounded QA chatbot agent, and fetches chat histories.
- **`agents.py`**: Manages specialist agents (Org Expert summary, scan requests, generated learning plans view and update).
- **`kb.py`**: Lists knowledge base documents and exposes the search lookup endpoint.
- **`feedback.py`**: Handles viewing, resolving, and deleting logs of unanswered queries in the Feedback Center.
