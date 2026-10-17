import yaml
from pathlib import Path
from fastapi import APIRouter
from ..config import settings
from ..schemas import (
    MetaResponse,
    CityMeta,
    CategoryMeta,
    BudgetTierMeta,
    SignalMeta,
    DatasetMeta,
    Centroid,
    ProvenanceClass,
)

router = APIRouter(prefix="/api/v1", tags=["Metadata"])

CONFIG_DIR = Path(__file__).resolve().parent.parent / "scoring" / "configs"


def load_yaml(filename: str) -> dict:
    with open(CONFIG_DIR / filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@router.get("/meta", response_model=MetaResponse)
async def get_meta():
    weights_data = load_yaml("weights.yaml")
    budget_data = load_yaml("budget_tiers.yaml")
    
    cities = [
        CityMeta(
            city_id="blr",
            name="Bengaluru",
            country="India",
            center=Centroid(lat=12.9716, lng=77.5946),
            h3_resolution=8
        )
    ]

    categories = [
        CategoryMeta(category_id="cafe", name="Café / Specialty Coffee"),
        CategoryMeta(category_id="pharmacy", name="Pharmacy / Retail Chemist"),
        CategoryMeta(category_id="gym", name="Fitness Centre / Gym"),
    ]

    budget_tiers = [
        BudgetTierMeta(
            tier_id=k,
            name=v["name"],
            max_acceptable_tier=v["max_acceptable_tier"],
            description=v["description"]
        )
        for k, v in budget_data.get("budget_tiers", {}).items()
    ]

    signals = [
        SignalMeta(
            signal_id="competition_density",
            name="Competition Density",
            better_when="lower",
            provenance=ProvenanceClass.MEASURED,
            description="Density of same-category commercial competitors in immediate neighbourhood."
        ),
        SignalMeta(
            signal_id="gap_opportunity",
            name="Gap Opportunity",
            better_when="higher",
            provenance=ProvenanceClass.ESTIMATED,
            description="Ratio of footfall and residential proxies to existing direct competitors."
        ),
        SignalMeta(
            signal_id="footfall_anchors",
            name="Footfall Anchors",
            better_when="higher",
            provenance=ProvenanceClass.ESTIMATED,
            description="Proximity to major foot traffic generators (malls, colleges, markets, hospitals)."
        ),
        SignalMeta(
            signal_id="transit_access",
            name="Transit Access",
            better_when="higher",
            provenance=ProvenanceClass.MEASURED,
            description="Bus stop, metro, and rail accessibility score."
        ),
        SignalMeta(
            signal_id="complementary_mix",
            name="Complementary Commercial Mix",
            better_when="higher",
            provenance=ProvenanceClass.MEASURED,
            description="Presence of synergetic businesses driving shared footfall."
        ),
        SignalMeta(
            signal_id="residential_catchment",
            name="Residential Catchment",
            better_when="higher",
            provenance=ProvenanceClass.ESTIMATED,
            description="Local household and apartment building density."
        ),
        SignalMeta(
            signal_id="daytime_population",
            name="Daytime Population",
            better_when="higher",
            provenance=ProvenanceClass.ESTIMATED,
            description="Commercial, office, and educational daytime activity proxies."
        ),
        SignalMeta(
            signal_id="road_accessibility",
            name="Road Accessibility",
            better_when="higher",
            provenance=ProvenanceClass.MEASURED,
            description="Arterial road connectivity, street grid density, and junction count."
        ),
        SignalMeta(
            signal_id="rent_efficiency",
            name="Rent Efficiency",
            better_when="higher",
            provenance=ProvenanceClass.HEURISTIC,
            description="Affordability alignment between area heuristic rent tier and selected budget."
        ),
    ]

    default_weights = weights_data.get("categories", {})

    dataset = DatasetMeta(
        id="blr-osm-snapshot",
        mode=settings.DATA_MODE,
        as_of="2026-10",
        attribution="© OpenStreetMap contributors (ODbL)",
        contains_simulated=(settings.DATA_MODE == "synthetic")
    )

    return MetaResponse(
        cities=cities,
        categories=categories,
        budget_tiers=budget_tiers,
        signals=signals,
        default_weights=default_weights,
        dataset=dataset
    )
