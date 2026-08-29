from typing import TypedDict, List, Dict, Any


class InvestigationState(TypedDict, total=False):
    # Original investigation request
    query: str

    # Query Analysis Agent output
    analyzed_query: str
    search_queries: List[str]

    # Document Retrieval Agent output
    retrieved_documents: List[Dict[str, Any]]

    # Visual Analysis Agent output
    visual_evidence: List[Dict[str, Any]]

    # Evidence Validation Agent output
    validated_evidence: List[Dict[str, Any]]
    evidence_conflicts: List[str]

    # Reasoning Agent output
    findings: List[Dict[str, Any]]
    reasoning: str

    # Report Generation Agent output
    report: str

    # Human review
    human_approved: bool
    reviewer_feedback: str