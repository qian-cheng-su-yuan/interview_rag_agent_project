from __future__ import annotations

from typing import List, Tuple

import requests

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    """OpenAI-compatible chat completions client with local fallback."""

    def __init__(self) -> None:
        self.api_key = settings.llm_api_key.strip()
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model_name = settings.llm_model_name
        self.timeout = settings.llm_timeout

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[dict], temperature: float = 0.2) -> Tuple[str, bool]:
        if not self.enabled:
            return self._fallback_answer(messages), False

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip(), True
        except Exception as exc:  # noqa: BLE001
            logger.exception("LLM call failed, using fallback answer. error=%s", exc)
            return self._fallback_answer(messages), False

    def _fallback_answer(self, messages: List[dict]) -> str:
        user_message = messages[-1].get("content", "") if messages else ""
        context_marker = "【知识库片段】"
        if context_marker in user_message:
            context = user_message.split(context_marker, 1)[-1].strip()
            context = context[:900]
            return (
                "当前未配置大模型 API Key，以下为基于检索片段生成的本地演示回答：\n\n"
                f"{context}\n\n"
                "建议配置 .env 中的 LLM_API_KEY 后，再查看更自然的模型回答。"
            )
        return "当前未配置大模型 API Key，无法调用在线大模型。"
