# Document RAG & Index Engine

This module implements Document Parsing and Hybrid Search Retrieval to answer employee policy questions from the Knowledge Base directory (`kb_docs/`).

## Components

- **`parser.py`**:
  - Parses Markdown documents into logical section-level chunks.
  - Normalizes formatting, tracks line numbers, and extracts document-level metadata (e.g. roles, policies, business units).

- **`indexer.py`**:
  - Implements a hybrid search engine combining TF-IDF/BM25 (lexical lookup) with semantic/concept filters.
  - Matches queries and ranks matching chunks with relevance scoring.
  - Exposes metadata filters for user roles and BUs.
