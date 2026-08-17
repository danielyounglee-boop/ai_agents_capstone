"""Core Agent Implementation using the Google GenAI SDK."""

import os
from google import genai
from google.genai import types


def get_client() -> genai.Client:
    """Instantiate and return the Google GenAI client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")
    return genai.Client(api_key=api_key)


def run_agent_turn(client: genai.Client, prompt: str, system_instruction: str = "You are a helpful and intelligent AI agent.") -> str:
    """Execute a single reasoning/generation turn with Gemini 2.5 Flash."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        ),
    )
    return response.text
