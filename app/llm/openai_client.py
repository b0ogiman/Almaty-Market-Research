"""OpenAI API wrapper."""

import json
from typing import Any, Optional

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger("llm.openai")


class OpenAIClient:
    """Async OpenAI API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.max_tokens = max_tokens or settings.openai_max_tokens

    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        response_format: Optional[dict[str, str]] = None,
    ) -> str:
        """Send chat completion request."""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": self.max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format
            resp = await client.chat.completions.create(**kwargs)
            content = resp.choices[0].message.content
            return content or ""
        except Exception as e:
            logger.exception("OpenAI request failed: %s", str(e))
            raise

    async def complete_json(
        self,
        messages: list[dict[str, str]],
        schema: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Request JSON response and validate.
        Uses response_format json_object for JSON output.
        """
        fmt = {"type": "json_object"}
        content = await self.complete(messages, response_format=fmt)
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning("Invalid JSON from LLM: %s", str(e))
            raise ValueError(f"Invalid JSON response: {e}") from e
