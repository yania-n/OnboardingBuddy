from typing import List
from fastapi import APIRouter, HTTPException
from ..db.models import MissingQueryItem, ResolveFeedbackRequest
from ..db.database import list_all_missing_feedback, resolve_missing_feedback, delete_missing_feedback

router = APIRouter(prefix="/api/feedback", tags=["System Feedback"])

@router.get("/missing", response_model=List[MissingQueryItem])
def get_all_missing_queries():
    """
    Fetches all missing information queries submitted by users that triggered a RAG fallback.
    Returns:
        List[MissingQueryItem]: A list of all logged missing information feedback items.
    """
    rows = list_all_missing_feedback()
    result = []
    for r in rows:
        result.append(MissingQueryItem(
            id=r["id"],
            user_id=r.get("user_id"),
            user_name=r.get("user_name"),
            user_role=r.get("user_role"),
            query=r["query"],
            context_bu=r.get("context_bu"),
            timestamp=r["timestamp"],
            status=r.get("status", "pending"),
            resolution_notes=r.get("resolution_notes")
        ))
    return result

@router.post("/resolve/{feedback_id}")
def resolve_feedback(feedback_id: str, req: ResolveFeedbackRequest):
    """
    Marks a pending missing feedback query as resolved and attaches resolution notes.
    Args:
        feedback_id (str): The unique ID of the feedback query to resolve.
        req (ResolveFeedbackRequest): Request body containing the resolution notes.
    """
    resolve_missing_feedback(feedback_id, req.resolution_notes or "Resolved by Admin")
    return {"message": "Feedback marked as resolved", "id": feedback_id}

@router.delete("/{feedback_id}")
def delete_feedback(feedback_id: str):
    """
    Permanently deletes a missing feedback query from SQLite and the JSON backup file.
    Args:
        feedback_id (str): The unique ID of the feedback query to delete.
    """
    delete_missing_feedback(feedback_id)
    return {"message": "Feedback query deleted successfully", "id": feedback_id}
