import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class DocumentChunk:
    """
    Represents a parsed semantic chunk of a markdown document with line boundaries and metadata.
    """
    def __init__(self, doc_name: str, section_title: str, content: str, line_start: int, line_end: int, metadata: Optional[Dict[str, Any]] = None):
        """
        Initializes a DocumentChunk instance.
        Args:
            doc_name (str): Name of the source markdown file (e.g. '01_ORG_STRUCTURE.md').
            section_title (str): Header/Section title of the chunk.
            content (str): Text content of the section.
            line_start (int): Starting line number in the source file.
            line_end (int): Ending line number in the source file.
            metadata (dict, optional): Extracted entity metadata (roles, BUs, tools, training codes).
        """
        self.doc_name = doc_name
        self.section_title = section_title
        self.content = content.strip()
        self.line_start = line_start
        self.line_end = line_end
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the document chunk object into a dictionary representation.
        Returns:
            dict: Serialized chunk dictionary.
        """
        return {
            "doc_name": self.doc_name,
            "section_title": self.section_title,
            "content": self.content,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "metadata": self.metadata
        }

def parse_markdown_content(doc_name: str, text: str) -> List[DocumentChunk]:
    """
    Parses the raw text of a markdown document into semantic sections based on Markdown headers (# to ####).
    Args:
        doc_name (str): The filename of the markdown document.
        text (str): The raw text content of the markdown document.
    Returns:
        List[DocumentChunk]: List of extracted DocumentChunk objects with line numbers and metadata.
    """
    lines = text.splitlines()
    chunks: List[DocumentChunk] = []

    current_section = doc_name.replace(".md", "")
    current_lines = []
    section_start_line = 1

    header_regex = re.compile(r"^(#{1,4})\s+(.+)$")

    for idx, line in enumerate(lines, start=1):
        match = header_regex.match(line)
        if match:
            # If we had accumulated content, save previous chunk
            if current_lines:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text:
                    metadata = extract_chunk_metadata(chunk_text, doc_name, current_section)
                    chunks.append(DocumentChunk(
                        doc_name=doc_name,
                        section_title=current_section,
                        content=chunk_text,
                        line_start=section_start_line,
                        line_end=idx - 1,
                        metadata=metadata
                    ))
            current_section = match.group(2).strip()
            current_lines = [line]
            section_start_line = idx
        else:
            current_lines.append(line)

    if current_lines:
        chunk_text = "\n".join(current_lines).strip()
        if chunk_text:
            metadata = extract_chunk_metadata(chunk_text, doc_name, current_section)
            chunks.append(DocumentChunk(
                doc_name=doc_name,
                section_title=current_section,
                content=chunk_text,
                line_start=section_start_line,
                line_end=len(lines),
                metadata=metadata
            ))

    return chunks

def parse_markdown_file(file_path: Path) -> List[DocumentChunk]:
    """
    Reads a local markdown file and parses its contents into DocumentChunk objects.
    Args:
        file_path (Path): Path to the markdown file.
    Returns:
        List[DocumentChunk]: List of parsed DocumentChunk objects (empty if file does not exist).
    """
    if not file_path.exists():
        return []

    doc_name = file_path.name
    text = file_path.read_text(encoding="utf-8")
    return parse_markdown_content(doc_name, text)

def extract_chunk_metadata(text: str, doc_name: str, section_title: str) -> Dict[str, Any]:
    """
    Extracts structured entity metadata (relevant roles, business units, tools, and training module codes)
    from a markdown text chunk.
    Args:
        text (str): Content text of the chunk.
        doc_name (str): Source document name.
        section_title (str): Section header title.
    Returns:
        dict: Metadata dictionary containing roles, business_units, training_modules, tools, and is_table.
    """
    text_lower = text.lower()
    metadata = {
        "roles": [],
        "business_units": [],
        "training_modules": [],
        "tools": [],
        "is_table": "|" in text
    }

    # Detect roles
    known_roles = [
        "account executive", "marketing analyst", "product owner", "tech recruiter",
        "project manager", "graduate trainee", "embedded firmware engineer", "mlops engineer",
        "solutions engineer", "customer success", "support engineer", "director", "evp"
    ]
    for r in known_roles:
        if r in text_lower:
            metadata["roles"].append(r)

    # Detect Business Units
    if "mobility" in text_lower or "bu-1" in text_lower or "vehicle" in text_lower:
        metadata["business_units"].append("Electric Mobility")
    if "solar" in text_lower or "bu-2" in text_lower or "pv" in text_lower:
        metadata["business_units"].append("Solar Energy Systems")
    if "storage" in text_lower or "bu-3" in text_lower or "bess" in text_lower or "battery" in text_lower:
        metadata["business_units"].append("Energy Storage Systems")
    if "gtm" in text_lower or "commercial" in text_lower or "sales" in text_lower or "marketing" in text_lower:
        metadata["business_units"].append("Commercial & GTM")

    # Detect training module codes (e.g., SEC-101, CMP-101, DATA-101, GTM-PITCH-101, HW-SAFE-201)
    module_matches = re.findall(r"\b[A-Z]{2,6}-[A-Z0-9]+-\d{3}\b|\b[A-Z]{2,6}-\d{3}\b", text)
    if module_matches:
        metadata["training_modules"] = list(set(module_matches))

    # Detect tools
    known_tools = [
        "salesforce", "hubspot", "jira", "confluence", "procore", "greenhouse", "lever",
        "snowflake", "bigquery", "looker", "tableau", "sap", "gitlab", "outreach",
        "linkedin recruiter", "servicenow", "workday", "slack", "teams"
    ]
    for t in known_tools:
        if t in text_lower:
            metadata["tools"].append(t)

    return metadata

