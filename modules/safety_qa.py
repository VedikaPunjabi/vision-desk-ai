import os
import json
import math
import re
from datetime import datetime

from dotenv import load_dotenv

# =========================================================
# GEMINI SETUP
# =========================================================

load_dotenv()

GENAI_AVAILABLE = False
client = None
types = None

try:
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key and api_key.strip():
        client = genai.Client(api_key=api_key)
        GENAI_AVAILABLE = True
        print("[RAG System] Gemini API client initialized successfully.")
    else:
        print("[RAG System] GEMINI_API_KEY not found. Using local mode.")

except Exception as e:
    print(f"[RAG System] Gemini unavailable: {e}")
    client = None


# =========================================================
# COSINE SIMILARITY
# =========================================================

def cosine_similarity(vec1, vec2):
    """Calculates cosine similarity between two numeric vectors."""

    dot = sum(a * b for a, b in zip(vec1, vec2))

    norm_a = math.sqrt(
        sum(a * a for a in vec1)
    )

    norm_b = math.sqrt(
        sum(b * b for b in vec2)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


# =========================================================
# VECTOR STORE
# =========================================================

class VectorStore:
    """
    Lightweight in-memory vector database
    for textual chunks and visual evidence.
    """

    def __init__(self):
        self.documents = []

    def add_item(
        self,
        text,
        embedding,
        source="User Document",
        doc_type="text",
        metadata=None
    ):
        doc_id = len(self.documents) + 1

        self.documents.append({
            "id": doc_id,
            "text": text,
            "embedding": embedding,
            "source": source,
            "type": doc_type,
            "metadata": metadata or {},
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        return doc_id

    def search(
        self,
        query_embedding,
        top_k=3,
        doc_type_filter=None
    ):
        scored = []

        for doc in self.documents:

            if (
                doc_type_filter
                and doc["type"] != doc_type_filter
            ):
                continue

            sim = cosine_similarity(
                query_embedding,
                doc["embedding"]
            )

            scored.append((sim, doc))

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return scored[:top_k]


# =========================================================
# RAG SYSTEM
# =========================================================

class RAGSystem:

    def __init__(
        self,
        model_name="gemini-2.5-flash",
        embedding_model="text-embedding-004"
    ):

        self.model_name = model_name
        self.embedding_model = embedding_model

        self.vector_store = VectorStore()

        # Seed default safety policies
        self._seed_default_policies()


    # =====================================================
    # EMBEDDINGS
    # =====================================================

    def generate_embedding(self, text: str) -> list:
        """
        Generates Gemini embedding when available.
        Otherwise uses local hashing vector.
        """

        if client:

            try:

                res = client.models.embed_content(
                    model=self.embedding_model,
                    contents=text
                )

                return res.embedding.values

            except Exception as e:

                print(
                    "[RAG System] Online embedding unavailable:",
                    e
                )

                print(
                    "[RAG System] Using local vectorizer."
                )

        # -------------------------------------------------
        # LOCAL FALLBACK
        # -------------------------------------------------

        words = re.findall(
            r"\b\w+\b",
            text.lower()
        )

        vector = [0.0] * 128

        for word in words:

            index = sum(
                ord(c) for c in word
            ) % 128

            vector[index] += 1.0

        norm = math.sqrt(
            sum(x * x for x in vector)
        ) or 1.0

        return [
            x / norm
            for x in vector
        ]


    # =====================================================
    # DEFAULT SAFETY POLICIES
    # =====================================================

    def _seed_default_policies(self):

        default_docs = [

            (
                "Section 4.1: Hard Hat & PPE Policy. "
                "All personnel operating in active "
                "construction or machinery zones must "
                "wear an approved hard hat, safety vest, "
                "and protective footwear at all times.",
                "Standard Safety Policy Manual"
            ),

            (
                "Section 5.3: Fall Protection & Ladders. "
                "Ladders must be secured on a level, "
                "non-slip surface. Workers operating "
                "at heights exceeding 2 meters must "
                "wear a safety harness tethered to "
                "an anchor point.",
                "OSHA Guidelines 2024"
            ),

            (
                "Section 7.2: Equipment Inspections. "
                "Heavy machinery and ladders must "
                "undergo daily pre-operation inspections. "
                "Any defective equipment must be "
                "tagged out immediately.",
                "Equipment Maintenance SOP"
            )
        ]

        for text, source in default_docs:

            self.ingest_document(
                text,
                source=source
            )


    # =====================================================
    # DOCUMENT INGESTION
    # =====================================================

    def ingest_document(
        self,
        content: str,
        source: str = "Uploaded Document"
    ) -> int:

        # FIXED CHUNKING
        chunks = [
            c.strip()
            for c in re.split(
                r"\n+|(?<=[.!?])\s+",
                content
            )
            if len(c.strip()) > 10
        ]

        if not chunks:
            chunks = [content]

        added_count = 0

        for chunk in chunks:

            embedding = self.generate_embedding(
                chunk
            )

            self.vector_store.add_item(
                text=chunk,
                embedding=embedding,
                source=source,
                doc_type="text"
            )

            added_count += 1

        return added_count


    # =====================================================
    # VISUAL EVIDENCE INDEXING
    # =====================================================

    def index_visual_detection(
        self,
        filename: str,
        detections: list,
        media_type: str
    ):

        detection_text = ", ".join(
            str(d)
            for d in detections
        )

        det_summary = (
            f"Visual Evidence "
            f"({media_type.capitalize()} "
            f"'{filename}'): "
            f"Detected objects -> "
            f"{detection_text}."
        )

        embedding = self.generate_embedding(
            det_summary
        )

        self.vector_store.add_item(
            text=det_summary,
            embedding=embedding,
            source=filename,
            doc_type="visual",
            metadata={
                "file": filename,
                "detections": detections,
                "media_type": media_type
            }
        )


    # =====================================================
    # QUESTION ANSWERING
    # =====================================================

    def answer_question(
        self,
        question: str
    ) -> dict:

        query_embedding = self.generate_embedding(
            question
        )

        # -------------------------------------------------
        # RETRIEVE TEXTUAL POLICIES
        # -------------------------------------------------

        text_matches = self.vector_store.search(
            query_embedding,
            top_k=3,
            doc_type_filter="text"
        )

        # -------------------------------------------------
        # RETRIEVE VISUAL EVIDENCE
        # -------------------------------------------------

        visual_matches = self.vector_store.search(
            query_embedding,
            top_k=2,
            doc_type_filter="visual"
        )

        # -------------------------------------------------
        # BUILD CONTEXT
        # -------------------------------------------------

        text_context = "\n".join(
            [
                f"[{doc['source']}]: {doc['text']}"
                for sim, doc in text_matches
                if sim > 0.05
            ]
        )

        visual_context = "\n".join(
            [
                f"[{doc['source']}]: {doc['text']}"
                for sim, doc in visual_matches
                if sim > 0.05
            ]
        )

        combined_context = (
            "=== TEXTUAL POLICIES ===\n"
            + (
                text_context
                or "No specific policy found."
            )
            + "\n\n=== VISUAL EVIDENCE ===\n"
            + (
                visual_context
                or "No recent media context uploaded."
            )
        )

        # -------------------------------------------------
        # RETRIEVED SNIPPETS
        # -------------------------------------------------

        retrieved_snippets = [

            {
                "source": doc["source"],
                "text": doc["text"],
                "similarity": round(sim, 2),
                "type": doc["type"]
            }

            for sim, doc in (
                text_matches + visual_matches
            )

            if sim > 0.05
        ]


        # =================================================
        # GEMINI ONLINE MODE
        # =================================================

        if client:

            prompt = f"""
You are Vision Desk AI's Safety Question Answering System.

Answer the user's question using ONLY the retrieved
context below.

[RETRIEVED CONTEXT]

{combined_context}

[USER QUESTION]

{question}

INSTRUCTIONS:

1. Base the answer strictly on the retrieved context.
2. Do not hallucinate.
3. Cite the relevant policy section.
4. Mention visual evidence when available.
5. Return ONLY valid JSON.

JSON FORMAT:

{{
    "answer": "Clear grounded answer",
    "supporting_evidence": [
        "Exact policy clause or evidence"
    ],
    "confidence": "High | Medium | Low",
    "has_violation_risk": true
}}
"""

            try:

                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                result = json.loads(
                    response.text
                )

                result["retrieved_context"] = (
                    retrieved_snippets
                )

                return result

            except Exception as e:

                print(
                    "[RAG System] Gemini generation "
                    f"failed: {e}"
                )


        # =================================================
        # LOCAL OFFLINE MODE
        # =================================================

        evidence = [
            doc["text"]
            for sim, doc in text_matches[:2]
            if sim > 0.05
        ]

        visual_evidence = [
            doc["text"]
            for sim, doc in visual_matches[:1]
            if sim > 0.05
        ]

        all_evidence = (
            evidence + visual_evidence
        )

        if not text_context and not visual_context:

            offline_answer = (
                "No relevant safety policies or "
                "visual evidence matches were found "
                "in the knowledge base."
            )

        else:

            offline_answer = (
                "Based on the retrieved workplace "
                "safety knowledge base:\n\n"
                + text_context[:800]
            )

        return {

            "answer": offline_answer,

            "supporting_evidence":
                all_evidence
                or ["Default Workplace Compliance Manual"],

            "confidence":
                "Local Offline Mode",

            "has_violation_risk": False,

            "retrieved_context":
                retrieved_snippets
        }


# =========================================================
# SINGLE GLOBAL RAG INSTANCE
# =========================================================

rag_system = RAGSystem()