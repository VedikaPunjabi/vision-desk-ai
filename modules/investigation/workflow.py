from langgraph.graph import StateGraph, END

from .state import InvestigationState
from .agents import (
    query_analysis_agent,
    document_retrieval_agent,
    visual_analysis_agent,
    evidence_validation_agent,
    reasoning_agent,
    report_generation_agent,
)


def human_review_agent(state: InvestigationState):
    """
    Prepare the report for human review.

    The actual approval is performed by the Vision Desk
    frontend through the /api/investigate endpoint.
    """

    return {
        "human_approved": False,
        "reviewer_feedback": "Awaiting human review."
    }


def build_investigation_workflow():

    workflow = StateGraph(InvestigationState)

    # -----------------------------------------------------
    # Agents
    # -----------------------------------------------------

    workflow.add_node(
        "query_analysis",
        query_analysis_agent
    )

    workflow.add_node(
        "document_retrieval",
        document_retrieval_agent
    )

    workflow.add_node(
        "visual_analysis",
        visual_analysis_agent
    )

    workflow.add_node(
        "evidence_validation",
        evidence_validation_agent
    )

    workflow.add_node(
        "reasoning",
        reasoning_agent
    )

    workflow.add_node(
        "report_generation",
        report_generation_agent
    )

    workflow.add_node(
        "human_review",
        human_review_agent
    )

    # -----------------------------------------------------
    # Workflow
    # -----------------------------------------------------

    workflow.set_entry_point("query_analysis")

    workflow.add_edge(
        "query_analysis",
        "document_retrieval"
    )

    workflow.add_edge(
        "document_retrieval",
        "visual_analysis"
    )

    workflow.add_edge(
        "visual_analysis",
        "evidence_validation"
    )

    workflow.add_edge(
        "evidence_validation",
        "reasoning"
    )

    workflow.add_edge(
        "reasoning",
        "report_generation"
    )

    workflow.add_edge(
        "report_generation",
        "human_review"
    )

    workflow.add_edge(
        "human_review",
        END
    )

    return workflow.compile()