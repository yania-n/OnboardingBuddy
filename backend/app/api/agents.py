from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from ..db.models import OrgScanResult, LearningPlanResponse, LearningPlanUpdate
from ..agents.org_expert import org_expert_agent
from ..agents.learning_expert import learning_expert_agent

router = APIRouter(prefix="/api/agents", tags=["Specialist Agents"])

# --- ORG EXPERT ENDPOINTS ---

# --- ORG EXPERT ENDPOINTS ---

@router.get("/org-expert/summary")
def get_org_expert_summary():
    """
    Retrieves the parsed summary of the organizational structure (Business Units,
    Departments, Teams, Roles) mapping.
    """
    return org_expert_agent.get_org_summary()

@router.post("/org-expert/brief")
def generate_org_expert_brief(payload: Dict[str, Any]):
    """
    Generates a personalized markdown organizational brief containing team context,
    who's who, culture info, and alignment for a user.
    """
    name = payload.get("name", "New Joiner")
    role = payload.get("role", "Software Engineer")
    team = payload.get("team", "")
    department = payload.get("department", "")
    business_unit = payload.get("business_unit", "")
    seniority = payload.get("seniority", "Mid-Level")
    
    brief = org_expert_agent.generate_org_brief(
        name=name,
        role=role,
        team=team,
        department=department,
        business_unit=business_unit,
        seniority=seniority
    )
    return {"brief": brief}

@router.post("/org-expert/scan", response_model=OrgScanResult)
def scan_org_knowledge_base():
    """
    Triggers the Org Expert Agent to scan kb_docs, detect any structural changes,
    and persist the updated org model.
    """
    result = org_expert_agent.scan_knowledge_base(force=True)
    return OrgScanResult(
        last_scanned_at=result["last_scanned_at"],
        files_scanned=result["files_scanned"],
        business_units=result["business_units"],
        departments=result["departments"],
        roles_count=result["roles_count"],
        changes_detected=result["changes_detected"],
        status=result["status"],
        org_graph=result["org_graph"]
    )

# --- LEARNING EXPERT ENDPOINTS ---

@router.get("/learning-expert/plans")
def list_learning_plans():
    """
    Lists the metadata of all cached role-based learning plans.
    """
    return learning_expert_agent.list_all_learning_plans()

@router.get("/learning-expert/plans/{role_slug}")
def get_learning_plan(role_slug: str):
    """
    Retrieves the raw markdown content of a specific role-based learning plan.
    Args:
        role_slug (str): Slugified role name.
    """
    content = learning_expert_agent.get_plan_by_slug(role_slug)
    if content is None:
        raise HTTPException(status_code=404, detail="Learning plan not found")
    return {
        "role_slug": role_slug,
        "markdown_content": content
    }

@router.put("/learning-expert/plans/{role_slug}")
def update_learning_plan(role_slug: str, update_in: LearningPlanUpdate):
    """
    Updates the raw markdown content of a role-based learning plan.
    Args:
        role_slug (str): Slugified role name.
        update_in (LearningPlanUpdate): The update payload containing markdown.
    """
    success = learning_expert_agent.update_learning_plan(role_slug, update_in.markdown_content)
    return {"message": "Learning plan updated successfully", "role_slug": role_slug}

@router.post("/learning-expert/generate", response_model=LearningPlanResponse)
def generate_role_learning_plan(payload: Dict[str, Any]):
    """
    Generates or retrieves a cached personalized 30-60-90 Day learning plan
    for a user's role and metadata.
    """
    role = payload.get("role", "Software Engineer")
    seniority = payload.get("seniority", "Mid-Level")
    team = payload.get("team", "")
    department = payload.get("department", "")
    business_unit = payload.get("business_unit", "")
    name = payload.get("name", "New Joiner")

    result = learning_expert_agent.get_or_create_learning_plan(
        role=role,
        seniority=seniority,
        team=team,
        department=department,
        business_unit=business_unit,
        name=name
    )
    return LearningPlanResponse(
        role=result["role"],
        role_slug=result["role_slug"],
        source_file=result["source_file"],
        is_reused=result["is_reused"],
        markdown_content=result["markdown_content"],
        created_at=result["created_at"]
    )

