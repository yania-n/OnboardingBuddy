import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from ..db.models import ChatMessageRequest, ChatMessageResponse, Citation
from ..db.database import get_connection
from ..agents.qa_chatbot import qa_chatbot_agent

router = APIRouter(prefix="/api/chat", tags=["Q&A Chatbot"])

@router.post("", response_model=ChatMessageResponse)
def send_chat_message(req: ChatMessageRequest):
    """
    Handles incoming chat queries from users, retrieves their profile context,
    queries the grounded QA chatbot agent, records the message exchange to the
    chat history in the SQLite database, and returns the agent's response.
    Args:
        req (ChatMessageRequest): Request containing the user's ID and query.
    Returns:
        ChatMessageResponse: The chatbot response with grounded answers and citations.
    """
    user_name = None
    user_role = None
    context_bu = None
    user_team = None
    user_dept = None

    # Fetch user context/profile if user_id is provided
    if req.user_id:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (req.user_id,))
        user_row = cursor.fetchone()
        if user_row:
            user_name = user_row["name"]
            user_role = user_row["role"]
            context_bu = user_row["business_unit"]
            user_team = user_row["team"]
            user_dept = user_row["department"]
        conn.close()

    # Call Grounded QA Chatbot to obtain response
    response = qa_chatbot_agent.answer_question(
        query=req.query,
        user_id=req.user_id,
        user_name=user_name,
        user_role=user_role,
        context_bu=context_bu,
        user_team=user_team,
        user_dept=user_dept
    )

    # Persist message history in the database
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    # Save user message
    u_msg_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO chat_messages (id, user_id, role, content, citations, is_missing_info, created_at)
    VALUES (?, ?, 'user', ?, NULL, 0, ?)
    """, (u_msg_id, req.user_id, req.query, now))

    # Save assistant message
    a_msg_id = str(uuid.uuid4())
    citations_json = json.dumps([c.model_dump() for c in response.citations])
    cursor.execute("""
    INSERT INTO chat_messages (id, user_id, role, content, citations, is_missing_info, created_at)
    VALUES (?, ?, 'assistant', ?, ?, ?, ?)
    """, (a_msg_id, req.user_id, response.answer, citations_json, 1 if response.is_missing_info else 0, now))

    conn.commit()
    conn.close()

    return response

@router.get("/history/{user_id}")
def get_chat_history(user_id: str):
    """
    Retrieves the chronological chat history of the last 50 messages for a given user.
    Args:
        user_id (str): Unique identifier of the user.
    Returns:
        List[Dict]: List of user/assistant messages with timestamps and optional citations.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM chat_messages 
    WHERE user_id = ? 
    ORDER BY created_at ASC
    LIMIT 50
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    messages = []
    for r in rows:
        citations = []
        if r["citations"]:
            try:
                citations = json.loads(r["citations"])
            except Exception:
                citations = []
        messages.append({
            "id": r["id"],
            "role": r["role"],
            "content": r["content"],
            "citations": citations,
            "is_missing_info": bool(r["is_missing_info"]),
            "created_at": r["created_at"]
        })
    return messages

