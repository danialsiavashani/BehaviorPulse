import json
import logging

import httpx

from app.services.llm.base import LLMClient
from app.services.llm.fallback_client import FallbackClient
from app.services.llm.prompts import SYSTEM_PROMPT, build_user_prompt

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

logger = logging.getLogger("signaltally")


class DeepSeekClient(LLMClient):
    def __init__(self, api_key: str, model: str = "deepseek-v4-flash", timeout_seconds: float = 15.0):
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._fallback = FallbackClient()

    def summarize_observation_analysis(self, evidence_packet: dict) -> dict:
        response = httpx.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(evidence_packet)},
                ],
                "max_tokens": 600,
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        raw_content = response.json()["choices"][0]["message"]["content"]

        try:
            parsed = json.loads(raw_content)
            return {
                "summary": parsed["summary"],
                "prediction": parsed["prediction"],
                "recommendations": parsed.get("recommendations", []),
            }
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning(
                "DeepSeek response could not be parsed, using fallback summary: %s", exc
            )
            return self._fallback.summarize_observation_analysis(evidence_packet)