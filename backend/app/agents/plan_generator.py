import uuid
import re
from typing import List, Dict, Any
from ..db.models import TaskItem
from .org_expert import org_expert_agent
from .learning_expert import learning_expert_agent
from ..config import KB_DOCS_DIR

class OnboardingPlanGeneratorAgent:
    """
    Synthesizes tailored, multi-phase onboarding plans and task roadmaps for new hires
    by combining organization structure, software access matrices, and role curricula.
    """
    def __init__(self):
        """Initializes the Onboarding Plan Generator."""
        pass


    def _parse_role_tools_from_kb(self, role: str) -> List[Dict[str, str]]:
        """
        Parses the Markdown table in 10_ROLE_TOOLS_ACCESS_MATRIX.md from GCS or local disk
        to extract matching tools, purpose, provisioning channels, approvals, and SLAs for a role.
        Args:
            role (str): The target role name.
        Returns:
            List[dict]: List of matched tool access metadata dictionaries.
        """
        content = ""
        gcs_success = False
        try:
            from google.cloud import storage
            from ..config import GCP_PROJECT_ID
            client = storage.Client(project=GCP_PROJECT_ID)
            bucket_name = "onboarding-buddy-kb-2e1aa6a7"
            bucket = client.bucket(bucket_name)
            blob = bucket.blob("10_ROLE_TOOLS_ACCESS_MATRIX.md")
            if blob.exists():
                content = blob.download_as_text(encoding="utf-8")
                gcs_success = True
        except Exception as e:
            print(f"Error downloading tool matrix from GCS: {e}")

        if not gcs_success:
            matrix_file = KB_DOCS_DIR / "10_ROLE_TOOLS_ACCESS_MATRIX.md"
            if matrix_file.exists():
                try:
                    content = matrix_file.read_text(encoding="utf-8")
                except Exception as e:
                    print(f"Error reading local tool matrix: {e}")
                    return []
            else:
                return []

        if not content:
            return []

        try:
            lines = content.splitlines()
            
            # Find the table lines
            table_rows = []
            for line in lines:
                if line.strip().startswith("|"):
                    row = [cell.strip() for cell in line.split("|")[1:-1]]
                    table_rows.append(row)
                    
            if len(table_rows) < 3:
                return []
                
            # The table starts after the header and the separator line
            data_rows = table_rows[2:]
            
            matched_tools = []
            
            # Helper to match role
            def is_match(role_input: str, row_role: str) -> bool:
                r_in = role_input.lower().replace("–", "-").strip()
                r_row = row_role.lower().replace("–", "-").strip()
                r_in = re.sub(r"\(.*?\)", "", r_in).strip()
                r_row = re.sub(r"\(.*?\)", "", r_row).strip()
                
                # Check if either is a substring of the other
                if r_in in r_row or r_row in r_in:
                    return True
                    
                # Token matches for key keywords
                for kw in ["firmware", "sales", "recruiter", "solar", "trainee", "marketing", "product", "embedded", "mobility"]:
                    if kw in r_in and kw in r_row:
                        return True
                return False

            for row in data_rows:
                if len(row) >= 6:
                    row_role = row[0].replace("**", "").strip()
                    if is_match(role, row_role):
                        matched_tools.append({
                            "tool_name": row[1],
                            "purpose": row[2],
                            "channel": row[3],
                            "approvals": row[4],
                            "sla": row[5],
                            "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
                        })
            return matched_tools
        except Exception as e:
            print(f"Error parsing tool access matrix from KB: {e}")
            return []

    def _get_role_tools(self, role: str, department: str = "") -> List[Dict[str, str]]:
        """
        Gathers both baseline software tools and role-specific application access requirements.
        Args:
            role (str): Target role name.
            department (str): Assigned department.
        Returns:
            List[dict]: Complete list of tool access entries for Phase 1 provisioning.
        """
        role_lower = role.lower()
        tools = []

        # Baseline tools for all employees
        baseline = [

            {
                "tool_name": "Workday & Google Workspace / O365",
                "purpose": "Self-service HR, organizational charts, corporate email, and calendar.",
                "channel": "Auto-provisioned on Day 1 via SSO",
                "approvals": "Auto-Approved",
                "sla": "Immediate",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Day 1 Provisioning Baseline"
            },
            {
                "tool_name": "ServiceNow & Slack / Teams",
                "purpose": "IT Helpdesk ticketing, software requests, and internal team communication.",
                "channel": "Auto-provisioned on Day 1 via SSO",
                "approvals": "Auto-Approved",
                "sla": "Immediate",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Day 1 Provisioning Baseline"
            }
        ]
        tools.extend(baseline)

        # Try to parse from the KB document first
        kb_tools = self._parse_role_tools_from_kb(role)
        if kb_tools:
            tools.extend(kb_tools)
            return tools

        # Role-specific tools from 10_ROLE_TOOLS_ACCESS_MATRIX.md
        if "sales" in role_lower or "account executive" in role_lower:
            tools.append({
                "tool_name": "Salesforce / HubSpot CRM",
                "purpose": "Manage accounts, pipeline, opportunity stages, quotes, and contract redlines.",
                "channel": "Software Access > CRM > Role: Enterprise AE",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "Outreach & LinkedIn Sales Navigator",
                "purpose": "Outbound prospecting sequences, email tracking, and target account research.",
                "channel": "Software Access > Sales Enablement Suite",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        elif "marketing" in role_lower or "analyst" in role_lower:
            tools.append({
                "tool_name": "Snowflake / BigQuery Data Warehouse",
                "purpose": "Read-only access to campaign data, web analytics, and lead conversion tables.",
                "channel": "Data Platform Access > Snowflake > Schema: MKTG_ANALYTICS",
                "approvals": "Manager + Data Governance",
                "sla": "72 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "Looker / Tableau / GA4 Workspace",
                "purpose": "Authoring and consuming multi-channel attribution and CAC/LTV dashboards.",
                "channel": "Software Access > BI Workspace > Role: Content Creator",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        elif "product" in role_lower or "owner" in role_lower or "pm" in role_lower:
            tools.append({
                "tool_name": "Jira & Confluence",
                "purpose": "Product backlog refinement, epic tracking, user stories, and release notes.",
                "channel": "Software Access > Jira > Project: SW-PLATFORM > Role: PO",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "Telemetry Edge Admin (Read-Only)",
                "purpose": "Querying live fleet and energy storage vehicle edge telemetry logs for feature specs.",
                "channel": "Data Platform Access > Telemetry Portal (Read-Only)",
                "approvals": "Manager + Platform Lead",
                "sla": "48 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        elif "firmware" in role_lower or "embedded" in role_lower:
            tools.append({
                "tool_name": "GitLab Enterprise & CI/CD Pipelines",
                "purpose": "Access firmware repos, build pipelines, and MISRA C static analysis tools.",
                "channel": "Software Access > GitLab > Repo: firmware-core",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "SafeRTOS & HIL Testing Workbench",
                "purpose": "Local RTOS environment, Lauterbach/J-Link debuggers, and HIL test benches.",
                "channel": "Hardware Lab Access > Embedded SW Workbench",
                "approvals": "Manager + Lab Director",
                "sla": "48 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        elif "solar" in role_lower or "project manager" in role_lower:
            tools.append({
                "tool_name": "Procore & Primavera P6",
                "purpose": "EPC submittal reviews, construction schedules, RFIs, and site milestones.",
                "channel": "Software Access > Construction Operations > Procore",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "SAP S/4HANA (Operations & Costing)",
                "purpose": "PO processing, vendor invoicing, material tracking, and project budget actuals.",
                "channel": "Finance & ERP Systems > SAP > Role: Project Costing",
                "approvals": "Manager + Finance Director",
                "sla": "48 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        elif "recruiter" in role_lower or "talent" in role_lower:
            tools.append({
                "tool_name": "Greenhouse / Lever ATS",
                "purpose": "Candidate pipeline management, requisition posting, and interview scheduling.",
                "channel": "Software Access > HR Systems > ATS > Role: Recruiter",
                "approvals": "TA Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "LinkedIn Recruiter & SeekOut Licenses",
                "purpose": "Sourcing candidates across hardware, firmware, and software engineering domains.",
                "channel": "Software Access > Talent Sourcing Licenses",
                "approvals": "TA Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        elif "trainee" in role_lower or "graduate" in role_lower:
            tools.append({
                "tool_name": "NexoraLearn LMS & Rotational Portal",
                "purpose": "Access mandatory foundation modules, rotation evaluations, and learning tracks.",
                "channel": "Provisioned Automatically on Day 1",
                "approvals": "Auto-Approved",
                "sla": "Immediate",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
            tools.append({
                "tool_name": "Cross-BU Sandbox Repos & CAD Viewers",
                "purpose": "Read-only access to cross-BU engineering repos, CAD models, and CRM views.",
                "channel": "Software Access > Early Careers Sandbox Access",
                "approvals": "Program Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })
        else:
            tools.append({
                "tool_name": f"{role} Core Workspace & Repository",
                "purpose": "Primary workspace, ticketing, and collaboration environment.",
                "channel": f"Software Access > {department or 'General'} > Role: Contributor",
                "approvals": "Direct Manager",
                "sla": "24 Hours",
                "ref": "10_ROLE_TOOLS_ACCESS_MATRIX.md#Role-Based Software & System Access Matrix"
            })

        return tools

    def generate_plan(
        self,
        role: str,
        team: str,
        department: str,
        business_unit: str,
        seniority: str = "Mid-Level",
        name: str = "New Joiner"
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive 6-phase onboarding roadmap for a new hire.
        Combines org context, learning curriculum, role-specific tools, and compliance gates.
        Args:
            role (str): Job role / title of the new hire.
            team (str): Assigned team.
            department (str): Assigned department.
            business_unit (str): Assigned business unit.
            seniority (str): Seniority level (e.g. 'Senior', 'Lead', 'Mid-Level', 'Entry-Level').
            name (str): Full name of the new hire.
        Returns:
            dict: Dictionary with 'overview', 'tasks' (list of TaskItem objects), and 'stats'.
        """
        # Step 1: Consult Org Expert Agent
        org_context = org_expert_agent.get_role_context(role, business_unit, department)

        role_info = org_context["role_info"]
        org_brief = org_expert_agent.generate_org_brief(
            name=name,
            role=role,
            team=team,
            department=department,
            business_unit=business_unit,
            seniority=seniority
        )

        # Step 2: Consult Learning Expert Agent
        learning_plan = learning_expert_agent.get_or_create_learning_plan(
            role=role,
            seniority=seniority,
            team=team,
            department=department,
            business_unit=business_unit,
            name=name
        )

        # Step 3: Extract tools and access items
        role_tools = self._get_role_tools(role, department)

        # Step 4: Construct Standardized 6-Phase Tasks
        tasks: List[TaskItem] = []
        order = 1

        # --- PHASE 1: Welcome (Days 1–2 / Day 1) ---
        for tool in role_tools:
            tasks.append(TaskItem(
                phase="Phase 1: Welcome (Days 1–2)",
                title=f"Setup & Verify {tool['tool_name']}",
                description=f"{tool['purpose']}. Submit/verify access via ServiceNow ({tool['channel']}). Required Approvals: {tool['approvals']} (SLA: {tool['sla']}).",
                category="access_setup",
                tool_name=tool["tool_name"],
                provisioning_channel=tool["channel"],
                required_approvals=tool["approvals"],
                sla=tool["sla"],
                kb_doc_reference=tool["ref"],
                order_index=order
            ))
            order += 1

        tasks.append(TaskItem(
            phase="Phase 1: Welcome (Days 1–2)",
            title="Complete Mandatory Security (SEC-101) & Ethics (CMP-101) Modules",
            description="Complete self-paced enterprise compliance modules: Enterprise Cybersecurity & Zero-Trust Architecture (SEC-101) and Global Code of Conduct (CMP-101) on the LMS portal.",
            category="training",
            kb_doc_reference="08_PHASE_3_DEPARTMENTAL_CURRICULUM.md#Mandatory Enterprise Foundations (All Employees)",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 1: Welcome (Days 1–2)",
            title="Meet Assigned Onboarding Buddy",
            description="Conduct initial welcome sync with your assigned Onboarding Buddy. Set up recurring weekly check-ins and review communication channels.",
            category="meeting",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Onboarding Buddy Program",
            order_index=order
        ))
        order += 1

        # --- PHASE 2: Bearings (Days 3–5 / Week 1) ---
        tasks.append(TaskItem(
            phase="Phase 2: Bearings (Days 3–5)",
            title=f"Conduct 1-on-1 Alignment Meeting with Manager ({role_info['reports_to']})",
            description=f"Meet with your manager to align on 90-day objectives, team OKRs, reporting cadence, and review the customized onboarding roadmap.",
            category="meeting",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 2: Bearings (Days 3–5)",
            title="Review Company Handbook & Cross-BU Synergies",
            description="Read the Company Mission, Vision, and Core Operating Principles. Study the Cross-BU Strategy Map connecting Solar, Storage, and Electric Mobility.",
            category="reading",
            kb_doc_reference="02_COMPANY_HANDBOOK.md#Mission, Vision, and Core Operating Principles",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 2: Bearings (Days 3–5)",
            title="Complete Data Governance (DATA-101) & Safety (EHS-101)",
            description="Complete Data Privacy Governance & IP Protection (DATA-101) and Workplace Safety & Hazard Control (EHS-101) modules.",
            category="training",
            kb_doc_reference="08_PHASE_3_DEPARTMENTAL_CURRICULUM.md#Mandatory Enterprise Foundations (All Employees)",
            order_index=order
        ))
        order += 1

        # --- PHASE 3: Learning (Days 6–29 / Month 1) ---
        tasks.append(TaskItem(
            phase="Phase 3: Learning (Days 6–29)",
            title=f"Complete Role Role Learning Curriculum ({learning_plan['role_slug']})",
            description=f"Execute the structured role learning plan drafted by the Learning Expert Agent. Review modules and labs stored in {learning_plan['source_file']}.",
            category="training",
            kb_doc_reference=f"backend/data/learning_plans/{learning_plan['source_file']}",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 3: Learning (Days 6–29)",
            title="Shadow Senior Peers & Review Team Rituals",
            description=f"Shadow at least 3 critical operational cycles in {team or department} (e.g., discovery calls, sprint ceremonies, architecture reviews, or site syncs).",
            category="reading",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 3: Learning (Days 6–29)",
            title="Pass Phase 3 Competency Gate Assessment",
            description="Achieve 100% score on role certification exam or practical scenario evaluation reviewed by direct manager.",
            category="deliverable",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        # --- PHASE 4: Hands Dirty (Days 30–50) ---
        tasks.append(TaskItem(
            phase="Phase 4: Hands Dirty (Days 30–50)",
            title="Deliver First Scoped Workstream / Project Deliverable",
            description=f"Execute an initial production deliverable (e.g., sprint user story, customer pitch, candidate intake, or site submittal review) with mentor guidance.",
            category="deliverable",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 4: Hands Dirty (Days 30–50)",
            title="Conduct Mid-Point 45-Day Alignment Check-in",
            description="Review sprint velocity, project milestones, and feedback with direct manager and buddy.",
            category="meeting",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        # --- PHASE 5: Ready to Own (Days 61–89) ---
        tasks.append(TaskItem(
            phase="Phase 5: Ready to Own (Days 61–89)",
            title="Lead Independent Workstream Execution",
            description=f"Take autonomous ownership of primary responsibilities within {department or team}. Interface directly with cross-functional stakeholders.",
            category="deliverable",
            kb_doc_reference="03_ROLES_RESPONSIBILITIES.md#Detailed Role Taxonomy",
            order_index=order
        ))
        order += 1

        # --- PHASE 6: Finish Line & Feedback (Day 90) ---
        tasks.append(TaskItem(
            phase="Phase 6: Finish Line (Day 90)",
            title="Conduct Final 90-Day Performance Review",
            description=f"Formal alignment with {role_info['reports_to']}. Review achievements against 90-day roadmap and transition off onboarding track.",
            category="meeting",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        tasks.append(TaskItem(
            phase="Phase 6: Finish Line (Day 90)",
            title="Submit 90-Day Employee Onboarding Experience Survey",
            description="Complete and submit the mandatory 90-Day Onboarding Experience Survey to provide feedback on tools, mentoring, and curriculum.",
            category="deliverable",
            kb_doc_reference="07_GLOBAL_ONBOARDING_FRAMEWORK.md#Enterprise 6-Phase Onboarding Architecture",
            order_index=order
        ))
        order += 1

        overview = org_brief


        return {
            "overview": overview,
            "tasks": tasks,
            "role_info": role_info,
            "learning_plan_file": learning_plan["source_file"],
            "learning_plan_reused": learning_plan["is_reused"]
        }

# Singleton instance
plan_generator_agent = OnboardingPlanGeneratorAgent()
