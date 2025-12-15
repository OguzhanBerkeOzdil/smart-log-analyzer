import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .models import LogEntry, ErrorGroup
from .interfaces import AnalyzerStrategy

load_dotenv()


class AIAnalyzer(AnalyzerStrategy):
    """
    Uses Google Gemini to provide insights on the most frequent error.
    """

    @property
    def name(self) -> str:
        return "AI Insight Analysis"

    def analyze(self, logs: List[LogEntry]) -> Dict[str, Any]:
        # 1. Identify the top error (reusing logic or relying on pre-calc could be better,
        # but for independence we calculate it here briefly)
        from collections import defaultdict

        counts = defaultdict(int)
        for entry in logs:
            if entry.level == "ERROR":
                counts[(entry.service, entry.message)] += 1

        if not counts:
            return {"ai_insight": "No errors found to analyze."}

        # Get top error
        (service, message), count = max(counts.items(), key=lambda x: x[1])
        top_error = ErrorGroup(service=service, message=message, count=count)

        # 2. Ask AI
        insight = self._get_error_explanation(top_error)

        return {"top_error_analyzed": top_error, "ai_insight": insight}

    def _get_error_explanation(self, error: ErrorGroup) -> str:
        API_KEY = os.getenv("GEMINI_API_KEY")
        MODEL = "gemini-2.0-flash"  # Updated to latest efficient model

        if not API_KEY:
            return "(!) AI features disabled: GEMINI_API_KEY not found."

        try:
            client = genai.Client(api_key=API_KEY)

            prompt = f"""
                I am a software engineer analyzing logs.
                I found this error occurring {error.count} times in the service '{error.service}':\n\n
                Error Message: "{error.message}"\n\n
                Explain what this error typically means and suggest 2 common ways to fix it.
                Keep it short (max 3 sentences).
            """

            system_instruction = "You are an expert software engineer specializing in log analysis and debugging."

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
