import asyncio
import json

import httpx

from ..config import settings
from ..logging import logger
from ..schemas.chat import LLMOutput


class LLMAdapter:
    def __init__(self):
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.api_key = settings.LLM_API_KEY
        self.model = settings.LLM_MODEL
        self.timeout = float(settings.LLM_TIMEOUT_S)

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMOutput | None:
        if not settings.LLM_ENABLED or not self.api_key:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"}
        }

        url = f"{self.base_url}/chat/completions"

        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        parsed = json.loads(content)
                        return LLMOutput.model_validate(parsed)
                    elif resp.status_code in [429, 500, 502, 503] and attempt == 0:
                        await asyncio.sleep(1.0)
                    else:
                        logger.warning(f"LLM API returned status {resp.status_code}: {resp.text[:200]}")
                        return None
            except (httpx.HTTPError, json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"LLM request attempt {attempt + 1} failed: {e!s}")
                if attempt == 0:
                    await asyncio.sleep(0.5)
                else:
                    return None

        return None


class FakeLLMAdapter:
    """Mock adapter for deterministic testing of various LLM behavior scenarios."""
    def __init__(self, mode: str = "valid"):
        self.mode = mode

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMOutput | None:
        if self.mode == "timeout":
            await asyncio.sleep(0.1)
            raise TimeoutError("Simulated LLM timeout")
        elif self.mode == "invalid_json":
            raise ValueError("Malformed JSON from LLM")
        elif self.mode == "rate_limited":
            return None
        elif self.mode == "insufficient_data":
            return LLMOutput(
                blocks=[],
                insufficient_data=True,
                missing_reason="Requested unavailable private financial metrics."
            )
        elif self.mode == "wrong_number":
            # Output containing an ungrounded fabricated number (e.g. 999.9)
            return LLMOutput(
                blocks=[{
                    "text": "Zone ranks #1 with an invented score of 999.9.",
                    "claims": [{
                        "type": "score",
                        "location_ids": [],
                        "evidence_ids": ["ev_001"],
                        "numbers": [999.9],
                        "polarity": "strength"
                    }]
                }]
            )
        else:
            return None


llm_adapter = LLMAdapter()
