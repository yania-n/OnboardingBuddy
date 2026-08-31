import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..config import LEARNING_PLANS_DIR, GCP_PROJECT_ID, GEMINI_MODEL
from ..rag.indexer import rag_engine


def slugify(text: str) -> str:
    """
    Normalizes a role title into an alphanumeric kebab-case slug (e.g., 'Account Executive' -> 'account-executive').
    Args:
        text (str): Input string.
    Returns:
        str: Slugified string.
    """
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)

class LearningExpertAgent:
    """
    Synthesizes and manages role-based 30-60-90 day learning plans.
    Persists curriculum as Markdown documents with local disk caching and AI generation.
    """
    def __init__(self, storage_dir: Path = LEARNING_PLANS_DIR):
        """
        Initializes the Learning Expert Agent and ensures the storage directory exists.
        Args:
            storage_dir (Path): Local directory where role learning plan markdown files are saved.
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._init_genai_client()

    def _init_genai_client(self):
        """
        Initializes the Vertex AI / Gemini client with default Google Cloud credentials.
        """
        self.genai_client = None
        try:
            from google import genai
            # Use Vertex AI backend with default credentials
            self.genai_client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT_ID,
                location=os.environ.get("GOOGLE_CLOUD_LOCATION", "europe-southwest1")
            )
        except Exception as e:
            print(f"GenAI Client init info (Learning Expert): {e}")

    def _get_plan_path(self, role: str) -> Path:
        """
        Calculates the file path for a role's markdown learning plan.
        Args:
            role (str): Role name.
        Returns:
            Path: Path to the corresponding markdown file.
        """
        slug = slugify(role)
        return self.storage_dir / f"{slug}.md"

    def get_or_create_learning_plan(
        self,
        role: str,
        seniority: str = "Mid-Level",
        team: str = "",
        department: str = "",
        business_unit: str = "",
        name: str = "New Joiner"
    ) -> Dict[str, Any]:
        """
        Retrieves a cached role learning plan or generates a new one based on KB documents.
        Args:
            role (str): Job title / role of the employee.
            seniority (str): Seniority level (e.g. 'Senior', 'Lead', 'Mid-Level').
            team (str): Assigned team.
            department (str): Assigned department.
            business_unit (str): Assigned business unit.
            name (str): Employee name.
        Returns:
            dict: Learning plan metadata and markdown content.
        """
        slug = slugify(role)
        plan_file = self._get_plan_path(role)


        if plan_file.exists():
            content = plan_file.read_text(encoding="utf-8")
            return {
                "role": role,
                "role_slug": slug,
                "source_file": plan_file.name,
                "is_reused": True,
                "markdown_content": content,
                "created_at": datetime.fromtimestamp(plan_file.stat().st_mtime).isoformat()
            }

        # Synthesize a new role-specific learning plan based on KB and parameters
        generated_md = self._generate_learning_plan_md(role, seniority, team, department, business_unit, name)
        plan_file.write_text(generated_md, encoding="utf-8")

        return {
            "role": role,
            "role_slug": slug,
            "source_file": plan_file.name,
            "is_reused": False,
            "markdown_content": generated_md,
            "created_at": datetime.now().isoformat()
        }

    def _generate_learning_plan_md(
        self,
        role: str,
        seniority: str,
        team: str,
        department: str,
        business_unit: str,
        name: str = "New Joiner"
    ) -> str:
        role_lower = role.lower()
        bu_name = business_unit or "Clean Energy Ecosystem"
        dept_name = department or "Engineering & Operations"

        # Try generating via Gemini first if client is available
        if self.genai_client:
            try:
                # Queries targeting compliance, tools, and role-specific learning
                queries = [
                    "mandatory compliance training GDPR security code of conduct EHS-101 SEC-101 DATA-101",
                    f"{role} {department} learning path training modules curriculum",
                    f"{role} tools access matrix onboarding guides",
                ]
                seen = set()
                all_chunks = []
                for query in queries:
                    for chunk, score in rag_engine.search(query, top_k=3):
                        key = f"{chunk.doc_name}:{chunk.section_title}"
                        if key not in seen:
                            seen.add(key)
                            all_chunks.append(chunk)

                # Format the context chunks
                context_blocks = []
                for chunk in all_chunks[:10]:
                    context_blocks.append(f"--- Document: {chunk.doc_name} ({chunk.section_title}) ---\n{chunk.content}")
                combined_context = "\n\n".join(context_blocks)

                prompt = f"""You are OnboardingBuddy's Learning Expert Agent for our clean energy enterprise.
Build a personalized, comprehensive, and structured learning/training plan for a new joiner based on their role, seniority, department, and team.

New Joiner Details:
- Name: {name}
- Role: {role}
- Seniority: {seniority}
- Department: {dept_name}
- Business Unit: {bu_name}
- Team: {team or 'Core Team'}

Use ONLY the knowledge base context provided below to extract courses, modules, codes (like SEC-101, CMP-101, DATA-101, EHS-101, MISRA-C-101, GTM-PITCH-101, etc.), training details, and timeline rules. Do not invent any modules, course names, or links that do not exist in the context.

Write all descriptions, targets, and milestones in simple, clear, and direct English. Avoid overly complex technical jargon, bureaucratic terminology, or dense phrasing.

Structure your output EXACTLY as the markdown format below (do not include any additional commentary outside the requested markdown structure):

# Learning Plan: {role} ({seniority})

## Metadata & Alignment
* **Role:** {role}
* **Seniority:** {seniority}
* **Team:** {team or 'Core Team'}
* **Department:** {dept_name}
* **Business Unit:** {bu_name}
* **Curriculum Framework:** [Identify/name the training track, e.g. Embedded Systems Track, Enterprise GTM Track, etc., based on the context]
* **Prepared For:** {name}
* **Generated By:** Learning Expert Agent (Grounded in Enterprise KB)

---

## 1. Executive Objective
[Provide a clear, brief objective (1-2 sentences) of this plan tailored to the role, department, and business unit.]

---

## 2. Mandatory Foundation & Domain Modules
[List the mandatory company-wide and role-specific training modules found in the context that they must complete. Format each as a bullet point. Include the module code, title, delivery format, and completion timeline if available in the context (e.g., * `SEC-101: Enterprise Cybersecurity & Zero-Trust Architecture` (Day 2)).]

---

## 3. Phased 30-Day Competency Milestones
[List weekly target milestones for Week 1, Week 2, Week 3, and Week 4, describing what they should target or pass, grounded strictly in the context.]

---

## 4. Practical Hands-On Labs & Shadowing
[List practical tasks, buddy pairings, shadowing sessions, or sandbox setups they must do, grounded in the context.]

---

## 5. Certification & Sign-off Gate
[Specify the completion criteria and sign-off rules for this learning path, grounded in the context.]

Knowledge Base Context:
{combined_context}
"""
                response = self.genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt
                )

                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"GenAI learning plan generation fallback: {e}")

        # Search RAG for role-specific curriculum and modules
        search_results = rag_engine.search(f"{role} learning curriculum training modules", top_k=3)
        rag_context = "\n".join([chunk.content for chunk, _ in search_results])

        # Determine curriculum tracks
        if "sales" in role_lower or "account executive" in role_lower or "commercial" in role_lower:
            track_name = "Enterprise Commercial & GTM Sales Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Phishing Defense` (Day 2)",
                "* `CMP-101: Global Code of Conduct, Ethics & Anti-Corruption` (Day 2)",
                "* `GTM-PITCH-101: Cross-BU Ecosystem Value Proposition & ROI Modeling` (Week 2)",
                "* `GTM-TECH-201: Technical RFP Response Frameworks & Utility Grid Rules` (Week 3)"
            ]
            milestones = [
                "**Week 1 Target:** Pass Enterprise Foundation & Security Certifications; master CRM (Salesforce/HubSpot).",
                "**Week 2 Target:** Shadow 5 AE discovery calls and review competitive battlecards.",
                "**Week 3 Target:** Shadow 3 Solutions Engineer technical demos and lead 1 live opportunity stage update.",
                "**Week 4 Completion Gate:** Deliver live competitive mock pitch to VP of Sales with 100% certification pass."
            ]
        elif "marketing" in role_lower or "analyst" in role_lower:
            track_name = "Commercial Analytics & Growth Marketing Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Phishing Defense` (Day 2)",
                "* `CMP-101: Global Code of Conduct & Corporate Ethics` (Day 2)",
                "* `DATA-101: Data Privacy Governance, GDPR/CCPA & IP Protection` (Week 1)",
                "* `GTM-PITCH-101: Cross-BU Ecosystem Value Proposition & ROI Modeling` (Week 2)"
            ]
            milestones = [
                "**Week 1 Target:** Verify Snowflake/BigQuery and BI workspace credentials; complete security training.",
                "**Week 2 Target:** Map lead-to-opportunity attribution models and audit GA4/CRM pipeline sync.",
                "**Week 3 Target:** Build automated MQL-to-SQL conversion velocity dashboard.",
                "**Week 4 Completion Gate:** Pass Marketing Data Architecture review and deploy 1 production BI dashboard."
            ]
        elif "product" in role_lower or "owner" in role_lower or "pm" in role_lower:
            track_name = "Systems Product Management & Agile Platform Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Zero-Trust Architecture` (Day 2)",
                "* `CMP-101: Global Code of Conduct & Corporate Ethics` (Day 2)",
                "* `PM-FRAME-101: Cross-BU Synergy Integration Roadmap Design` (Week 2)",
                "* `PM-DATA-201: Telemetry-Driven Feature Prioritization & System Metrics` (Week 3)"
            ]
            milestones = [
                "**Week 1 Target:** Setup Jira, Confluence, Figma; attend standing squad ceremonies as observer.",
                "**Week 2 Target:** Review product vision, epics, and Definition of Ready (DoR) / Definition of Done (DoD).",
                "**Week 3 Target:** Draft 3 production-ready user stories meeting full DoR criteria.",
                "**Week 4 Completion Gate:** Lead 1 full sprint cycle backlog refinement session with Product Lead."
            ]
        elif "firmware" in role_lower or "embedded" in role_lower:
            track_name = "Embedded Systems & High-Voltage Safety Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Zero-Trust Architecture` (Day 2)",
                "* `EHS-101: Workplace Safety & High-Voltage Hazard Control` (Day 3)",
                "* `HW-SAFE-201: ISO 26262 Functional Safety & Lockout/Tagout Protocols` (Week 2)",
                "* `MISRA-C-101: Automotive & Industrial MISRA C:2012 Coding Standards` (Week 3)",
                "* `FW-RTOS-301: Deterministic Real-Time Operating Systems & Debugging` (Week 4)"
            ]
            milestones = [
                "**Week 1 Target:** Setup GitLab, SafeRTOS, Lauterbach debugger, and pass EHS high-voltage safety lab.",
                "**Week 2 Target:** Complete CANoe telemetry bus sniffing and local build environment verification.",
                "**Week 3 Target:** Implement low-level peripheral driver with 100% MISRA C compliance.",
                "**Week 4 Completion Gate:** Successfully flash and execute hardware-in-the-loop (HIL) automated test suite."
            ]
        elif "solar" in role_lower or "project manager" in role_lower:
            track_name = "Solar Project Delivery & EPC Governance Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Phishing Defense` (Day 2)",
                "* `EHS-101: High-Voltage Electrical & Site Safety Sign-off` (Day 3)",
                "* `OPS-SUPPLY-101: Global Procurement Protocols & Material Logistics` (Week 2)",
                "* `HW-SAFE-201: ISO/UL Safety Standards & Grid Interconnection Compliance` (Week 3)"
            ]
            milestones = [
                "**Week 1 Target:** Setup Procore, Primavera P6, SAP S/4HANA; complete site PPE clearance.",
                "**Week 2 Target:** Review regional utility interconnection rules (IEEE 1547) and EPC contract frameworks.",
                "**Week 3 Target:** Shadow Senior PM on 2 active commercial solar site inspections and vendor reviews.",
                "**Week 4 Completion Gate:** Lead 1 equipment delivery or milestone gate review with zero schedule deviations."
            ]
        elif "recruiter" in role_lower or "talent" in role_lower:
            track_name = "Technical Talent Acquisition & Sourcing Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Phishing Defense` (Day 2)",
                "* `CMP-101: Global Code of Conduct & Anti-Corruption` (Day 2)",
                "* `DATA-101: Data Privacy Governance & Candidate Data Ethics` (Week 1)",
                "* Structured Technical Interview & Bias Mitigation Training (Week 2)"
            ]
            milestones = [
                "**Week 1 Target:** Configure ATS (Greenhouse/Lever) and sourcing licenses (LinkedIn Recruiter, SeekOut).",
                "**Week 2 Target:** Audit technical role taxonomies and build specialized Boolean search matrices.",
                "**Week 3 Target:** Shadow 5 technical intake syncs with hiring managers and conduct 5 phone screens.",
                "**Week 4 Completion Gate:** Pass Technical Sourcing Certification and independently lead candidate intake call."
            ]
        elif "trainee" in role_lower or "graduate" in role_lower or "apprentice" in role_lower:
            track_name = "Early Careers Multi-Rotational Foundation Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Phishing Defense` (Day 2)",
                "* `CMP-101: Global Code of Conduct, Ethics & Anti-Corruption` (Day 2)",
                "* `EHS-101: Workplace Safety & High-Voltage Lab Access` (Day 3)",
                "* `PM-FRAME-101` & `GTM-PITCH-101: Cross-BU Synergy Foundations` (Weeks 2–3)"
            ]
            milestones = [
                "**Month 1 Target:** Master enterprise foundations, setup sandbox development tools, sign Learning Agreement.",
                "**Month 2–3 Target (Rotation 1):** Scoped engineering/operations placement in primary BU with mentor sign-off.",
                "**Month 4–5 Target (Rotation 2):** Cross-BU secondary placement driving multi-domain integration project.",
                "**Month 6 Completion Gate:** Deliver Executive Capstone Presentation and transition to permanent role."
            ]
        else:
            track_name = f"{role} Specialized Professional Learning Track"
            core_modules = [
                "* `SEC-101: Enterprise Cybersecurity & Phishing Defense` (Day 2)",
                "* `CMP-101: Global Code of Conduct & Corporate Ethics` (Day 2)",
                "* `DATA-101: Data Privacy Governance & Information Security` (Week 1)",
                f"* Domain Foundations for {dept_name} & {bu_name} (Weeks 2–3)"
            ]
            milestones = [
                "**Week 1 Target:** Complete enterprise IT setup, single sign-on verification, and meet assigned Onboarding Buddy.",
                "**Week 2 Target:** Conduct 1-on-1 manager alignment and map departmental workflows.",
                "**Week 3 Target:** Complete core role-specific modules and shadow senior team members.",
                "**Week 4 Completion Gate:** Successfully deliver first mentored sprint milestone / project deliverable."
            ]

        modules_text = "\n".join(core_modules)
        milestones_text = "\n".join([f"* {m}" for m in milestones])

        return f"""# Learning Plan: {role} ({seniority})

## Metadata & Alignment
* **Role:** {role}
* **Seniority:** {seniority}
* **Team:** {team or 'Core Team'}
* **Department:** {dept_name}
* **Business Unit:** {bu_name}
* **Curriculum Framework:** {track_name}
* **Prepared For:** {name}
* **Generated By:** Learning Expert Agent (Grounded in Enterprise KB)

---

## 1. Executive Objective
Equip {name} (joining as {seniority} {role}) with end-to-end technical, operational, and cultural fluency within {dept_name} ({bu_name}). The curriculum ensures fast time-to-productivity, strict compliance with safety/security standards, and deep alignment with our cross-BU closed-loop clean energy strategy.

---

## 2. Mandatory Foundation & Domain Modules
{modules_text}

---

## 3. Phased 30-Day Competency Milestones
{milestones_text}

---

## 4. Practical Hands-On Labs & Shadowing
* **Buddy Pairing:** Meet 2–3x weekly with assigned onboarding buddy to review practical tool usage and team rituals.
* **Operational Observation:** Shadow at least 3 critical operational cycles (standups, customer calls, architectural reviews, or site audits).
* **Sandbox Validation:** Complete 1 scoped sandbox exercise replicating real-world production tasks prior to full autonomy.

---

## 5. Certification & Sign-off Gate
* **Requirement:** 100% completion of LMS modules and passing score on role-specific practical assessment.
* **Evaluator:** Direct Manager and Department Lead.
"""

    def list_all_learning_plans(self) -> List[Dict[str, Any]]:
        """
        Lists summary metadata for all cached role learning plans.
        Returns:
            List[dict]: List of learning plan metadata items (slug, title, file name, preview).
        """
        plans = []
        for p_file in sorted(self.storage_dir.glob("*.md")):
            content = p_file.read_text(encoding="utf-8")
            title = p_file.name.replace(".md", "").replace("-", " ").title()
            plans.append({
                "role_slug": p_file.stem,
                "role_title": title,
                "file_name": p_file.name,
                "size_bytes": p_file.stat().st_size,
                "last_modified": datetime.fromtimestamp(p_file.stat().st_mtime).isoformat(),
                "content_preview": "\n".join(content.splitlines()[:6])
            })
        return plans

    def get_plan_by_slug(self, role_slug: str) -> Optional[str]:
        """
        Retrieves the raw markdown string of a learning plan for a specific role slug.
        Args:
            role_slug (str): Kebab-case role identifier.
        Returns:
            str or None: Raw markdown content, or None if not found.
        """
        p_file = self.storage_dir / f"{role_slug}.md"
        if p_file.exists():
            return p_file.read_text(encoding="utf-8")
        return None

    def update_learning_plan(self, role_slug: str, markdown_content: str) -> bool:
        """
        Overwrites or creates a markdown learning plan file for a given role slug.
        Args:
            role_slug (str): Kebab-case role identifier.
            markdown_content (str): New markdown content to save.
        Returns:
            bool: True on successful write.
        """
        p_file = self.storage_dir / f"{role_slug}.md"
        p_file.write_text(markdown_content, encoding="utf-8")
        return True

# Singleton instance
learning_expert_agent = LearningExpertAgent()

