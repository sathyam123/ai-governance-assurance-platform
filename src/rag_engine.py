from pathlib import Path
import re

# Location of the sample HR documents
DOCUMENT_DIR = Path(__file__).resolve().parents[1] / "data" / "hr_documents"

# Common words that do not help much with keyword matching
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can",
    "do", "does", "for", "from", "how", "i", "in", "is", "it",
    "of", "on", "or", "should", "the", "to", "what", "when",
    "where", "who", "with", "you", "your","company", "provide", "provides", "policy", "employee", "employees"
}


def tokenize(text):
    """Convert text into searchable lowercase keywords."""
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def load_documents():
    """Load all TXT documents from the HR document folder."""
    documents = []

    if not DOCUMENT_DIR.exists():
        return documents

    for file_path in DOCUMENT_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8-sig").strip()

        if text:
            documents.append({
                "source": file_path.name,
                "content": text
            })

    return documents


def split_into_chunks(documents, max_chars=700):
    """Split documents into smaller, searchable text chunks."""
    chunks = []

    for document in documents:
        paragraphs = [
            paragraph.strip()
            for paragraph in document["content"].split("\n")
            if paragraph.strip()
        ]

        current_chunk = ""
        chunk_number = 1

        for paragraph in paragraphs:
            if current_chunk and len(current_chunk) + len(paragraph) > max_chars:
                chunks.append({
                    "chunk_id": f"{document['source']}_{chunk_number}",
                    "source": document["source"],
                    "text": current_chunk.strip()
                })
                chunk_number += 1
                current_chunk = ""

            if current_chunk:
                current_chunk += "\n" + paragraph
            else:
                current_chunk = paragraph

        if current_chunk:
            chunks.append({
                "chunk_id": f"{document['source']}_{chunk_number}",
                "source": document["source"],
                "text": current_chunk.strip()
            })

    return chunks



def retrieve_documents(query, top_k=3):
    """Retrieve relevant HR document chunks using keyword matching."""
    query_terms = set(tokenize(query))

    if not query_terms:
        return []

    documents = load_documents()
    chunks = split_into_chunks(documents)

    results = []

    for chunk in chunks:
        chunk_terms = set(tokenize(chunk["text"]))
        matching_terms = query_terms.intersection(chunk_terms)
        score = len(matching_terms)

        if query.strip().lower() in chunk["text"].lower():
            score += 2

        # Require at least two meaningful matching keywords
        if len(matching_terms) >= 2:
            results.append({
                **chunk,
                "score": score,
                "matched_terms": sorted(matching_terms)
            })

    results.sort(key=lambda item: item["score"], reverse=True)

    return results[:top_k]



def generate_mock_answer(query, retrieved_chunks):
    """
    Create a transparent mock response from retrieved text.
    This is not an LLM-generated answer.
    """
    if not retrieved_chunks:
        return (
            "I could not find supporting information in the available "
            "HR policy documents. Please contact HR or your reporting "
            "manager for clarification."
        )

    excerpts = []

    for chunk in retrieved_chunks:
        excerpts.append(
            f"Source: {chunk['source']}\n"
            f"Relevant policy text:\n{chunk['text']}"
        )

    return (
        "Based on the available HR policy documents, "
        "the following information may help answer your question:\n\n"
        + "\n\n---\n\n".join(excerpts)
        + "\n\nPlease refer to the cited policy document for context. "
        "This is a mock retrieval-based response, not an AI-generated answer."
    )


def answer_question(query, top_k=3):
    """Run the complete mock RAG workflow."""
    retrieved_chunks = retrieve_documents(query, top_k=top_k)

    return {
        "question": query,
        "answer": generate_mock_answer(query, retrieved_chunks),
        "sources": [
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"],
                "score": chunk["score"],
                "text": chunk["text"]
            }
            for chunk in retrieved_chunks
        ],
        "retrieval_status": "Retrieved" if retrieved_chunks else "No supporting documents found"
    }