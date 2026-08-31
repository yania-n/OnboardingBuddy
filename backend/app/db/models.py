from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class JoinerCreate(BaseModel):
    name: str
    email: str
    role: str
    team: str
    department: str
    business_unit: str
    seniority: Optional[str] = 'Mid-Level'
    start_date: Optional[str] = None

class JoinerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    team: Optional[str] = None
    department: Optional[str] = None
    business_unit: Optional[str] = None
    seniority: Optional[str] = None
    start_date: Optional[str] = None
    status: Optional[str] = None

class JoinerResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    team: str
    department: str
    business_unit: str
    seniority: str
    start_date: str
    status: str
    created_at: str
    updated_at: str
    progress_percentage: Optional[float] = 0.0
    total_tasks: Optional[int] = 0
    completed_tasks: Optional[int] = 0

class TaskItem(BaseModel):
    id: Optional[str] = None
    plan_id: Optional[str] = None
    phase: str
    title: str
    description: str
    category: str  # 'access_setup' | 'reading' | 'training' | 'meeting' | 'deliverable'
    tool_name: Optional[str] = None
    provisioning_channel: Optional[str] = None
    required_approvals: Optional[str] = None
    sla: Optional[str] = None
    kb_doc_reference: Optional[str] = None
    is_completed: bool = False
    completed_at: Optional[str] = None
    order_index: int = 0

class TaskToggleRequest(BaseModel):
    is_completed: bool

class PlanCreateOrUpdate(BaseModel):
    overview: str
    tasks: List[TaskItem]

class PlanResponse(BaseModel):
    id: str
    user_id: str
    status: str  # 'draft' | 'published'
    overview: str
    tasks: List[TaskItem]
    created_at: str
    updated_at: str
    stats: Optional[Dict[str, Any]] = None

class ChatMessageRequest(BaseModel):
    user_id: Optional[str] = None
    query: str
    conversation_id: Optional[str] = None

class Citation(BaseModel):
    doc_name: str
    section_title: str
    excerpt: str
    relevance_score: float

class ChatMessageResponse(BaseModel):
    answer: str
    citations: List[Citation] = []
    is_missing_info: bool = False
    manager_escalation: bool = False
    context_role: Optional[str] = None

class MissingQueryItem(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    query: str
    context_bu: Optional[str] = None
    timestamp: str
    status: str  # 'pending' | 'resolved'
    resolution_notes: Optional[str] = None

class ResolveFeedbackRequest(BaseModel):
    resolution_notes: Optional[str] = 'Resolved by admin'

class OrgScanResult(BaseModel):
    last_scanned_at: str
    files_scanned: int
    business_units: List[str]
    departments: List[str]
    roles_count: int
    changes_detected: List[str]
    status: str
    org_graph: Optional[Dict[str, Any]] = None

class LearningPlanResponse(BaseModel):
    role: str
    role_slug: str
    source_file: str
    is_reused: bool
    markdown_content: str
    created_at: str

class LearningPlanUpdate(BaseModel):
    markdown_content: str