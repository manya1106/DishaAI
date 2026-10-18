import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def _no_live_llm_by_default(monkeypatch):
    """The real apps/api/.env has LLM_ENABLED=true so the app can talk to a
    locally-running Ollama instance. Tests should not silently depend on
    that external service being up (slow, flaky, not available in CI) —
    default every test to LLM_ENABLED=False; a test that wants to exercise
    real-or-mocked LLM behavior opts back in explicitly via its own
    monkeypatch.setattr(..., "LLM_ENABLED", True), which simply overrides
    this for that test's duration.
    """
    monkeypatch.setattr(settings, "LLM_ENABLED", False)
