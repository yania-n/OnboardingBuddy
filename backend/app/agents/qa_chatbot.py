import re
import os
from typing import Dict, Any, List, Optional
from ..db.models import ChatMessageResponse, Citation
from ..db.database import save_missing_feedback
from ..rag.indexer import rag_engine
from .org_expert import org_expert_agent
from ..config import GCP_PROJECT_ID, GEMINI_MODEL


class QAChatbotAgent:
    """
    Grounded Question-Answering Chatbot Assistant.
    Searches the Knowledge Base with BM25, queries Vertex AI / Gemini when available,
    synthesizes citations, and escalates unanswered queries to managers.
    """
    def __init__(self):
        """Initializes the Q&A Chatbot Agent and attempts to connect to Vertex AI."""
        self._init_genai_client()

    def _init_genai_client(self):
        """Initializes the Google GenAI / Vertex AI client."""
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
            print(f"GenAI Client init info: {e}")

    def _extract_subject_terms(self, text: str) -> List[str]:
        """
        Extracts meaningful non-generic keyword tokens from a user query.
        Args:
            text (str): Raw question string.
        Returns:
            List[str]: Filtered subject keyword tokens.
        """
        tokens = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower())
        generic = {
            "what", "where", "when", "which", "who", "whom", "whose", "why", "how",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "can", "could", "should", "would", "must", "may",
            "the", "and", "but", "for", "with", "about", "against", "between", "into",
            "through", "during", "before", "after", "above", "below", "from", "down",
            "in", "out", "on", "off", "over", "under", "again", "further", "then",
            "once", "here", "there", "all", "any", "both", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "s", "t", "just", "don", "now",
            "tell", "explain", "describe", "give", "show", "please", "help", "know",
            "policy", "rules", "guidelines", "information", "details", "process"
        }
        return [t for t in tokens if t not in generic]

    def _is_org_question(self, query: str) -> bool:
        """
        Determines if a query pertains to company structure, leaders, or culture.
        Args:
            query (str): User question.
        Returns:
            bool: True if organizational keywords are detected.
        """
        org_keywords = {
            "org", "organisation", "organization", "team", "department", "division",
            "unit", "role", "stakeholder", "colleague", "peer", "manager", "report",
            "structure", "culture", "values", "mission", "strategy", "okr", "goal",
            "who", "contact", "meet", "introduce", "introduction", "connect",
        }
        words = set(re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", query.lower()))
        return bool(words & org_keywords)

    def answer_question(
        self,
        query: str,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        user_role: Optional[str] = None,
        context_bu: Optional[str] = None,
        user_team: Optional[str] = None,
        user_dept: Optional[str] = None
    ) -> ChatMessageResponse:
        """
        Answers a user's question using strict knowledge-base grounding and citations.
        If information is missing, records the query to the manager feedback log and returns escalation advice.
        Args:
            query (str): The question asked by the user.
            user_id (str, optional): User ID for personalizing context.
            user_name (str, optional): User name.
            user_role (str, optional): User role title.
            context_bu (str, optional): Business unit context.
            user_team (str, optional): User team.
            user_dept (str, optional): User department.
        Returns:
            ChatMessageResponse: Answer with source citations and escalation flags.
        """

        cleaned_query = query.strip()
        if not cleaned_query:
            return ChatMessageResponse(
                answer="Please ask a question about your onboarding, role, company policies, or tools.",
                citations=[],
                is_missing_info=False,
                manager_escalation=False,
                context_role=user_role
            )

        # Check with Org Expert for direct organizational questions
        org_answer = org_expert_agent.answer_org_query(cleaned_query)
        if org_answer:
            citations = [
                Citation(
                    doc_name="01_ORG_STRUCTURE.md",
                    section_title="Executive & Business Unit Organizational Chart",
                    excerpt=org_answer[:200] + "...",
                    relevance_score=1.0
                )
            ]
            return ChatMessageResponse(
                answer=org_answer,
                citations=citations,
                is_missing_info=False,
                manager_escalation=False,
                context_role=user_role
            )

        subject_terms = self._extract_subject_terms(cleaned_query)

        # Query the RAG engine
        search_results = rag_engine.search(
            query=cleaned_query,
            top_k=4,
            filter_role=user_role,
            filter_bu=context_bu,
            min_score=0.4
        )

        # Enrich with org context if question is org/team/role related
        if self._is_org_question(cleaned_query):
            org_chunks = org_expert_agent.get_org_context_chunks(
                role=user_role or "",
                team=user_team or "",
                department=user_dept or "",
                business_unit=context_bu or "",
                top_k=3
            )
            seen_keys = {f"{c.doc_name}:{c.section_title}" for c, _ in search_results}
            class OrgMockChunk:
                def __init__(self, doc_name, section_title, content):
                    self.doc_name = doc_name
                    self.section_title = section_title
                    self.content = content.strip()
                    self.line_start = 1
                    self.line_end = 1
                    self.metadata = {}

            for oc in org_chunks:
                key = f"{oc['source']}:{oc['section']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    search_results.append((OrgMockChunk(oc['source'], oc['section'], oc['text']), oc['relevance_score']))

        # Verify grounding: check if key subject terms exist in the knowledge base / retrieved chunks
        is_grounded = False
        if search_results and subject_terms:
            retrieved_corpus = " ".join([c.content.lower() + " " + c.section_title.lower() for c, _ in search_results])
            matched_terms = [term for term in subject_terms if term in retrieved_corpus]
            match_ratio = len(matched_terms) / len(subject_terms)

            if match_ratio >= 0.5 or (len(matched_terms) >= 2 and len(subject_terms) <= 3):
                is_grounded = True

        if not is_grounded:
            # Fallback to manager escalation and log missing feedback
            save_missing_feedback(
                query=cleaned_query,
                user_id=user_id,
                user_name=user_name,
                user_role=user_role,
                context_bu=context_bu
            )
            fallback_answer = (
                "I'm sorry, I don't have information on that in our current company knowledge base. "
                "Please reach out directly to your manager for guidance on this topic, and I have logged your question as feedback "
                "so our team can expand the knowledge base documentation."
            )
            return ChatMessageResponse(
                answer=fallback_answer,
                citations=[],
                is_missing_info=True,
                manager_escalation=True,
                context_role=user_role
            )

        # Build citations
        citations: List[Citation] = []
        for chunk, score in search_results:
            clean_excerpt = chunk.content.replace("\n", " ").strip()
            if len(clean_excerpt) > 180:
                clean_excerpt = clean_excerpt[:180] + "..."

            citations.append(Citation(
                doc_name=chunk.doc_name,
                section_title=chunk.section_title,
                excerpt=clean_excerpt,
                relevance_score=round(score, 2)
            ))

        # Summarize information directly into a clear answer without directing to links
        summary_text = self._synthesize_grounded_answer(cleaned_query, search_results, user_role, context_bu)

        return ChatMessageResponse(
            answer=summary_text,
            citations=citations,
            is_missing_info=False,
            manager_escalation=False,
            context_role=user_role
        )

    def _synthesize_grounded_answer(
        self,
        query: str,
        search_results: List[Any],
        user_role: Optional[str] = None,
        context_bu: Optional[str] = None
    ) -> str:
        # Prepare context from retrieved chunks
        context_blocks = []
        for idx, (chunk, _) in enumerate(search_results, start=1):
            context_blocks.append(f"--- Document Section: {chunk.doc_name} ({chunk.section_title}) ---\n{chunk.content}")
        combined_context = "\n\n".join(context_blocks)

        # Try Vertex AI Gemini generation if available
        if self.genai_client:
            try:
                prompt = f"""You are the Onboarding Q&A Expert Agent for our clean energy enterprise.

Your ONLY source of truth is the context provided below from the company knowledge base.

You will also receive a short profile of the new joiner asking the question. Use it to:
- Address them by their first name
- Tailor examples and terminology to their role, seniority, and department
- Make references to their team or manager where relevant
- Adjust the depth of your answer to their seniority level

Rules you must follow without exception:
1. Answer ONLY from the provided KB context — never use external knowledge or assumptions.
2. If the context does not contain a clear answer, reply with "I'm sorry, I don't have information on that in our current company knowledge base. Please reach out directly to your manager for guidance on this topic, and I have logged your question as feedback so our team can expand the knowledge base documentation."
3. Always cite the source document at the end of your answer, e.g. "Source: NexoraGlobal_EmployeeHandbook"
4. Be concise and friendly. Use bullet points for lists. Keep answers under 250 words unless the question genuinely requires more.
5. Never make up policies, names, dates, links, or procedures.
6. Warm, encouraging tone — remember this person is new and finding their feet.
7. When answering queries about the company mission, always reference the official mission statement and include key terms like "decarbonization".
8. Always use simple, clear English to interact with users. Avoid overly complex jargon, bureaucratic terminology, or dense phrasing.

User Role: {user_role or 'New Employee'}
Business Unit: {context_bu or 'Clean Energy Ecosystem'}
User Question: {query}

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
                print(f"GenAI generation fallback: {e}")

        # Local deterministic summarizer
        return self._local_semantic_summary(query, search_results)

    def _local_semantic_summary(self, query: str, search_results: List[Any]) -> str:
        top_chunk, _ = search_results[0]
        content = top_chunk.content

        lines = content.splitlines()
        trimmed_lines = []
        for l in lines:
            if l.startswith("#"):
                clean_header = l.replace("#", "").strip()
                trimmed_lines.append(f"**{clean_header}**")
            else:
                trimmed_lines.append(l)

        summary = "\n".join(trimmed_lines[:15]).strip()

        if len(search_results) > 1:
            second_chunk, _ = search_results[1]
            if second_chunk.doc_name != top_chunk.doc_name:
                second_lines = [l for l in second_chunk.content.splitlines() if not l.startswith("#")]
                if second_lines:
                    summary += "\n\n" + "\n".join(second_lines[:8]).strip()

        return summary

# Singleton instance
qa_chatbot_agent = QAChatbotAgent()
