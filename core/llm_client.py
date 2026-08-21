"""LLM adapters for the diagnostic research prototype.

The production adapter is OpenAI-compatible and uses only Python's standard
library. It can target a hosted OpenAI-compatible endpoint or a local server
such as Ollama/LM Studio. The rest of the system depends only on the
StructuredLLMClient protocol.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol


class StructuredLLMClient(Protocol):
    def complete_structured(self, system: str, user: str, tool_name: str,
                            tool_description: str, input_schema: dict) -> dict: ...


@dataclass
class OpenAICompatibleLLMClient:
    """Minimal dependency-free client for OpenAI-compatible chat APIs."""
    base_url: str = field(default_factory=lambda: os.getenv("DIAG_LLM_BASE_URL", "https://api.openai.com/v1"))
    api_key: str = field(default_factory=lambda: os.getenv("DIAG_LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    model: str = field(default_factory=lambda: os.getenv("DIAG_LLM_MODEL", "gpt-4.1-mini"))
    timeout: int = 90

    def complete_structured(self, system: str, user: str, tool_name: str,
                            tool_description: str, input_schema: dict) -> dict:
        schema_name = tool_name.replace("-", "_")
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "strict": True, "schema": input_schema},
            },
        }
        data = json.dumps(payload).encode("utf-8")
        url = self.base_url.rstrip("/") + "/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = "Bearer " + self.api_key
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"LLM HTTP {exc.code}: {detail[:1000]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach LLM endpoint {url}: {exc.reason}") from exc

        try:
            content = body["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"LLM returned an unexpected structured response: {body}") from exc


AnthropicLLMClient = OpenAICompatibleLLMClient


@dataclass
class ScriptedLLMClient:
    responses: list[dict]
    calls: list[dict] = field(default_factory=list)
    _index: int = 0

    def complete_structured(self, system: str, user: str, tool_name: str,
                            tool_description: str, input_schema: dict) -> dict:
        self.calls.append({"system": system, "user": user, "tool_name": tool_name, "input_schema": input_schema})
        if self._index >= len(self.responses):
            raise AssertionError("ScriptedLLMClient ran out of scripted responses")
        response = self.responses[self._index]
        self._index += 1
        return response
