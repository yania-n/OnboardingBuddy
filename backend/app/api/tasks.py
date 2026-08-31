import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..db.models import TaskItem, TaskToggleRequest
from ..db.database import get_connection

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.patch("/{task_id}/toggle")
def toggle_task(task_id: str, req: TaskToggleRequest):
    """
    Toggles the is_completed state of a specific onboarding task.
    Also updates completed_at timestamp and returns updated stats for the plan.
    Args:
        task_id (str): Unique identifier of the task.
        req (TaskToggleRequest): Request body containing the new completion state.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM onboarding_tasks WHERE id = ?", (task_id,))
    task_row = cursor.fetchone()
    if not task_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    new_val = 1 if req.is_completed else 0
    now = datetime.now().isoformat() if req.is_completed else None

    cursor.execute("UPDATE onboarding_tasks SET is_completed = ?, completed_at = ? WHERE id = ?", (new_val, now, task_id))
    conn.commit()

    # Recalculate plan stats
    plan_id = task_row["plan_id"]
    cursor.execute("""
    SELECT 
        COUNT(id) as total_tasks,
        SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_tasks
    FROM onboarding_tasks
    WHERE plan_id = ?
    """, (plan_id,))
    stat = cursor.fetchone()
    total = stat["total_tasks"] or 0
    completed = stat["completed_tasks"] or 0
    pct = round((completed / total) * 100, 1) if total > 0 else 0.0

    conn.close()
    return {
        "task_id": task_id,
        "is_completed": req.is_completed,
        "completed_at": now,
        "plan_stats": {
            "total_tasks": total,
            "completed_tasks": completed,
            "progress_percentage": pct
        }
    }

@router.post("/plan/{plan_id}", response_model=TaskItem)
def add_task(plan_id: str, task_in: TaskItem):
    """
    Adds a new custom onboarding task manually to a specific plan.
    Args:
        plan_id (str): The unique identifier of the onboarding plan.
        task_in (TaskItem): Task details to be added.
    """
    conn = get_connection()
    cursor = conn.cursor()

    task_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO onboarding_tasks (id, plan_id, phase, title, description, category, tool_name, provisioning_channel, required_approvals, sla, kb_doc_reference, is_completed, order_index)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        task_id, plan_id, task_in.phase, task_in.title, task_in.description,
        task_in.category, task_in.tool_name, task_in.provisioning_channel,
        task_in.required_approvals, task_in.sla, task_in.kb_doc_reference, task_in.order_index
    ))
    conn.commit()
    conn.close()

    task_in.id = task_id
    task_in.plan_id = plan_id
    return task_in

@router.delete("/{task_id}")
def delete_task(task_id: str):
    """
    Deletes an onboarding task from a plan.
    Args:
        task_id (str): Unique identifier of the task to delete.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM onboarding_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Task deleted successfully"}

