#!/usr/bin/env python3
"""Index clinical notes into ChromaDB for vector search.

This script reads all clinical notes from the generated data directory
and indexes them into ChromaDB using OpenAI embeddings for semantic search.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import CLINICAL_NOTES_DIR, OPENAI_API_KEY, validate_config
from src.services.rag_service import init_chromadb, index_notes, search_notes


def main():
    """Index clinical notes and verify the indexing."""
    print("=" * 60)
    print("ClaimsIQ Nexus - Clinical Notes Indexer")
    print("=" * 60)
    
    # Validate configuration
    try:
        validate_config()
        print(f"\n[OK] Configuration validated")
        print(f"    OpenAI API Key: {'*' * 8}...{OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 4 else 'NOT SET'}")
    except ValueError as e:
        print(f"\n[ERROR] Configuration error: {e}")
        sys.exit(1)
    
    # Check clinical notes directory
    notes_path = Path(CLINICAL_NOTES_DIR)
    if not notes_path.exists():
        print(f"\n[ERROR] Clinical notes directory not found: {notes_path}")
        print("        Run 'python scripts/generate_data.py' first to generate data.")
        sys.exit(1)
    
    # Count available notes
    md_files = list(notes_path.glob("*.md"))
    print(f"\n[INFO] Found {len(md_files)} clinical notes in {notes_path}")
    
    if len(md_files) == 0:
        print("[ERROR] No clinical notes found to index.")
        sys.exit(1)
    
    # Initialize ChromaDB and index notes
    print("\n[INFO] Initializing ChromaDB with OpenAI embeddings...")
    collection = init_chromadb(persist=True)  # Use persistent storage
    
    print("[INFO] Indexing clinical notes (this may take a moment)...")
    indexed_count = index_notes(CLINICAL_NOTES_DIR)
    
    print(f"\n[SUCCESS] Indexed {indexed_count} clinical notes into ChromaDB")
    
    # Verify collection stats
    print("\n" + "-" * 60)
    print("ChromaDB Collection Statistics:")
    print("-" * 60)
    print(f"  Collection name: {collection.name}")
    print(f"  Document count:  {collection.count()}")
    
    # Test semantic search
    print("\n" + "-" * 60)
    print("Testing Semantic Search:")
    print("-" * 60)
    
    test_queries = [
        "prior authorization documentation",
        "diabetes treatment insulin therapy",
        "chronic condition management",
        "medical necessity justification",
    ]
    
    for query in test_queries:
        results = search_notes(query, limit=2)
        print(f"\n  Query: '{query}'")
        if results:
            for i, r in enumerate(results, 1):
                golden = " [GOLDEN NUGGET]" if r.get("is_golden_nugget") else ""
                print(f"    {i}. Note {r['note_id']} (score: {r['similarity_score']:.3f}){golden}")
                print(f"       Type: {r['note_type']}, Patient: {r['patient_id']}")
        else:
            print("    No results found")
    
    # Check golden nuggets
    print("\n" + "-" * 60)
    print("Golden Nugget Notes in Collection:")
    print("-" * 60)
    
    # Get all documents and filter for golden nuggets
    all_docs = collection.get(include=["metadatas"])
    golden_count = 0
    golden_notes = []
    
    if all_docs["metadatas"]:
        for i, meta in enumerate(all_docs["metadatas"]):
            if meta.get("is_golden_nugget") == "true":
                golden_count += 1
                golden_notes.append({
                    "note_id": meta.get("note_id"),
                    "claim_id": meta.get("claim_id"),
                    "note_type": meta.get("note_type"),
                })
    
    print(f"  Total golden nugget notes: {golden_count}")
    for note in golden_notes[:5]:  # Show first 5
        print(f"    - {note['note_id']}: {note['note_type']} (Claim: {note['claim_id']})")
    if len(golden_notes) > 5:
        print(f"    ... and {len(golden_notes) - 5} more")
    
    print("\n" + "=" * 60)
    print("[COMPLETE] Clinical notes are now indexed and searchable!")
    print("=" * 60)
    
    return indexed_count


if __name__ == "__main__":
    main()
