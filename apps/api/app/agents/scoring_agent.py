"""Scoring Agent: wraps the deterministic 9-signal scoring engine.

Wraps scoring/engine.py and data/loader.py unchanged - see plan.md
§4.1. Transparently backed by Postgres (real OSM data for all of
Bengaluru) or the JSON snapshot fallback, depending on DATA_MODE;
callers never need to know which.
"""

from ..data.loader import loader
from ..schemas.analysis import LocationResult
from ..scoring.engine import scoring_engine


class ScoringAgent:
    def score(
        self,
        city_id: str,
        category_id: str,
        budget_tier: str,
        weight_overrides: dict[str, float] | None = None,
        top_n: int = 10,
    ) -> tuple[list[LocationResult], dict[str, float]]:
        snapshot = loader.get_snapshot(city_id)
        cells = snapshot.get("cells", {})
        return scoring_engine.score_cells(cells, category_id, budget_tier, weight_overrides, top_n)


scoring_agent = ScoringAgent()
