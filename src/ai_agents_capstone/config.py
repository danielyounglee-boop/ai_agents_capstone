"""Configuration and environment settings for EduPathway AI."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Application configuration and model settings."""

    # GCP Project & Region
    project_id: str = os.getenv("GCP_PROJECT_ID", "ai-in-5-days-dyl-temp")
    location: str = os.getenv("GCP_LOCATION", "us-central1")
    use_vertex_ai: bool = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "true").lower() == "true"

    # API Keys
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", None)

    # Model Aliases (ADK 2.0 / Gemini Models)
    model_fast: str = os.getenv("MODEL_FAST", "gemini-2.0-flash")
    model_reasoning: str = os.getenv("MODEL_REASONING", "gemini-2.0-pro")
    model_tutor: str = os.getenv("MODEL_TUTOR", "gemini-2.0-flash")

    # App Data & Traces Storage
    data_dir: str = os.getenv("EDUPATHWAY_DATA_DIR", "data")
    traces_dir: str = os.getenv("EDUPATHWAY_TRACES_DIR", "traces")
    profiles_dir: str = os.getenv("EDUPATHWAY_PROFILES_DIR", "data/profiles")


config = AppConfig()
