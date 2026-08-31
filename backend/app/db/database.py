import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..config import DB_FILE, DATA_DIR, MISSING_QUERIES_FILE

def get_connection():
    """
    Establishes and returns a connection to the SQLite database.
    Creates parent directories for the database file if they do not exist.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the SQLite database by creating all required tables if they don't exist:
    - users: profiles of onboarded employees
    - onboarding_plans: personalized plan metadata
    - onboarding_tasks: tasks matching the phased roadmap framework
    - chat_messages: history of chatbot conversation logs
    - missing_information_feedback: log of unanswered queries for managers to resolve
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        team TEXT NOT NULL,
        department TEXT NOT NULL,
        business_unit TEXT NOT NULL,
        seniority TEXT DEFAULT 'Mid-Level',
        start_date TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Create onboarding plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS onboarding_plans (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        status TEXT DEFAULT 'published',
        overview TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # Create onboarding tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS onboarding_tasks (
        id TEXT PRIMARY KEY,
        plan_id TEXT NOT NULL,
        phase TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT NOT NULL,
        tool_name TEXT,
        provisioning_channel TEXT,
        required_approvals TEXT,
        sla TEXT,
        kb_doc_reference TEXT,
        is_completed INTEGER DEFAULT 0,
        completed_at TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (plan_id) REFERENCES onboarding_plans(id) ON DELETE CASCADE
    )
    """)

    # Create chat messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        citations TEXT,
        is_missing_info INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # Create missing feedback queries log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS missing_information_feedback (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        user_name TEXT,
        user_role TEXT,
        query TEXT NOT NULL,
        context_bu TEXT,
        timestamp TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        resolution_notes TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_missing_feedback(query: str, user_id: Optional[str] = None, user_name: Optional[str] = None, user_role: Optional[str] = None, context_bu: Optional[str] = None):
    """
    Saves an unanswered/escalated query to the missing feedback logs (both SQLite database
    and the backup missing_kb_queries.json file) for admin/manager visibility.
    """
    conn = get_connection()
    cursor = conn.cursor()
    feedback_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Persist in SQLite
    cursor.execute("""
    INSERT INTO missing_information_feedback (id, user_id, user_name, user_role, query, context_bu, timestamp, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (feedback_id, user_id, user_name, user_role, query, context_bu, now))
    conn.commit()
    conn.close()

    # Append to the JSON file backup
    try:
        entries = []
        if MISSING_QUERIES_FILE.exists():
            with open(MISSING_QUERIES_FILE, 'r', encoding='utf-8') as f:
                try:
                    entries = json.load(f)
                except Exception:
                    entries = []
        entries.append({
            'id': feedback_id,
            'user_id': user_id,
            'user_name': user_name,
            'user_role': user_role,
            'query': query,
            'context_bu': context_bu,
            'timestamp': now,
            'status': 'pending'
        })
        with open(MISSING_QUERIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2)
    except Exception as e:
        print(f"Error writing missing queries file: {e}")

    return feedback_id

def list_all_missing_feedback():
    """
    Retrieves all missing feedback entries from the SQLite database, ordered by latest first.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM missing_information_feedback ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def resolve_missing_feedback(feedback_id: str, resolution_notes: str = 'Resolved by admin'):
    """
    Updates the status of a missing feedback entry to 'resolved' and adds resolution notes
    in both the SQLite database and the JSON file backup.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE missing_information_feedback
    SET status = 'resolved', resolution_notes = ?
    WHERE id = ?
    """, (resolution_notes, feedback_id))
    conn.commit()
    conn.close()

    try:
        if MISSING_QUERIES_FILE.exists():
            with open(MISSING_QUERIES_FILE, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            for item in entries:
                if item.get('id') == feedback_id:
                    item['status'] = 'resolved'
                    item['resolution_notes'] = resolution_notes
            with open(MISSING_QUERIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2)
    except Exception as e:
        print(f"Error updating missing queries JSON file: {e}")

def delete_missing_feedback(feedback_id: str):
    """
    Permanently deletes a missing feedback entry from the SQLite database
    and the backup JSON file.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM missing_information_feedback
    WHERE id = ?
    """, (feedback_id,))
    conn.commit()
    conn.close()

    try:
        if MISSING_QUERIES_FILE.exists():
            with open(MISSING_QUERIES_FILE, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            # Filter out the matching feedback ID
            entries = [item for item in entries if item.get('id') != feedback_id]
            with open(MISSING_QUERIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(entries, f, indent=2)
    except Exception as e:
        print(f"Error deleting query from JSON file: {e}")
