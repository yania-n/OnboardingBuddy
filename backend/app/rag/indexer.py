import math
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ..config import KB_DOCS_DIR, GCP_PROJECT_ID
from .parser import parse_markdown_file, parse_markdown_content, DocumentChunk
from google.cloud import storage

class RAGIndexer:
    """
    In-memory BM25 indexer with metadata boosting for knowledge base markdown documents.
    Supports reading from Google Cloud Storage or local file fallback.
    """
    def __init__(self, kb_dir: Path = KB_DOCS_DIR):
        """
        Initializes the RAG Indexer and triggers initial index construction.
        Args:
            kb_dir (Path): Local directory containing markdown handbook files.
        """
        self.kb_dir = kb_dir
        self.chunks: List[DocumentChunk] = []
        self.inverted_index: Dict[str, List[int]] = {}
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.corpus_size: int = 0
        self.indexed_at: Optional[str] = None
        self.build_index()

    def _tokenize(self, text: str) -> List[str]:
        """
        Extracts lowercase alphanumeric tokens and strips common English stopwords.
        Args:
            text (str): Input text string.
        Returns:
            List[str]: Cleaned list of filtered tokens.
        """
        tokens = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
            "by", "about", "against", "between", "into", "through", "during", "before",
            "after", "above", "below", "from", "up", "down", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did", "can",
            "could", "should", "would", "must", "all", "each", "every", "both", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "s", "t", "just", "don", "now"
        }
        return [t for t in tokens if t not in stopwords]

    def build_index(self):
        """
        Builds the inverted index and BM25 token statistics by reading markdown documents
        from GCS bucket or local kb_docs directory.
        """
        self.chunks = []
        self.inverted_index = {}
        self.doc_lengths = []

        gcs_success = False
        try:
            client = storage.Client(project=GCP_PROJECT_ID)
            bucket_name = "onboarding-buddy-kb-2e1aa6a7"
            bucket = client.bucket(bucket_name)
            
            blobs = list(bucket.list_blobs())
            md_blobs = sorted([b for b in blobs if b.name.endswith(".md")], key=lambda x: x.name)
            
            if md_blobs:
                for blob in md_blobs:
                    text = blob.download_as_text(encoding="utf-8")
                    file_chunks = parse_markdown_content(blob.name, text)
                    self.chunks.extend(file_chunks)
                gcs_success = True
        except Exception as e:
            print(f"Failed to read from GCS bucket, falling back to local files: {e}")

        # Local fallback
        if not gcs_success:
            if not self.kb_dir.exists():
                return

            for md_file in sorted(self.kb_dir.glob("*.md")):
                file_chunks = parse_markdown_file(md_file)
                self.chunks.extend(file_chunks)

        self.corpus_size = len(self.chunks)
        if self.corpus_size == 0:
            return

        total_tokens = 0
        for chunk_idx, chunk in enumerate(self.chunks):
            # Combine doc name, section title (with weight) and content
            weighted_text = f"{chunk.doc_name} {chunk.section_title} {chunk.section_title} {chunk.content}"
            tokens = self._tokenize(weighted_text)
            self.doc_lengths.append(len(tokens))
            total_tokens += len(tokens)

            for token in set(tokens):
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append(chunk_idx)

        self.avg_doc_len = total_tokens / max(1, self.corpus_size)

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_role: Optional[str] = None,
        filter_bu: Optional[str] = None,
        min_score: float = 0.1
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Executes a BM25 ranked retrieval query with dynamic metadata and title boosts.
        Args:
            query (str): The search text/question.
            top_k (int): Maximum number of ranked results to return.
            filter_role (str, optional): Target employee role for score boosting.
            filter_bu (str, optional): Target business unit for score boosting.
            min_score (float): Minimum score cutoff threshold.
        Returns:
            List[Tuple[DocumentChunk, float]]: Ranked list of (DocumentChunk, score) tuples.
        """
        if not self.chunks:
            self.build_index()

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: Dict[int, float] = {}
        k1 = 1.5
        b = 0.75

        for token in query_tokens:
            matching_chunks = self.inverted_index.get(token, [])
            df = len(matching_chunks)
            if df == 0:
                continue

            # BM25 IDF
            idf = math.log(1.0 + (self.corpus_size - df + 0.5) / (df + 0.5))

            for chunk_idx in matching_chunks:
                chunk = self.chunks[chunk_idx]
                chunk_tokens = self._tokenize(f"{chunk.section_title} {chunk.content}")
                tf = chunk_tokens.count(token)
                doc_len = self.doc_lengths[chunk_idx]

                term_score = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / max(1.0, self.avg_doc_len)))))
                scores[chunk_idx] = scores.get(chunk_idx, 0.0) + term_score

        # Apply metadata boosts
        ranked: List[Tuple[DocumentChunk, float]] = []
        for chunk_idx, base_score in scores.items():
            chunk = self.chunks[chunk_idx]
            boost = 1.0

            if filter_role:
                filter_role_clean = filter_role.lower()
                for r in chunk.metadata.get("roles", []):
                    if r in filter_role_clean or filter_role_clean in r:
                        boost += 0.4
                        break

            if filter_bu:
                filter_bu_clean = filter_bu.lower()
                for bu in chunk.metadata.get("business_units", []):
                    if bu.lower() in filter_bu_clean or filter_bu_clean in bu.lower():
                        boost += 0.3
                        break

            # Exact keyword in title boost
            for qt in query_tokens:
                if qt in chunk.section_title.lower():
                    boost += 0.25

            final_score = base_score * boost
            if final_score >= min_score:
                ranked.append((chunk, final_score))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Lists all available local markdown documents with preview metadata.
        Returns:
            List[dict]: Summary details for all handbook documents.
        """
        docs = []
        if not self.kb_dir.exists():
            return []

        for md_file in sorted(self.kb_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            lines = content.splitlines()
            title = lines[0].replace("#", "").strip() if lines else md_file.name
            docs.append({
                "file_name": md_file.name,
                "title": title,
                "size_bytes": md_file.stat().st_size,
                "line_count": len(lines),
                "preview": "\n".join(lines[:6])
            })
        return docs

    def get_document_content(self, file_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the raw text content of a specific local markdown handbook file.
        Args:
            file_name (str): Name of the file to read.
        Returns:
            dict or None: Document content and metadata, or None if file does not exist.
        """
        file_path = self.kb_dir / file_name
        if not file_path.exists() or not file_path.is_file():
            return None
        content = file_path.read_text(encoding="utf-8")
        return {
            "file_name": file_name,
            "content": content,
            "line_count": len(content.splitlines())
        }

# Singleton instance
rag_engine = RAGIndexer()

