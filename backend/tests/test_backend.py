import pytest
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.database import init_db, list_all_missing_feedback, resolve_missing_feedback
from app.rag.indexer import rag_engine
from app.agents.org_expert import org_expert_agent
from app.agents.learning_expert import learning_expert_agent, slugify
from app.agents.plan_generator import plan_generator_agent
from app.agents.qa_chatbot import qa_chatbot_agent
from fastapi.testclient import TestClient
from app.main import app
from seed import seed_database

@pytest.fixture(autouse=True)
def setup_test_env():
    init_db()
    rag_engine.build_index()
    org_expert_agent.scan_knowledge_base(force=True)
    seed_database()

def test_rag_indexer():
    assert len(rag_engine.chunks) > 0
    results = rag_engine.search("Salesforce CRM access", top_k=3)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert "10_ROLE_TOOLS_ACCESS_MATRIX.md" in top_chunk.doc_name or "09A" in top_chunk.doc_name or "06" in top_chunk.doc_name

def test_org_expert_agent():
    summary = org_expert_agent.get_org_summary()
    assert "business_units" in summary
    assert "Electric Mobility" in summary["business_units"]
    assert "Solar Energy Systems" in summary["business_units"]
    assert "Energy Storage Systems" in summary["business_units"]

    # Test answering org query
    ans = org_expert_agent.answer_org_query("Who is the CEO?")
    assert ans is not None
    assert "Chief Executive Officer" in ans

    # Test Hugging Face inspired methods
    chunks = org_expert_agent.get_org_context_chunks(
        role="Account Executive",
        team="Enterprise Fleet Sales",
        department="Global Commercial Operations",
        business_unit="Central Commercial / Cross-BU"
    )
    assert len(chunks) > 0
    assert "source" in chunks[0]

    depts = org_expert_agent.suggest_departments()
    assert "Global Commercial Operations" in depts

    teams = org_expert_agent.suggest_teams_for_dept("Global Commercial Operations")
    assert len(teams) > 0

    roles = org_expert_agent.suggest_roles_for_team("Enterprise Fleet Sales")
    assert len(roles) > 0

    # Test generating org brief
    brief = org_expert_agent.generate_org_brief(
        name="Maya Lin",
        role="Account Executive",
        team="Enterprise Fleet Sales",
        department="Global Commercial Operations",
        business_unit="Central Commercial / Cross-BU",
        seniority="Senior"
    )
    assert "## Your Team" in brief
    assert "## Where You Fit" in brief
    assert "## Key People to Know" in brief
    assert "## Culture Highlights" in brief

def test_learning_expert_agent():
    # Test generation for a new role
    role = "Novel Battery Thermal Specialist"
    slug = slugify(role)
    test_file = learning_expert_agent.storage_dir / f"{slug}.md"
    if test_file.exists():
        test_file.unlink()

    result = learning_expert_agent.get_or_create_learning_plan(
        role=role,
        seniority="Senior",
        team="Battery Pack Cooling",
        department="Powertrain & Hardware Engineering",
        business_unit="Electric Mobility"
    )
    assert result["role_slug"] == slug
    assert result["is_reused"] is False
    assert test_file.exists()

    # Second call should reuse existing plan
    reuse_result = learning_expert_agent.get_or_create_learning_plan(role=role)
    assert reuse_result["is_reused"] is True

def test_plan_generator_agent():
    plan = plan_generator_agent.generate_plan(
        role="Product Owner",
        team="Vehicle Telematics",
        department="Vehicle Software",
        business_unit="Electric Mobility",
        seniority="Senior",
        name="Test Joiner"
    )
    assert len(plan["tasks"]) >= 10
    phases = set(t.phase for t in plan["tasks"])
    assert "Phase 1: Welcome (Days 1–2)" in phases
    assert "Phase 2: Bearings (Days 3–5)" in phases
    assert "Phase 3: Learning (Days 6–29)" in phases
    assert "Phase 6: Finish Line (Day 90)" in phases

    # Verify tool task details
    jira_task = next((t for t in plan["tasks"] if "Jira" in t.title), None)
    assert jira_task is not None
    assert jira_task.sla == "24 Hours"
    assert jira_task.required_approvals == "Direct Manager"

def test_qa_chatbot_grounded_answer():
    # Grounded query
    res = qa_chatbot_agent.answer_question(
        query="What is the mission of the company?",
        user_role="Product Owner"
    )
    assert res.is_missing_info is False
    assert res.manager_escalation is False
    assert len(res.citations) > 0
    assert "decarbonization" in res.answer.lower() or "mission" in res.answer.lower()

def test_qa_chatbot_missing_fallback_and_feedback_logging():
    # Ungrounded / missing query
    missing_query = "What is the policy on taking personal pets to the testing facility?"
    res = qa_chatbot_agent.answer_question(
        query=missing_query,
        user_id="test-user-123",
        user_name="John Doe",
        user_role="Embedded Firmware Engineer",
        context_bu="Electric Mobility"
    )
    assert res.is_missing_info is True
    assert res.manager_escalation is True
    assert "reach out directly to your manager" in res.answer

    # Verify it was persisted to missing feedback log
    feedbacks = list_all_missing_feedback()
    logged = next((f for f in feedbacks if f["query"] == missing_query), None)
    assert logged is not None
    assert logged["status"] == "pending"

def test_api_endpoints():
    with TestClient(app) as client:
        # 1. Health check
        r = client.get("/health")
        assert r.status_code == 200

        # 2. List joiners
        r = client.get("/api/joiners")
        assert r.status_code == 200
        joiners = r.json()
        assert len(joiners) > 0
        first_id = joiners[0]["id"]

        # 3. Get plan for joiner
        r = client.get(f"/api/plans/user/{first_id}")
        assert r.status_code == 200
        plan = r.json()
        assert len(plan["tasks"]) > 0

        # 4. Toggle task
        first_task = plan["tasks"][0]
        r = client.patch(f"/api/tasks/{first_task['id']}/toggle", json={"is_completed": True})
        assert r.status_code == 200
        assert r.json()["is_completed"] is True

        # 5. Send Chat message
        r = client.post("/api/chat", json={"user_id": first_id, "query": "What tools do I need on Day 1?"})
        assert r.status_code == 200
        assert "ServiceNow" in r.json()["answer"] or "Workday" in r.json()["answer"] or "SSO" in r.json()["answer"]

        # 6. Trigger Org Scan
        r = client.post("/api/agents/org-expert/scan")
        assert r.status_code == 200
        assert r.json()["status"] in ["up-to-date", "updated"]

        # 7. List Learning Plans
        r = client.get("/api/agents/learning-expert/plans")
        assert r.status_code == 200
        assert len(r.json()) > 0

        # 8. Generate Org Brief
        r = client.post("/api/agents/org-expert/brief", json={
            "name": "Maya Lin",
            "role": "Account Executive",
            "team": "Enterprise Fleet Sales",
            "department": "Global Commercial Operations",
            "business_unit": "Central Commercial / Cross-BU",
            "seniority": "Senior"
        })
        assert r.status_code == 200
        brief_data = r.json()
        assert "brief" in brief_data
        assert "## Your Team" in brief_data["brief"]
        assert "## Where You Fit" in brief_data["brief"]
        assert "## Key People to Know" in brief_data["brief"]
        assert "## Culture Highlights" in brief_data["brief"]

def test_feedback_resolve_and_delete():
    # 1. Add some feedback
    from app.db.database import save_missing_feedback
    f_id = save_missing_feedback("Test feedback delete query", "user-456", "Test User", "Developer", "Digital Services")

    # 2. Verify it is logged
    feedbacks = list_all_missing_feedback()
    logged = next((f for f in feedbacks if f["id"] == f_id), None)
    assert logged is not None

    with TestClient(app) as client:
        # 3. Resolve it
        r = client.post(f"/api/feedback/resolve/{f_id}", json={"resolution_notes": "Resolved for testing"})
        assert r.status_code == 200

        # Verify resolution
        feedbacks = list_all_missing_feedback()
        logged = next((f for f in feedbacks if f["id"] == f_id), None)
        assert logged["status"] == "resolved"
        assert logged["resolution_notes"] == "Resolved for testing"

        # 4. Delete it
        r = client.delete(f"/api/feedback/{f_id}")
        assert r.status_code == 200

        # Verify it's gone
        feedbacks = list_all_missing_feedback()
        logged = next((f for f in feedbacks if f["id"] == f_id), None)
        assert logged is None

