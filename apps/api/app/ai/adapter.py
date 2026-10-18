import asyncio
import json

import httpx

from ..config import settings
from ..logging import logger
from ..schemas.chat import LLMOutput

_POLARITY_WORDS = {"strength", "weakness", "neutral"}


def _coerce_claim_fields(parsed: dict) -> dict:
    """Fix a specific, predictable small-model mistake: some open-weight
    models (observed: qwen2.5:7b-instruct) put the polarity word into
    "type" instead of "polarity", despite an explicit worked example in
    the prompt. Rather than depend on perfect instruction-following from
    a 7B model, detect and correct this one known failure shape before
    strict schema validation — the verifier downstream still checks the
    actual content, this only repairs which JSON key a value landed in.
    """
    for block in parsed.get("blocks", []):
        for claim in block.get("claims", []):
            claim_type = claim.get("type")
            if claim_type in _POLARITY_WORDS:
                claim["polarity"] = claim_type
                claim["type"] = "fact"
    return parsed


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
                        parsed = _coerce_claim_fields(json.loads(content))
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

    async def generate_json(
        self, system_prompt: str, user_prompt: str, timeout_s: float | None = None, max_attempts: int = 2
    ) -> dict | None:
        """Generic JSON completion for callers that don't use the chat
        LLMOutput schema (e.g. ai/score_review.py). Mirrors generate()'s
        request/retry handling but returns the raw parsed dict instead of
        validating into LLMOutput. `timeout_s` and `max_attempts` let a
        latency-sensitive caller (score_review needs the whole analysis
        request to stay well under ~10s) fail fast and fall back instead
        of waiting out the full chat timeout and a retry.
        """
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
        effective_timeout = timeout_s if timeout_s is not None else self.timeout

        for attempt in range(max_attempts):
            try:
                async with httpx.AsyncClient(timeout=effective_timeout) as client:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        return json.loads(content)
                    elif resp.status_code in [429, 500, 502, 503] and attempt < max_attempts - 1:
                        await asyncio.sleep(1.0)
                    else:
                        logger.warning(f"LLM API returned status {resp.status_code}: {resp.text[:200]}")
                        return None
            except (httpx.HTTPError, json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"LLM generate_json attempt {attempt + 1} failed: {e!s}")
                if attempt < max_attempts - 1:
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
