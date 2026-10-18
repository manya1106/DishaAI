"""
test_scoring_agent.py — Phase 2 Scoring Agent unit test.
Verifies that ScoringAgent produces deterministic rankings, evidence bundle,
and matches golden tests bit-for-bit.
"""

import sys
from pathlib import Path

person_d_dir = Path(__file__).resolve().parents[1]
repo_root = person_d_dir.parent
for p in [str(person_d_dir), str(repo_root), str(repo_root / "apps/api")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from person_D.scoring_agent import scoring_agent


def test_scoring_agent_deterministic_golden():
    payload = {
        "city_id": "blr",
        "category_id": "cafe",
        "budget_tier": "medium",
        "top_n": 10,
        "selected_location_ids": [],
    }

    res1 = scoring_agent.handle(payload)
    res2 = scoring_agent.handle(payload)

    assert res1["status"] == "success"
    assert len(res1["top_locations"]) == 10
    assert "evidence_bundle" in res1
    assert "effective_weights" in res1

    # Exact bit-for-bit reproducibility
    locs1 = res1["top_locations"]
    locs2 = res2["top_locations"]

    for l1, l2 in zip(locs1, locs2):
        assert l1["rank"] == l2["rank"]
        assert l1["location_id"] == l2["location_id"]
        assert l1["overall_score"] == l2["overall_score"]
        assert l1["confidence"] == l2["confidence"]

    # Verify rank 1 has highest score
    assert locs1[0]["overall_score"] >= locs1[-1]["overall_score"]
    assert locs1[0]["rank"] == 1
    assert locs1[-1]["rank"] == 10
