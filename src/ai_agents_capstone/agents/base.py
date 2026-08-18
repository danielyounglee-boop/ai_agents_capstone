"""Base Agent abstraction with tool telemetry, LLM invocation, and structured output parsing."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

from ..config import config
from ..observability.tracer import Tracer

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """Abstract Base Agent providing tool integration, telemetry tracing, and LLM inference."""

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model_name: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.model_name = model_name or config.model_fast
        self.tools = tools or []
        self._tool_map = {t.__name__: t for t in self.tools}

    def execute_tool(self, tool_name: str, inputs: Dict[str, Any], tracer: Optional[Tracer] = None) -> Any:
        """Execute a registered tool and record telemetry with latency and status."""
        tool_fn = self._tool_map.get(tool_name)
        if not tool_fn:
            err = f"Tool '{tool_name}' not registered on agent '{self.name}'."
            if tracer:
                tracer.record_tool_call(tool_name, inputs, None, 0.0, success=False, error_message=err, agent_name=self.name)
            raise ValueError(err)

        start_time = time.perf_counter()
        try:
            result = tool_fn(**inputs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            if tracer:
                tracer.record_tool_call(tool_name, inputs, result, elapsed_ms, success=True, agent_name=self.name)
            return result
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            err_msg = str(e)
            if tracer:
                tracer.record_tool_call(tool_name, inputs, None, elapsed_ms, success=False, error_message=err_msg, agent_name=self.name)
            raise

    def call_gemini(
        self,
        prompt: str,
        schema: Optional[Type[T]] = None,
        tracer: Optional[Tracer] = None,
    ) -> str:
        """Call Gemini model using Google GenAI / ADK client with graceful offline fallback."""
        start_time = time.perf_counter()
        prompt_tokens = len(prompt.split()) + len(self.system_prompt.split())

        try:
            # Attempt real Google GenAI / Vertex AI call
            from google import genai
            from google.genai import types

            if config.gemini_api_key:
                client = genai.Client(api_key=config.gemini_api_key)
            else:
                client = genai.Client(
                    vertexai=config.use_vertex_ai,
                    project=config.project_id,
                    location=config.location,
                )

            config_params = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=0.2,
            )
            if schema:
                config_params.response_mime_type = "application/json"
                config_params.response_schema = schema

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config_params,
            )
            raw_text = response.text or ""
            completion_tokens = len(raw_text.split())
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if tracer:
                tracer.record_agent_invocation(
                    agent_name=self.name,
                    model_name=self.model_name,
                    duration_ms=elapsed_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )
            return raw_text

        except Exception as e:
            # Graceful rule-based simulation / offline fallback for local verification
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            simulated_response = self._generate_simulated_fallback(prompt, schema)
            completion_tokens = len(simulated_response.split())

            if tracer:
                tracer.record_agent_invocation(
                    agent_name=self.name,
                    model_name=f"{self.model_name} (simulated fallback)",
                    duration_ms=elapsed_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )
            return simulated_response

    @abstractmethod
    def _generate_simulated_fallback(self, prompt: str, schema: Optional[Type[BaseModel]]) -> str:
        """Deterministic simulation fallback when network or API credentials are unconfigured."""
        pass
