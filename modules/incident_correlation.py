import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Automatically reads GEMINI_API_KEY from your .env file
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class MultimodalIntelligenceEngine:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name

    def analyze_incident(self, detection_summary: str, retrieved_rules: str) -> dict:
        """
        Module 3: Multimodal Intelligence Engine
        Correlates visual detection data with retrieved document rules.
        """
        prompt = f"""
        You are an AI Workplace Safety and Compliance Officer.

        [VISUAL DETECTION (Module 1)]
        {detection_summary}

        [SAFETY POLICIES RETRIEVED (Module 2)]
        {retrieved_rules}

        TASK:
        Correlate the visual detection with the safety policies.
        Return ONLY a valid JSON response with the following schema:
        {{
          "violation_detected": true,
          "rule_violated": "Cite exact clause/rule from the policy context",
          "severity": "Low | Medium | High | Critical",
          "explanation": "Brief, grounded evidence explaining the violation",
          "recommended_action": "Immediate corrective measure"
        }}
        """
        
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        return json.loads(response.text)

if __name__ == "__main__":
    engine = MultimodalIntelligenceEngine()
    
    mock_detection = "Person detected near heavy machinery without safety helmet at 10:15 AM."
    mock_rules = "Section 4.1: Mandatory Hard Hats. All personnel working within 5 meters of active machinery must wear a certified hard hat."

    print("\n--- Running Module 3 Test ---")
    result = engine.analyze_incident(mock_detection, mock_rules)
    print(json.dumps(result, indent=2))



    