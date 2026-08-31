import uuid
from datetime import datetime
from app.db.database import get_connection, init_db
from app.agents.plan_generator import plan_generator_agent
from app.agents.org_expert import org_expert_agent

SAMPLE_JOINERS = [
    {
        "name": "Maya Lin",
        "email": "maya.lin@enterprise.com",
        "role": "Account Executive",
        "team": "Enterprise Fleet Sales",
        "department": "Global Commercial Operations",
        "business_unit": "Central Commercial / Cross-BU",
        "seniority": "Senior",
        "start_date": "2026-08-15"
    },
    {
        "name": "Alex Rivera",
        "email": "alex.rivera@enterprise.com",
        "role": "Marketing Analyst",
        "team": "Growth & Demand Gen",
        "department": "Global Commercial Operations",
        "business_unit": "Central Commercial / Cross-BU",
        "seniority": "Mid-Level",
        "start_date": "2026-08-20"
    },
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@enterprise.com",
        "role": "Product Owner",
        "team": "Vehicle Telematics & Edge",
        "department": "Vehicle Software / Energy Systems Product Management",
        "business_unit": "Electric Mobility",
        "seniority": "Senior",
        "start_date": "2026-08-01"
    },
    {
        "name": "David Kim",
        "email": "david.kim@enterprise.com",
        "role": "Tech Recruiter",
        "team": "Hardware & Firmware Talent",
        "department": "Global Talent Acquisition & HR",
        "business_unit": "Central Platforms & Corporate Operations",
        "seniority": "Mid-Level",
        "start_date": "2026-08-10"
    },
    {
        "name": "Marcus Vance",
        "email": "marcus.vance@enterprise.com",
        "role": "Project Manager – Solar Energy Systems",
        "team": "Utility Solar EPC Delivery",
        "department": "Solar Project Management & Delivery",
        "business_unit": "Solar Energy Systems",
        "seniority": "Lead",
        "start_date": "2026-07-28"
    },
    {
        "name": "Elena Rostova",
        "email": "elena.rostova@enterprise.com",
        "role": "Graduate Trainee",
        "team": "Rotational Cohort 2026",
        "department": "Global Early Careers Program",
        "business_unit": "Rotational Across BUs",
        "seniority": "Entry-Level / Trainee",
        "start_date": "2026-08-25"
    }
]

def seed_database():
    """
    Seeds the SQLite database with initial realistic sample joiners, plans, and tasks
    if the database is currently empty.
    """
    init_db()
    org_expert_agent.scan_knowledge_base()


    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM users")
    count = cursor.fetchone()["count"]

    if count > 0:
        print(f"Database already contains {count} joiners. Skipping seed.")
        conn.close()
        return

    print("Seeding initial realistic joiners and onboarding roadmaps...")
    now = datetime.now().isoformat()

    for idx, sj in enumerate(SAMPLE_JOINERS):
        user_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO users (id, name, email, role, team, department, business_unit, seniority, start_date, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
        """, (
            user_id, sj["name"], sj["email"], sj["role"], sj["team"],
            sj["department"], sj["business_unit"], sj["seniority"],
            sj["start_date"], now, now
        ))

        plan_data = plan_generator_agent.generate_plan(
            role=sj["role"],
            team=sj["team"],
            department=sj["department"],
            business_unit=sj["business_unit"],
            seniority=sj["seniority"],
            name=sj["name"]
        )

        plan_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO onboarding_plans (id, user_id, status, overview, created_at, updated_at)
        VALUES (?, ?, 'published', ?, ?, ?)
        """, (plan_id, user_id, plan_data["overview"], now, now))

        for t_idx, task in enumerate(plan_data["tasks"], start=1):
            t_id = str(uuid.uuid4())
            # For realism, mark first 2-3 tasks completed for earlier start dates
            is_comp = 1 if (idx % 2 == 0 and t_idx <= 3) or (idx == 4 and t_idx <= 6) else 0
            comp_time = now if is_comp else None

            cursor.execute("""
            INSERT INTO onboarding_tasks (id, plan_id, phase, title, description, category, tool_name, provisioning_channel, required_approvals, sla, kb_doc_reference, is_completed, completed_at, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t_id, plan_id, task.phase, task.title, task.description,
                task.category, task.tool_name, task.provisioning_channel,
                task.required_approvals, task.sla, task.kb_doc_reference,
                is_comp, comp_time, t_idx
            ))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
