import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ..core.models import ErrorGroup

load_dotenv()


def get_error_explanation(error: ErrorGroup) -> str:
    """
    Sends the error message to Google Gemini to get a debugging tip.
    """

    API_KEY = os.getenv("GEMINI_API_KEY")  # inside function to allow mocking in tests
    MODEL = "gemini-2.5-flash"

    if not API_KEY:
        return "(!) AI features disabled: GEMINI_API_KEY not found in environment variables."

    try:
        client = genai.Client(api_key=API_KEY)

        prompt = f"""
            I am a software engineer analyzing logs.
            I found this error occurring {error.count} times in the service '{error.service}':\n\n
            Error Message: "{error.message}"\n\n
            Explain what this error typically means and suggest 2 common ways to fix it.
            Keep it short (max 3 sentences).
        """

        system_instruction = f"""
            You are an expert software engineer specializing in log analysis and debugging.
            Provide concise, clear explanations and practical troubleshooting steps.
        """

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )

        return str(response.text)

    except Exception as e:
        return f"(!) Failed to get AI insight: {e}"
