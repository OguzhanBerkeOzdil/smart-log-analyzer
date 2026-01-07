import os
from typing import List
from dotenv import load_dotenv
from google import genai
from google.genai import types
from .models import LogEntry, ErrorGroup, AIAnalysisResult, ErrorAnalysisResult
from .interfaces import AnalyzerStrategy


load_dotenv()


class AIAnalyzer(AnalyzerStrategy[AIAnalysisResult]):
    """
    Uses Google Gemini to provide insights on the most frequent error.

    NOTE:
    This analyzer is intentionally NOT designed to work on raw log entries.
    It depends on the output of ErrorAnalyzer and must be executed after it.

    The analyze() method is implemented only to satisfy the AnalyzerStrategy
    interface contract and to prevent accidental misuse at runtime.
    """

    @property
    def name(self) -> str:
        return "AI Insight Analysis"

    def analyze(self, logs: List[LogEntry]) -> AIAnalysisResult:
        raise RuntimeError(
            "AIAnalyzer cannot analyze raw logs. " "It must be run after ErrorAnalyzer."
        )

    def analyze_from_error_result(
        self,
        error_result: ErrorAnalysisResult,
    ) -> AIAnalysisResult:

        if not error_result["top_errors"]:
            return {
                "kind": "ai",
                "top_error": None,
                "insight": "No errors found to analyze.",
            }

        top_error = error_result["top_errors"][0]
        insight = self.get_error_explanation(top_error)

        return {
            "kind": "ai",
            "top_error": top_error,
            "insight": insight,
        }

    def get_error_explanation(self, error: ErrorGroup) -> str:
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

            response = client.models.generate_content( # pyright: ignore[reportUnknownMemberType]
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
