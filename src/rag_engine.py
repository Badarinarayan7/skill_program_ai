import os
from google import genai
from google.genai import types

def query_program_mentor(user_query, current_program="Selected Program", pdf_text=""):
    """
    Core RAG connection engine that forces the Gemini 2.5 Flash model to answer 
    questions using strictly the parsed context of the selected academic program.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ **System Notification:** Please set your `GEMINI_API_KEY` environment variable in your terminal to talk to the live AI Mentor!"
        
    client = genai.Client(api_key=api_key)
    
    system_instruction = f"""
    You are an elite academic counselor and skill analysis platform named 'SkillProgram AI Mentor'[cite: 4, 259].
    The user is evaluating an educational program/resource titled: '{current_program}'.
    
    Here is the comprehensive text data extracted from the source material (brochures, syllabi, matrices, or URLs)[cite: 6, 43]:
    ---
    {pdf_text if pdf_text.strip() else 'No specific background content data parsed yet.'}
    ---
    
    Your goal is to answer the user's questions or solve their problems intelligently by locking your focus onto the extracted text data above. 
    Be highly direct, accurate to the facts inside the material, and prioritize extracting exact context definitions. 
    Always start your response with the emoji 💡.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
        )
        return response.text
    except Exception as e:
        return f"💡 **AI Mentor error:** I ran into a connection issue analyzing your request. Details: {e}"