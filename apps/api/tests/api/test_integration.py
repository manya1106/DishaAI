from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
    assert "data_mode" in data


def test_meta_endpoint():
    resp = client.get("/api/v1/meta")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["cities"]) >= 1
    assert data["cities"][0]["city_id"] == "blr"
    assert len(data["categories"]) == 3
    assert len(data["signals"]) == 9
    assert "default_weights" in data


def test_analyses_crud_flow():
    # 1. POST analysis
    req_payload = {
        "city_id": "blr",
        "category_id": "cafe",
        "budget_tier": "medium",
        "top_n": 10
    }
    resp = client.post("/api/v1/analyses", json=req_payload)
    assert resp.status_code == 200
    analysis = resp.json()
    analysis_id = analysis["analysis_id"]
    assert len(analysis["locations"]) == 10
    assert len(analysis["evidence"]) >= 10
    loc1 = analysis["locations"][0]
    loc1_id = loc1["location_id"]

    # 2. GET analysis by ID
    get_resp = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["analysis_id"] == analysis_id

    # 3. GET location report
    rep_resp = client.get(f"/api/v1/analyses/{analysis_id}/locations/{loc1_id}")
    assert rep_resp.status_code == 200
    rep_data = rep_resp.json()
    assert rep_data["location"]["location_id"] == loc1_id
    assert len(rep_data["location"]["signals"]) == 9

    # 4. POST compare
    loc2_id = analysis["locations"][1]["location_id"]
    comp_resp = client.post(
        f"/api/v1/analyses/{analysis_id}/compare",
        json={"location_ids": [loc1_id, loc2_id]}
    )
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert len(comp_data["locations"]) == 2
    assert len(comp_data["signal_deltas"]) == 9

    # 5. POST chat (deterministic)
    chat_resp = client.post(
        f"/api/v1/analyses/{analysis_id}/chat",
        json={
            "message": "Why does #1 lead the ranking?",
            "selected_location_ids": [loc1_id],
            "mode": "deterministic"
        }
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["verification"]["status"] in ["verified", "partially_verified"]
    assert len(chat_data["blocks"]) >= 1

    # 6. POST chat (trap refusal)
    trap_resp = client.post(
        f"/api/v1/analyses/{analysis_id}/chat",
        json={
            "message": "What is the monthly rent in rupees for #1?",
            "selected_location_ids": [loc1_id],
            "mode": "auto"
        }
    )
    assert trap_resp.status_code == 200
    trap_data = trap_resp.json()
    assert trap_data["mode"] == "refused_insufficient_data"
    assert trap_data["uncertainty"]["insufficient_data"] is True


def test_trust_stats_endpoint():
    resp = client.get("/api/v1/trust/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["latest_eval"] is not None
    assert data["latest_eval"]["metrics"]["cases_total"] == 21
    assert data["latest_eval"]["metrics"]["leaked_unsupported"] == 0
    assert len(data["verifier_rules_summary"]) == 9
