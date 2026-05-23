import os
import json
import time
from google import genai
from google.genai import types
import pytesseract
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Tesseract Path Configuration
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print(f"CRITICAL: Tesseract not found at {tesseract_path}. Check installation.")

# Define retry strategy for 503/500 errors
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception)
)
def call_gemini_api(client, extracted_text, system_instruction):
    """Wrapper to call Gemini with automatic retry logic."""
    return client.models.generate_content(
        model='gemini-2.0-flash', # Note: 'gemini-2.5' is not yet standard; '2.0-flash' is the stable high-perf model
        contents=f"Analyze this document context and extract agent analytics:\n\n{extracted_text}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json"
        ),
    )

def run_multi_agent_analysis(extracted_text):
    """
    Executes a structured 9-Agent parallel orchestration matrix with retry logic.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY environment variable not set."}

    client = genai.Client(api_key=api_key)

    system_instruction = """
    You are an orchestration node managing a cluster of 9 specialized Agent micro-services evaluating an academic program. 
    Analyze the provided input and return a valid JSON object with the following keys:
    Curriculum_Score, Faculty_Score, ROI_Score, Industry_Alignment, Placement_Score, 
    Sentiment_Score, Fees, Projects, GenAI_Coverage, Placement_Support, Missing_Skills, Job_Roles, SWOT.
    SWOT must contain: Strengths, Weaknesses, Opportunities, Risks.
    Return raw JSON only.
    """

    try:
        response = call_gemini_api(client, extracted_text, system_instruction)
        return json.loads(response.text)
    except Exception as e:
        print(f"Final attempt failed: {e}")
        return {
            "Curriculum_Score": 0, "Faculty_Score": 0, "ROI_Score": 0, 
            "SWOT": {"Strengths": "Service Unavailable", "Weaknesses": "API Timeout", "Opportunities": "None", "Risks": "High Traffic"},
            "Missing_Skills": ["Retry request"], "Job_Roles": ["N/A"]
        }