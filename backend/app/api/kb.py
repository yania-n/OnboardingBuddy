from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from ..rag.indexer import rag_engine

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])

@router.get("/docs")
def list_documents():
    """
    Lists the file names and metadata of all documents registered in the RAG Knowledge Base.
    """
    return rag_engine.get_all_documents()

@router.get("/docs/{file_name}")
def get_document(file_name: str):
    """
    Retrieves the raw markdown content of a specific knowledge base document.
    Args:
        file_name (str): The filename of the document to fetch.
    """
    doc = rag_engine.get_document_content(file_name)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/search")
def search_knowledge_base(
    q: str = Query(..., description="Search query string"),
    role: Optional[str] = None,
    bu: Optional[str] = None,
    top_k: int = 5
):
    """
    Searches the Knowledge Base using hybrid BM25 and semantic matching.
    Optionally filters results by user role and business unit to maintain grounding focus.
    Args:
        q (str): Query string.
        role (str, optional): Role to filter documents.
        bu (str, optional): Business unit to filter documents.
        top_k (int): Number of top results to return.
    """
    results = rag_engine.search(query=q, top_k=top_k, filter_role=role, filter_bu=bu, min_score=0.1)
    formatted = []
    for chunk, score in results:
        formatted.append({
            "doc_name": chunk.doc_name,
            "section_title": chunk.section_title,
            "line_start": chunk.line_start,
            "line_end": chunk.line_end,
            "relevance_score": round(score, 3),
            "content": chunk.content,
            "metadata": chunk.metadata
        })
    return {
        "query": q,
        "results_count": len(formatted),
        "results": formatted
    }

