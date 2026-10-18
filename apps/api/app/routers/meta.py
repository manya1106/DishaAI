from pathlib import Path

import yaml
from fastapi import APIRouter

from ..config import settings
from ..schemas import (
    BudgetTierMeta,
    CategoryMeta,
    CategoryQuestion,
    Centroid,
    CityMeta,
    DatasetMeta,
    MetaResponse,
    ProvenanceClass,
    SelectOption,
    SignalMeta,
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

    # Short, category-specific tier descriptions for the wizard's tier step
    # (plan.md / the SiteScout architecture doc §7.1, adapted to cafe/pharmacy/gym).
    category_tier_descriptions = {
        "cafe": {
            "low": "Chai-and-snacks or regular coffee counter, low ticket size.",
            "medium": "Branded-style cafe with seating and a broader menu.",
            "high": "Specialty coffee, designer interiors, higher average ticket.",
        },
        "pharmacy": {
            "low": "Neighbourhood standard pharmacy, OTC-led.",
            "medium": "Pharmacy plus OTC and personal care range.",
            "high": "Wellness/health-store style with delivery and chronic-care focus.",
        },
        "gym": {
            "low": "Basic neighbourhood gym, equipment-first.",
            "medium": "Mid-range fitness centre with classes and trainers.",
            "high": "Boutique studio or full-service club, premium interiors.",
        },
    }

    target_customer_options = [
        SelectOption(value="students", label="Students"),
        SelectOption(value="young_professionals", label="Young professionals"),
        SelectOption(value="families", label="Families"),
        SelectOption(value="seniors", label="Seniors"),
        SelectOption(value="tourists", label="Tourists / visitors"),
    ]

    category_questions = {
        "cafe": [
            CategoryQuestion(
                question_id="format",
                label="Format",
                type="single_select",
                options=[
                    SelectOption(value="takeaway_kiosk", label="Takeaway kiosk"),
                    SelectOption(value="sit_down", label="Sit-down cafe"),
                    SelectOption(value="coworking", label="Co-working style"),
                ],
            ),
        ],
        "pharmacy": [
            CategoryQuestion(
                question_id="is_24x7",
                label="Planning to run 24x7?",
                type="boolean",
                options=[SelectOption(value="true", label="Yes"), SelectOption(value="false", label="No")],
            ),
            CategoryQuestion(
                question_id="nearby_clinics_ok",
                label="Comfortable being next to clinics/diagnostic labs?",
                type="boolean",
                options=[SelectOption(value="true", label="Yes"), SelectOption(value="false", label="No")],
            ),
        ],
        "gym": [
            CategoryQuestion(
                question_id="format",
                label="Format",
                type="single_select",
                options=[
                    SelectOption(value="boutique_studio", label="Boutique studio"),
                    SelectOption(value="full_service", label="Full-service gym"),
                ],
            ),
            CategoryQuestion(
                question_id="parking_needed",
                label="Do members need dedicated parking?",
                type="boolean",
                options=[SelectOption(value="true", label="Yes"), SelectOption(value="false", label="No")],
            ),
        ],
    }

    return MetaResponse(
        cities=cities,
        categories=categories,
        budget_tiers=budget_tiers,
        signals=signals,
        default_weights=default_weights,
        dataset=dataset,
        category_tier_descriptions=category_tier_descriptions,
        target_customer_options=target_customer_options,
        category_questions=category_questions,
    )
