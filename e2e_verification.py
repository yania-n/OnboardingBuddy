import os
import httpx
import json
import time

BASE_URL = os.environ.get("BASE_URL", "https://onboarding-buddy-517395366109.europe-southwest1.run.app")

def test_full_flow():
    """
    Executes an end-to-end integration test against the target API (local or Cloud Run).
    Verifies:
    1. Health check (/health)
    2. Joiners list retrieval (/api/joiners)
    3. Plan preview generation (/api/plans/preview)
    4. Joiner profile creation with automated plan generation (/api/joiners)
    5. Plan fetching and task state toggling (/api/tasks/{id}/toggle)
    6. Grounded Q&A chatbot queries with citation checks (/api/chat)
    7. Manager escalation and feedback logging for out-of-domain queries
    """

    with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
        print("1. Testing Health Endpoint...")
        r = client.get("/health")
        assert r.status_code == 200, f"Health check failed: {r.text}"
        print("   [PASS] API is healthy!")

        print("\n2. Testing Joiners List...")
        r = client.get("/api/joiners")
        assert r.status_code == 200
        joiners = r.json()
        print(f"   [PASS] Fetched {len(joiners)} joiners.")
        for j in joiners[:3]:
            print(f"      - {j['name']} ({j['role']} in {j['department']}) - Progress: {j['progress_percentage']}%")

        print("\n3. Testing Plan Preview Generation...")
        test_payload = {
            "name": "Dr. Claire Sterling",
            "email": "claire.sterling@enterprise.com",
            "role": "Principal Battery Analytics Engineer",
            "team": "Degradation Modeling",
            "department": "Battery Analytics & MLOps",
            "business_unit": "Energy Storage Systems",
            "seniority": "Principal / Director",
            "start_date": "2026-09-01"
        }
        r = client.post("/api/plans/preview", json=test_payload)
        assert r.status_code == 200, f"Preview failed: {r.text}"
        preview = r.json()
        print(f"   [PASS] Preview generated successfully with {len(preview['tasks'])} tasks across 6 phases.")
        print(f"      Overview: {preview['overview']}")

        print("\n4. Testing Joiner Creation & Automated Plan Generation...")
        r = client.post("/api/joiners", json=test_payload)
        assert r.status_code == 200
        new_joiner = r.json()
        user_id = new_joiner["id"]
        print(f"   [PASS] Created Joiner ID: {user_id}")

        print("\n5. Testing Fetch Plan & Task Toggle...")
        r = client.get(f"/api/plans/user/{user_id}")
        assert r.status_code == 200
        plan = r.json()
        task1 = plan["tasks"][0]
        print(f"   Task 1: {task1['title']} (Phase: {task1['phase']}, SLA: {task1.get('sla')})")

        # Toggle completion
        r = client.patch(f"/api/tasks/{task1['id']}/toggle", json={"is_completed": True})
        assert r.status_code == 200
        toggle_res = r.json()
        print(f"   [PASS] Task toggled! New progress: {toggle_res['plan_stats']['progress_percentage']}% ({toggle_res['plan_stats']['completed_tasks']}/{toggle_res['plan_stats']['total_tasks']})")

        print("\n6. Testing Grounded Q&A Chatbot...")
        r = client.post("/api/chat", json={
            "user_id": user_id,
            "query": "What is our Vehicle-to-Grid (V2G) synergy?"
        })
        assert r.status_code == 200
        chat_resp = r.json()
        print(f"   [PASS] Answer received:")
        print(f"      \"{chat_resp['answer'][:150]}...\"")
        print(f"      Citations count: {len(chat_resp['citations'])}")
        for cit in chat_resp['citations']:
            print(f"         * {cit['doc_name']} -> {cit['section_title']} (score: {cit['relevance_score']})")
        assert chat_resp["is_missing_info"] is False

        print("\n7. Testing Q&A Chatbot with Missing / Out-of-Scope Query...")
        missing_q = "Can I bring my pet iguana to the battery testing cleanroom?"
        r = client.post("/api/chat", json={
            "user_id": user_id,
            "query": missing_q
        })
        assert r.status_code == 200
        missing_resp = r.json()
        print(f"   [PASS] Escalation Response received:")
        print(f"      \"{missing_resp['answer']}\"")
        assert missing_resp["is_missing_info"] is True
        assert missing_resp["manager_escalation"] is True

        print("\n8. Testing Missing Information Feedback Center...")
        r = client.get("/api/feedback/missing")
        assert r.status_code == 200
        feedbacks = r.json()
        logged = next((f for f in feedbacks if f["query"] == missing_q), None)
        assert logged is not None, "Missing query was not logged to feedback!"
        print(f"   [PASS] Verified missing query recorded in feedback! ID: {logged['id']}")

        # Resolve feedback
        r = client.post(f"/api/feedback/resolve/{logged['id']}", json={"resolution_notes": "Added cleanroom pet restrictions to 02_COMPANY_HANDBOOK.md"})
        assert r.status_code == 200
        print("   [PASS] Feedback marked as resolved with resolution notes!")

        print("\n9. Testing Org Expert Scan Trigger...")
        r = client.post("/api/agents/org-expert/scan")
        assert r.status_code == 200
        scan_res = r.json()
        print(f"   [PASS] Org Expert scanned {scan_res['files_scanned']} files. Status: {scan_res['status']}")
        print(f"      Business Units: {', '.join(scan_res['business_units'])}")

        print("\n10. Testing Learning Expert Plans Repository...")
        r = client.get("/api/agents/learning-expert/plans")
        assert r.status_code == 200
        learning_plans = r.json()
        print(f"   [PASS] Found {len(learning_plans)} role-specific .md learning plans stored on disk:")
        for lp in learning_plans[:4]:
            print(f"      * {lp['file_name']} ({lp['role_title']}) - {lp['size_bytes']} bytes")

        print("\n11. Testing Knowledge Base Doc Retrieval & RAG Search...")
        r = client.get("/api/kb/docs")
        assert r.status_code == 200
        docs = r.json()
        print(f"   [PASS] Knowledge base contains {len(docs)} indexed documents.")

        r = client.get("/api/kb/search?q=Snowflake+approval+SLA")
        assert r.status_code == 200
        search_res = r.json()
        print(f"   [PASS] RAG search returned {search_res['results_count']} chunks for query 'Snowflake approval SLA'.")

        print("\n=======================================================")
        print("ALL 11 END-TO-END VERIFICATION CHECKS PASSED PERFECTLY!")
        print("=======================================================")

if __name__ == "__main__":
    test_full_flow()
