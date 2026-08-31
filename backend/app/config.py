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

# GCP Project, Region, LLM Model and API keys
GCP_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT', 'onboarding-agent-507110')
GCP_REGION = os.environ.get('GOOGLE_CLOUD_REGION', 'europe-southwest1')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.6-flash')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

def call_gemini_generate(genai_client, prompt: str):
    """
    Attempts content generation using the primary GEMINI_MODEL (defaults to gemini-3.6-flash).
    If the requested model is not found in the target GCP region, automatically falls back
    to available Flash models in order: gemini-3.6-flash -> gemini-3.5-flash -> gemini-2.5-flash -> gemini-2.0-flash -> gemini-1.5-flash.
    """
    models_to_try = [GEMINI_MODEL, "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    seen = set()
    unique_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

    last_error = None
    for model_name in unique_models:
        try:
            response = genai_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "404" in err_str or "not_found" in err_str or "not found" in err_str:
                continue
            else:
                print(f"GenAI call error for model {model_name}: {e}")
                break
    if last_error:
        print(f"All GenAI model fallbacks attempted. Last status: {last_error}")
    return None
