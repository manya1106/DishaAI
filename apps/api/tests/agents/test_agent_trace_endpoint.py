from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_agent_trace_endpoint_returns_handoffs_after_chat():
    analysis_resp = client.post(
        "/api/v1/analyses",
        json={"city_id": "blr", "category_id": "cafe", "budget_tier": "medium", "top_n": 5},
    )
    analysis = analysis_resp.json()
    analysis_id = analysis["analysis_id"]
    loc1_id = analysis["locations"][0]["location_id"]

    chat_resp = client.post(
        f"/api/v1/analyses/{analysis_id}/chat",
        json={
            "message": "Why does #1 lead the ranking?",
            "selected_location_ids": [loc1_id],
            "mode": "deterministic",
        },
    )
    trace_id = chat_resp.json()["trace_id"]

    trace_resp = client.get(f"/api/v1/trust/agent-trace/{trace_id}")
    assert trace_resp.status_code == 200
    data = trace_resp.json()
    assert data["trace_id"] == trace_id
    assert [h["recipient"] for h in data["handoffs"]] == ["verifier", "narrator", "verifier"]
    assert all(h["sender"] == "orchestrator" for h in data["handoffs"])


def test_agent_trace_endpoint_404_for_unknown_trace():
    resp = client.get("/api/v1/trust/agent-trace/does-not-exist")
    assert resp.status_code == 404
