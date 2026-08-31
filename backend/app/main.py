from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .db.database import init_db
from .rag.indexer import rag_engine
from .agents.org_expert import org_expert_agent
from .api import joiners, plans, tasks, chat, agents, kb, feedback

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the startup and shutdown lifecycle events of the FastAPI application.
    Performs database initialization, indexes documents in the Knowledge Base,
    initializes the organizational model, and seeds sample data.
    """
    # Startup: initialize database, RAG index, and org knowledge
    init_db()
    rag_engine.build_index()
    org_expert_agent.load_or_initialize()

    # Automatically seed sample data if empty
    from seed import seed_database
    seed_database()

    yield
    # Shutdown

app = FastAPI(
    title="OnboardingBuddy AI Platform API",
    description="Enterprise AI-Powered Personalized Onboarding Roadmap and Grounded Q&A Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(joiners.router)
app.include_router(plans.router)
app.include_router(tasks.router)
app.include_router(chat.router)
app.include_router(agents.router)
app.include_router(kb.router)
app.include_router(feedback.router)

@app.get("/health")
def health():
    """
    Exposes a lightweight health-check endpoint for Cloud Run and system uptime monitors.
    Returns:
        dict: System health status {"status": "healthy"}.
    """
    return {"status": "healthy"}

# Mount frontend static build if present
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if not FRONTEND_DIST.exists():
    FRONTEND_DIST = Path("frontend/dist").resolve()

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    if (FRONTEND_DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Serves the Single Page Application (SPA) compiled assets or falls back to index.html
        for client-side routing, while preserving 404s for unmatched API or documentation routes.
        Args:
            full_path (str): The requested URL path.
        Returns:
            FileResponse: The requested static file or frontend index.html fallback.
        """
        if full_path.startswith("api/") or full_path == "api" or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = FRONTEND_DIST / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/")
    def root():
        """
        Returns general application details and status when running without compiled frontend assets.
        Returns:
            dict: API metadata, document count, and online status.
        """
        return {
            "app": "OnboardingBuddy AI API",
            "status": "online",
            "docs_count": len(rag_engine.chunks),
            "version": "1.0.0"
        }



