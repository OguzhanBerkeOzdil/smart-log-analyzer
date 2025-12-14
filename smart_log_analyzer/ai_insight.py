import os
import google.generativeai as genai
from dotenv import load_dotenv
from .models import ErrorGroup

load_dotenv()

def get_error_explanation(error: ErrorGroup) -> str:
    """
    Sends the error message to Google Gemini to get a debugging tip.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "(!) AI features disabled: GEMINI_API_KEY not found in environment variables."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            f"I am a software engineer analyzing logs. "
            f"I found this error occurring {error.count} times in the service '{error.service}':\n\n"
            f"Error Message: \"{error.message}\"\n\n"
            f"Explain what this error typically means and suggest 2 common ways to fix it. "
            f"Keep it short (max 3 sentences)."
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"(!) Failed to get AI insight: {e}"