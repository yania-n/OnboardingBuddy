import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from ..db.models import JoinerCreate, JoinerUpdate, JoinerResponse
from ..db.database import get_connection
from ..agents.plan_generator import plan_generator_agent

router = APIRouter(prefix="/api/joiners", tags=["Joiners"])

def _calculate_user_stats(user_id: str, conn):
    """
    Calculates progress metrics for a user's onboarding plan, including:
    - total_tasks: the total number of tasks assigned.
    - completed_tasks: the number of completed tasks.
    - pct: progress percentage rounded to 1 decimal place.
    Args:
        user_id (str): Unique identifier of the user.
        conn: Open SQLite connection object.
    Returns:
        tuple (total, completed, pct): Calculated progress stats.
    """
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        COUNT(t.id) as total_tasks,
        SUM(CASE WHEN t.is_completed = 1 THEN 1 ELSE 0 END) as completed_tasks
    FROM onboarding_plans p
    LEFT JOIN onboarding_tasks t ON t.plan_id = p.id
    WHERE p.user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    total = row["total_tasks"] or 0
    completed = row["completed_tasks"] or 0
    pct = round((completed / total) * 100, 1) if total > 0 else 0.0
    return total, completed, pct

@router.get("", response_model=List[JoinerResponse])
def get_all_joiners():
    """
    Retrieves all joiners (new hire profiles) from the users database, calculates their
    current onboarding progress percentages, and returns the compiled list.
    Returns:
        List[JoinerResponse]: List of all joiner details with statistics.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    result = []
    for r in rows:
        total, completed, pct = _calculate_user_stats(r["id"], conn)
        result.append(JoinerResponse(
            id=r["id"],
            name=r["name"],
            email=r["email"],
            role=r["role"],
            team=r["team"],
            department=r["department"],
            business_unit=r["business_unit"],
            seniority=r["seniority"] or "Mid-Level",
            start_date=r["start_date"],
            status=r["status"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            progress_percentage=pct,
            total_tasks=total,
            completed_tasks=completed
        ))
    conn.close()
    return result

@router.get("/{user_id}", response_model=JoinerResponse)
def get_joiner(user_id: str):
    """
    Retrieves profiling data and progress statistics for a single joiner.
    Args:
        user_id (str): The unique identifier of the joiner.
    Returns:
        JoinerResponse: Detailed profile of the requested joiner.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Joiner not found")

    total, completed, pct = _calculate_user_stats(user_id, conn)
    res = JoinerResponse(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        role=row["role"],
        team=row["team"],
        department=row["department"],
        business_unit=row["business_unit"],
        seniority=row["seniority"] or "Mid-Level",
        start_date=row["start_date"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        progress_percentage=pct,
        total_tasks=total,
        completed_tasks=completed
    )
    conn.close()
    return res

@router.post("", response_model=JoinerResponse)
def create_joiner(joiner_in: JoinerCreate):
    """
    Creates a new user profile (joiner), automatically triggers the AI Plan Generator Agent
    to draft a personalized, phased onboarding tasks list, saves the user and tasks
    to the SQLite database, and returns the response.
    Args:
        joiner_in (JoinerCreate): The payload containing details of the new hire.
    """
    conn = get_connection()
    cursor = conn.cursor()
    user_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    start_date = joiner_in.start_date or datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO users (id, name, email, role, team, department, business_unit, seniority, start_date, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """, (
        user_id, joiner_in.name, joiner_in.email, joiner_in.role,
        joiner_in.team, joiner_in.department, joiner_in.business_unit,
        joiner_in.seniority or "Mid-Level", start_date, now, now
    ))

    # Automatically generate default onboarding plan based on role/metadata
    plan_data = plan_generator_agent.generate_plan(
        role=joiner_in.role,
        team=joiner_in.team,
        department=joiner_in.department,
        business_unit=joiner_in.business_unit,
        seniority=joiner_in.seniority or "Mid-Level",
        name=joiner_in.name
    )

    plan_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO onboarding_plans (id, user_id, status, overview, created_at, updated_at)
    VALUES (?, ?, 'published', ?, ?, ?)
    """, (plan_id, user_id, plan_data["overview"], now, now))

    for task in plan_data["tasks"]:
        t_id = str(uuid.uuid4())
        cursor.execute("""
        INSERT INTO onboarding_tasks (id, plan_id, phase, title, description, category, tool_name, provisioning_channel, required_approvals, sla, kb_doc_reference, is_completed, order_index)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            t_id, plan_id, task.phase, task.title, task.description,
            task.category, task.tool_name, task.provisioning_channel,
            task.required_approvals, task.sla, task.kb_doc_reference, task.order_index
        ))

    conn.commit()
    conn.close()

    return JoinerResponse(
        id=user_id,
        name=joiner_in.name,
        email=joiner_in.email,
        role=joiner_in.role,
        team=joiner_in.team,
        department=joiner_in.department,
        business_unit=joiner_in.business_unit,
        seniority=joiner_in.seniority or "Mid-Level",
        start_date=start_date,
        status="active",
        created_at=now,
        updated_at=now,
        progress_percentage=0.0,
        total_tasks=len(plan_data["tasks"]),
        completed_tasks=0
    )

@router.delete("/{user_id}")
def delete_joiner(user_id: str):
    """
    Permanently deletes a joiner from the SQLite database. ON DELETE CASCADE will trigger
    automatic deletion of their onboarding plan and associated tasks.
    Args:
        user_id (str): Unique identifier of the user to delete.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Joiner deleted successfully"}

