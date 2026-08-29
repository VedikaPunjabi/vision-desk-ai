from typing import Dict, Any
import os

from langchain_google_genai import ChatGoogleGenerativeAI


# =========================================================
# GEMINI / MOCK AI SETUP
# =========================================================

llm = None

# Use Gemini only if an API key is available.
# Otherwise Module 5 runs in demo/mock mode.
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if api_key:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=api_key,
    )


def generate_response(prompt: str) -> str:
    """
    Uses Gemini when an API key is available.
    Otherwise returns a useful local demonstration response.
    """

    if llm is not None:
        return llm.invoke(prompt).content

    prompt_lower = prompt.lower()

    # Query Analysis
    if "query analysis agent" in prompt_lower:
        return """
QUERY ANALYSIS

Incident:
A worker was observed near machinery without proper PPE.

Key investigation elements:
- Worker safety
- PPE compliance
- Machinery-related hazards
- Applicable workplace safety policy

Search requirements:
- PPE requirements
- Machinery safety rules
- Required protective equipment
- Workplace safety violations
"""

    # Evidence Validation
    if "evidence validation agent" in prompt_lower:
        return """
EVIDENCE VALIDATION

Relevant evidence:
- Investigation request describing missing PPE
- Workplace safety policy evidence retrieved by the system
- Visual evidence, if an image is supplied

Validation:
The reported PPE issue is relevant to the investigation.

Confidence:
Moderate, because the current demonstration does not include
an actual image or verified employee statement.

Conflict:
No direct evidence conflict was identified.
"""

    # Reasoning
    if "reasoning agent" in prompt_lower:
        return """
REASONING AND FINDINGS

Finding:
The reported incident indicates a potential PPE compliance
violation.

Applicable area:
Workplace PPE and machinery safety requirements.

Severity:
Moderate potential safety risk.

Reason:
Failure to use required PPE near machinery can increase the
risk of workplace injury.

Recommended action:
Verify the applicable policy, confirm the incident evidence,
and reinforce PPE compliance before taking disciplinary action.
"""

    # Report Generation
    if "report generation agent" in prompt_lower:
        return """
INVESTIGATION REPORT

1. Investigation Summary
A worker was reportedly observed near machinery without
proper personal protective equipment.

2. Evidence Reviewed
- Investigation request
- Retrieved workplace safety information
- Visual evidence, if provided

3. Relevant Policy / Rules
PPE requirements and machinery safety procedures should be
checked against the organization's applicable safety policy.

4. Findings
The incident represents a potential PPE compliance violation.

5. Severity
Moderate potential safety risk.

6. Recommended Corrective Actions
- Verify the incident and applicable policy.
- Ensure required PPE is available and used.
- Provide safety guidance or refresher training.
- Document the final investigation decision.

7. Limitations
The demonstration does not have a configured Gemini API,
actual employee statements, or verified incident imagery.
Therefore, the findings require human review.
"""

    # Fallback
    return """
MOCK AI ANALYSIS

The investigation workflow was executed successfully.

The available evidence should be reviewed against the
applicable workplace safety policies.

Human review is required before a final decision.
"""
# =========================================================
# 1. QUERY ANALYSIS AGENT
# =========================================================

def query_analysis_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    query = state.get("query", "")

    prompt = f"""
You are the Query Analysis Agent in a workplace investigation
system.

Analyze the following investigation request:

{query}

Identify:

1. Main incident
2. Important entities
3. Evidence that should be searched
4. Relevant workplace safety topics
5. Possible policy areas

Return a concise investigation search plan.
"""

    response_text = generate_response(prompt)

    return {
        "analyzed_query": response_text,
        "search_queries": [
            query,
            "workplace safety PPE machinery policy",
            "PPE compliance safety requirements",
        ],
    }


# =========================================================
# 2. DOCUMENT RETRIEVAL AGENT
# =========================================================

def document_retrieval_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    queries = state.get(
        "search_queries",
        [state.get("query", "")]
    )

    documents = []

    try:
        # Lazy import.
        # This prevents Module 2 dependencies from crashing
        # Module 5 during startup.
        from ..vector_store import search_chunks

        for query in queries:

            try:
                results = search_chunks(
                    query,
                    n_results=5
                )

                if isinstance(results, list):
                    documents.extend(results)

                elif results:
                    documents.append(results)

            except Exception as e:

                documents.append({
                    "query": query,
                    "status": "Retrieval error",
                    "error": str(e)
                })

    except Exception as e:

        documents.append({
            "status": "Document retrieval unavailable",
            "reason": str(e)
        })

    return {
        "retrieved_documents": documents
    }


# =========================================================
# 3. VISUAL ANALYSIS AGENT
# =========================================================

def visual_analysis_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    query = state.get("query", "")

    image_path = None

    # Optional image path format:
    #
    # image_path: C:\path\image.jpg
    #
    if "image_path:" in query:

        image_path = query.split(
            "image_path:",
            1
        )[1].strip()

    # No image supplied
    if not image_path:

        return {
            "visual_evidence": [
                {
                    "status": "No image supplied",
                    "detections": []
                }
            ]
        }

    # Image path supplied but doesn't exist
    if not os.path.exists(image_path):

        return {
            "visual_evidence": [
                {
                    "status": "Image not found",
                    "image_path": image_path,
                    "detections": []
                }
            ]
        }

    try:

        # Lazy import of Module 1.
        # This prevents the Torch/YOLO DLL issue from
        # crashing Module 5 when no image is being analyzed.
        from ..vision_detector import run_detection

        output = run_detection(
            image_path,
            "module5_output"
        )

        return {
            "visual_evidence": [
                {
                    "status": "Visual analysis completed",
                    "image_path": image_path,
                    "detections": output
                }
            ]
        }

    except Exception as e:

        return {
            "visual_evidence": [
                {
                    "status": "Visual analysis failed",
                    "image_path": image_path,
                    "error": str(e)
                }
            ]
        }


# =========================================================
# 4. EVIDENCE VALIDATION AGENT
# =========================================================

def evidence_validation_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    documents = state.get(
        "retrieved_documents",
        []
    )

    visual = state.get(
        "visual_evidence",
        []
    )

    prompt = f"""
You are the Evidence Validation Agent in a workplace
safety investigation.

Investigation:

{state.get("query", "")}

Retrieved document evidence:

{documents}

Visual evidence:

{visual}

Validate the available evidence.

Determine:

1. Which evidence is relevant?
2. Which evidence is reliable?
3. Which evidence is uncertain?
4. Are there conflicts between evidence sources?
5. What evidence can safely be used for reasoning?

Do not invent evidence.
Clearly identify uncertainty.
"""

    response_text = generate_response(prompt)

    return {
        "validated_evidence": [
            {
                "validation": response_text,
                "documents": documents,
                "visual": visual
            }
        ],
        "evidence_conflicts": []
    }


# =========================================================
# 5. REASONING AGENT
# =========================================================

def reasoning_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    validated_evidence = state.get(
        "validated_evidence",
        []
    )

    prompt = f"""
You are the Reasoning Agent for a workplace safety
investigation.

Investigation:

{state.get("query", "")}

Validated evidence:

{validated_evidence}

Reason over the available evidence.

Determine:

1. What happened?
2. What evidence supports the finding?
3. Which safety policy or rule may apply?
4. Was there a likely violation?
5. What is the severity?
6. What corrective action is appropriate?

Do not invent facts.
Clearly identify uncertainty.
"""

    response_text = generate_response(prompt)

    return {
        "reasoning": response_text,

        "findings": [
            {
                "analysis": response_text
            }
        ]
    }


# =========================================================
# 6. REPORT GENERATION AGENT
# =========================================================

def report_generation_agent(
    state: Dict[str, Any]
) -> Dict[str, Any]:

    prompt = f"""
You are the Report Generation Agent for a workplace
investigation system.

Create a professional investigation report.

Investigation:

{state.get("query", "")}

Evidence:

{state.get("validated_evidence", [])}

Reasoning:

{state.get("reasoning", "")}

The report must contain:

1. Investigation Summary
2. Evidence Reviewed
3. Relevant Policy / Rules
4. Findings
5. Severity
6. Recommended Corrective Actions
7. Limitations / Uncertainty

Only use information supported by the investigation.
Do not invent facts.
"""

    response_text = generate_response(prompt)

    return {
        "report": response_text
    }