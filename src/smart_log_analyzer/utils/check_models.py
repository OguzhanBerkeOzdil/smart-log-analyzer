import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: GEMINI_API_KEY not set.")
else:
    client = genai.Client(api_key=API_KEY)
    print("Checking available models for your API key...\n")
    try:
        for model in client.models.list():
            if model.supported_actions and "generateContent" in model.supported_actions:
                print(f" - {model.name}")
    except Exception as e:
        print(f"Error connecting to Google API: {e}")
