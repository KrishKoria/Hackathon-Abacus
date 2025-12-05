"""RAG service for ClaimsIQ Nexus.

Provides ChromaDB vector search for clinical notes using
OpenAI embeddings.
"""

import os
import re
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

from src.config import (
    CLINICAL_NOTES_DIR,
    OPENAI_API_KEY,
    OPENAI_EMBEDDING_MODEL,
)

# Global ChromaDB client and collection cache
_chroma_client: Optional[chromadb.Client] = None
_collection: Optional[chromadb.Collection] = None


def init_chromadb(persist: bool = False) -> chromadb.Collection:
    """Initialize ChromaDB with OpenAI embeddings.

    Args:
        persist: If True, use persistent storage (default: False, in-memory)

    Returns:
        ChromaDB collection for clinical notes
    """
    global _chroma_client, _collection

    if _collection is not None:
        return _collection

    # Initialize client
    if persist:
        _chroma_client = chromadb.PersistentClient(path=".chroma")
    else:
        _chroma_client = chromadb.Client()

    # Create OpenAI embedding function
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=OPENAI_EMBEDDING_MODEL,
    )

    # Get or create collection
    _collection = _chroma_client.get_or_create_collection(
        name="clinical_notes",
        embedding_function=openai_ef,
        metadata={"description": "Clinical notes for ClaimsIQ Nexus"},
    )

    return _collection


def index_notes(notes_dir: Optional[str] = None) -> int:
    """Index clinical notes into ChromaDB.

    Args:
        notes_dir: Directory containing clinical note markdown files
                   (default: CLINICAL_NOTES_DIR from config)

    Returns:
        Number of notes indexed
    """
    if notes_dir is None:
        notes_dir = CLINICAL_NOTES_DIR

    notes_path = Path(notes_dir)
    if not notes_path.exists():
        return 0

    collection = init_chromadb()

    # Clear existing documents
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    # Read and index all markdown files
    documents = []
    metadatas = []
    ids = []

    for md_file in notes_path.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        # Parse frontmatter
        metadata = _parse_frontmatter(content)

        # Get note ID from filename or frontmatter
        note_id = metadata.get("note_id") or md_file.stem

        # Remove frontmatter from content for embedding
        content_body = _remove_frontmatter(content)

        documents.append(content_body)
        metadatas.append({
            "note_id": note_id,
            "patient_id": metadata.get("patient_id", ""),
            "claim_id": metadata.get("claim_id", "") or "",
            "note_type": metadata.get("note_type", ""),
            "note_date": metadata.get("note_date", ""),
            "is_golden_nugget": str(metadata.get("is_golden_nugget", "false")).lower(),
            "filename": md_file.name,
        })  
        ids.append(note_id)

    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    return len(documents)


def search_notes(
    query: str,
    patient_id: Optional[str] = None,
    limit: int = 5,
) -> list[dict]:
    """Search clinical notes using semantic search.

    Args:
        query: Natural language search query
        patient_id: Optional patient ID filter
        limit: Maximum number of results

    Returns:
        List of search results with note content and metadata
    """
    collection = init_chromadb()

    # Check if collection has documents
    if collection.count() == 0:
        # Try to index notes
        indexed = index_notes()
        if indexed == 0:
            return []

    # Build where filter
    where_filter = None
    if patient_id:
        where_filter = {"patient_id": patient_id}

    # Perform search
    results = collection.query(
        query_texts=[query],
        n_results=limit,
        where=where_filter,
    )

    # Format results
    formatted_results = []

    if results and results["documents"] and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0

            # Calculate similarity score (ChromaDB uses L2 distance)
            # Convert distance to similarity (0-1 scale)
            similarity = max(0, 1 - (distance / 2))

            formatted_results.append({
                "note_id": metadata.get("note_id", ""),
                "patient_id": metadata.get("patient_id", ""),
                "claim_id": metadata.get("claim_id") if metadata.get("claim_id") else None,
                "note_type": metadata.get("note_type", ""),
                "note_date": metadata.get("note_date", ""),
                "content_snippet": _get_snippet(doc, query),
                "full_content": doc,
                "similarity_score": round(similarity, 4),
                "is_golden_nugget": metadata.get("is_golden_nugget", "false") == "true",
            })

    return formatted_results


def get_note_by_id(note_id: str) -> Optional[dict]:
    """Get a specific clinical note by ID.

    Args:
        note_id: The note identifier (e.g., "CN-001")

    Returns:
        Note data as dictionary, or None if not found
    """
    collection = init_chromadb()

    # Ensure collection is indexed
    if collection.count() == 0:
        index_notes()

    results = collection.get(ids=[note_id])

    if not results["documents"]:
        return None

    doc = results["documents"][0]
    metadata = results["metadatas"][0] if results["metadatas"] else {}

    return {
        "note_id": note_id,
        "patient_id": metadata.get("patient_id", ""),
        "claim_id": metadata.get("claim_id") if metadata.get("claim_id") else None,
        "note_type": metadata.get("note_type", ""),
        "note_date": metadata.get("note_date", ""),
        "content": doc,
        "is_golden_nugget": metadata.get("is_golden_nugget", "false") == "true",
    }


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown content with optional frontmatter

    Returns:
        Dictionary of frontmatter key-value pairs
    """
    metadata = {}

    # Check for frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    # Handle null/false values
                    if value.lower() == "null":
                        value = None
                    elif value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    metadata[key] = value

    return metadata


def _remove_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from markdown content.

    Args:
        content: Markdown content with optional frontmatter

    Returns:
        Content without frontmatter
    """
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()

    return content


def _get_snippet(content: str, query: str, max_length: int = 200) -> str:
    """Get a relevant snippet from content based on query.

    Args:
        content: Full document content
        query: Search query
        max_length: Maximum snippet length

    Returns:
        Relevant content snippet
    """
    # Try to find query terms in content
    query_terms = query.lower().split()

    # Look for paragraph containing query terms
    paragraphs = content.split("\n\n")

    for para in paragraphs:
        para_lower = para.lower()
        if any(term in para_lower for term in query_terms):
            # Found relevant paragraph
            if len(para) <= max_length:
                return para.strip()
            else:
                # Truncate with ellipsis
                return para[:max_length].strip() + "..."

    # No match found, return first paragraph
    first_para = paragraphs[0] if paragraphs else content
    if len(first_para) <= max_length:
        return first_para.strip()
    else:
        return first_para[:max_length].strip() + "..."
