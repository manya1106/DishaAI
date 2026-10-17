from app.schemas.enums import SignalStatus
from app.scoring.engine import scoring_engine


def test_missing_data_renormalisation():
    cells = {
        "c1": {
            "cell_id": "c1",
            "display_name": "Test Zone",
            "centroid": {"lat": 12.97, "lng": 77.59},
            "polygon": [[12.97, 77.59]],
            "rent_tier": None,  # rent is unavailable
            "ineligible": False,
            "features": {
                "cafe": {"competitor_density": 5, "complementary_mix": 10},
                "footfall_anchors": 8,
                "transit_access": 6,
                "residential_catchment": 15,
                "daytime_population": 20,
                "road_accessibility": 3.0,
                "junction_count": 4,
            }
        }
    }

    locations, _weights = scoring_engine.score_cells(
        cells=cells,
        category_id="cafe",
        budget_tier="medium",
        top_n=1
    )

    assert len(locations) == 1
    loc = locations[0]
    
    # Rent efficiency should be unavailable
    rent_sig = next(s for s in loc.signals if s.signal_id == "rent_efficiency")
    assert rent_sig.status == SignalStatus.UNAVAILABLE
    assert rent_sig.score is None
    assert rent_sig.effective_weight == 0.0

    # Effective weights of available signals must sum to 1.0
    active_effective_weights = sum(s.effective_weight for s in loc.signals if s.score is not None)
    assert round(active_effective_weights, 2) == 1.0

    # Total contribution must equal overall_score
    total_contrib = sum(s.contribution for s in loc.signals)
    assert round(total_contrib, 1) == loc.overall_score
