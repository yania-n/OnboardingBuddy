import uuid
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from ..db.models import PlanResponse, PlanCreateOrUpdate, TaskItem, JoinerCreate
from ..db.database import get_connection
from ..agents.plan_generator import plan_generator_agent

router = APIRouter(prefix="/api/plans", tags=["Onboarding Plans"])

@router.get("/user/{user_id}", response_model=PlanResponse)
def get_user_plan(user_id: str):
    """
    Retrieves the onboarding plan and tasks roadmap for a specific user.
    Calculates progress stats (total, completed, percentage).
    Args:
        user_id (str): Unique identifier of the user/joiner.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM onboarding_plans WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,))
    plan_row = cursor.fetchone()
    if not plan_row:
        conn.close()
        raise HTTPException(status_code=404, detail="No onboarding plan found for this user")

    plan_id = plan_row["id"]
    cursor.execute("SELECT * FROM onboarding_tasks WHERE plan_id = ? ORDER BY order_index ASC, id ASC", (plan_id,))
    task_rows = cursor.fetchall()

    tasks = []
    completed_count = 0
    for tr in task_rows:
        is_comp = bool(tr["is_completed"])
        if is_comp:
            completed_count += 1
        tasks.append(TaskItem(
            id=tr["id"],
            plan_id=tr["plan_id"],
            phase=tr["phase"],
            title=tr["title"],
            description=tr["description"] or "",
            category=tr["category"],
            tool_name=tr["tool_name"],
            provisioning_channel=tr["provisioning_channel"],
            required_approvals=tr["required_approvals"],
            sla=tr["sla"],
            kb_doc_reference=tr["kb_doc_reference"],
            is_completed=is_comp,
            completed_at=tr["completed_at"],
            order_index=tr["order_index"]
        ))

    total = len(tasks)
    pct = round((completed_count / total) * 100, 1) if total > 0 else 0.0

    stats = {
        "total_tasks": total,
        "completed_tasks": completed_count,
        "progress_percentage": pct
    }

    conn.close()
    return PlanResponse(
        id=plan_id,
        user_id=user_id,
        status=plan_row["status"],
        overview=plan_row["overview"] or "",
        tasks=tasks,
        created_at=plan_row["created_at"],
        updated_at=plan_row["updated_at"],
        stats=stats
    )

@router.post("/preview")
def preview_plan(joiner: JoinerCreate):
    """
    Simulates the AI plan generation flow and returns a preview of the phased onboarding
    tasks without persisting them.
    Args:
        joiner (JoinerCreate): Profile options for generating the plan preview.
    """
    plan_data = plan_generator_agent.generate_plan(
        role=joiner.role,
        team=joiner.team,
        department=joiner.department,
        business_unit=joiner.business_unit,
        seniority=joiner.seniority or "Mid-Level",
        name=joiner.name
    )
    return plan_data

@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: str, plan_update: PlanCreateOrUpdate):
    """
    Updates the general overview and overwrites/re-creates the onboarding tasks
    for a given plan.
    Args:
        plan_id (str): The unique identifier of the plan to update.
        plan_update (PlanCreateOrUpdate): Plan overview and list of new/updated tasks.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM onboarding_plans WHERE id = ?", (plan_id,))
    plan_row = cursor.fetchone()
    if not plan_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Plan not found")

    now = datetime.now().isoformat()
    cursor.execute("UPDATE onboarding_plans SET overview = ?, updated_at = ? WHERE id = ?", (plan_update.overview, now, plan_id))

    # Replace tasks with updated list
    cursor.execute("DELETE FROM onboarding_tasks WHERE plan_id = ?", (plan_id,))
    for idx, t in enumerate(plan_update.tasks, start=1):
        t_id = t.id or str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO onboarding_tasks (id, plan_id, phase, title, description, category, tool_name, provisioning_channel, required_approvals, sla, kb_doc_reference, is_completed, completed_at, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            t_id, plan_id, t.phase, t.title, t.description, t.category,
            t.tool_name, t.provisioning_channel, t.required_approvals,
            t.sla, t.kb_doc_reference, 1 if t.is_completed else 0,
            t.completed_at, idx
        ))

    conn.commit()
    conn.close()
    return get_user_plan(plan_row["user_id"])

@router.get("/dashboard/stats")
def get_dashboard_stats():
    """
    Aggregates global analytics metrics across all new hires and plans for the
    Manager Dashboard (active plans count, overall average completion pct, BU distribution).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as active FROM users WHERE status = 'active'")
    active_users = cursor.fetchone()["active"]

    cursor.execute("SELECT COUNT(*) as total, SUM(is_completed) as completed FROM onboarding_tasks")
    task_stat = cursor.fetchone()
    total_tasks = task_stat["total"] or 0
    completed_tasks = task_stat["completed"] or 0
    avg_progress = round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0

    cursor.execute("SELECT business_unit, COUNT(*) as count FROM users GROUP BY business_unit")
    bu_dist = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_joiners": total_users,
        "active_plans": active_users,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "average_progress_pct": avg_progress,
        "bu_distribution": bu_dist
    }

