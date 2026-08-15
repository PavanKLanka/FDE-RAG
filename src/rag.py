from src.loader import load_documents
from src.chunker import chunk_text
from src.embeddings import EmbeddingModel
from src.retriever import Retriever
from src.llm import classify_intent
from src.llm import generate_answer


# ============================================================
# 1. LOAD KNOWLEDGE BASE
# ============================================================

documents = load_documents(
    "data/knowledge_base"
)


# ============================================================
# 2. CREATE CHUNKS
# ============================================================

chunks = []

for document in documents:

    document_chunks = chunk_text(
        document["content"]
    )

    for chunk in document_chunks:

        chunks.append({
            "text": chunk,
            "source": document["source"]
        })


# ============================================================
# 3. CREATE EMBEDDING MODEL
# ============================================================

embedding_model = EmbeddingModel()


# ============================================================
# 4. CREATE EMBEDDINGS FOR KNOWLEDGE BASE
# ============================================================

chunk_texts = [
    chunk["text"]
    for chunk in chunks
]

embeddings = embedding_model.embed(
    chunk_texts
)


# ============================================================
# 5. CREATE RETRIEVER
# ============================================================

retriever = Retriever(
    embeddings,
    chunks
)


# ============================================================
# 6. GENERAL CONVERSATION
# ============================================================

def handle_conversation(question):

    prompt = f"""
You are SupportPilot, a polite and friendly
CloudDesk customer support assistant.

The user is having a general conversation.

Respond naturally and briefly.

USER:
{question}
"""

    return generate_answer(
        question,
        prompt
    )


# ============================================================
# 7. UNKNOWN / UNRELATED
# ============================================================

def handle_unknown():

    return (
        "I'm SupportPilot, the CloudDesk customer "
        "support assistant. I can help with CloudDesk "
        "questions such as passwords, accounts, billing, "
        "subscriptions, integrations, security, and "
        "support tickets. Please let me know how I can help."
    )


# ============================================================
# 8. MAIN QUESTION HANDLER
# ============================================================

def answer_question(question):

    # --------------------------------------------------------
    # STEP 1: CLASSIFY INTENT
    # --------------------------------------------------------

    intent = classify_intent(
        question
    )

    print(
        f"[Intent Router] {question} → {intent}"
    )


    # ========================================================
    # CONVERSATION
    # ========================================================

    if intent == "conversation":

        answer = handle_conversation(
            question
        )

        return {
            "answer": answer,
            "sources": [],
            "handoff": False,
            "score": 1.0,
            "intent": "conversation"
        }


    # ========================================================
    # UNKNOWN
    # ========================================================

    if intent == "unknown":

        answer = handle_unknown()

        return {
            "answer": answer,
            "sources": [],
            "handoff": False,
            "score": 0.0,
            "intent": "unknown"
        }


    # ========================================================
    # SUPPORT
    # ========================================================

    query_embedding = embedding_model.embed(
        [question]
    )


    # --------------------------------------------------------
    # SEARCH KNOWLEDGE BASE
    # --------------------------------------------------------

    results = retriever.search(
        query_embedding,
        top_k=3
    )


    # --------------------------------------------------------
    # DEBUG INFORMATION
    # --------------------------------------------------------

    print("\n[Retriever Results]")

    for result in results:

        print(
            f"Score: {result['score']:.4f} | "
            f"Source: {result['source']}"
        )


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not results:

        return {
            "answer": (
                "I couldn't find information about this "
                "in the CloudDesk knowledge base. "
                "I recommend connecting with a human "
                "support agent."
            ),
            "sources": [],
            "handoff": True,
            "score": 0.0,
            "intent": "support"
        }


    # ========================================================
    # BEST MATCH
    # ========================================================

    best_score = results[0]["score"]


    print(
        f"[Best Retrieval Score] {best_score:.4f}"
    )


    # ========================================================
    # CONFIDENCE CHECK
    # ========================================================

    CONFIDENCE_THRESHOLD = 0.40


    if best_score < CONFIDENCE_THRESHOLD:

        return {
            "answer": (
                "I couldn't find enough information "
                "in the CloudDesk knowledge base to "
                "answer this accurately. "
                "I recommend connecting with a human "
                "support agent."
            ),
            "sources": [],
            "handoff": True,
            "score": best_score,
            "intent": "support"
        }


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context = "\n\n".join(
        result["text"]
        for result in results
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    answer = generate_answer(
        question,
        context
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "answer": answer,
        "sources": [
            result["source"]
            for result in results
        ],
        "handoff": False,
        "score": best_score,
        "intent": "support"
    }