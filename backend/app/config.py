import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
KB_DOCS_DIR = WORKSPACE_DIR / 'kb_docs'
DATA_DIR = BASE_DIR / 'data'
LEARNING_PLANS_DIR = DATA_DIR / 'learning_plans'
ORG_KNOWLEDGE_FILE = DATA_DIR / 'org_knowledge.json'
MISSING_QUERIES_FILE = DATA_DIR / 'missing_kb_queries.json'
DB_FILE = DATA_DIR / 'onboarding.db'

DATA_DIR.mkdir(parents=True, exist_ok=True)
LEARNING_PLANS_DIR.mkdir(parents=True, exist_ok=True)

# GCP Project and optional LLM keys
GCP_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', 'onboarding-agent-507110')
GCP_REGION = os.environ.get('GOOGLE_CLOUD_REGION', 'europe-southwest1')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')