from typing import List, Dict
from pydantic import Field
from .common import BaseSchema, Centroid
from .enums import ProvenanceClass


class CityMeta(BaseSchema):
    city_id: str
    name: str
    country: str
    center: Centroid
    h3_resolution: int


class CategoryMeta(BaseSchema):
    category_id: str
    name: str


class BudgetTierMeta(BaseSchema):
    tier_id: str
    name: str
    max_acceptable_tier: int
    description: str


class SignalMeta(BaseSchema):
    signal_id: str
    name: str
    better_when: str  # "higher" or "lower"
    provenance: ProvenanceClass
    description: str


class DatasetMeta(BaseSchema):
    id: str
    mode: str
    as_of: str
    attribution: str
    contains_simulated: bool


class MetaResponse(BaseSchema):
    cities: List[CityMeta]
    categories: List[CategoryMeta]
    budget_tiers: List[BudgetTierMeta]
    signals: List[SignalMeta]
    default_weights: Dict[str, Dict[str, float]]
    dataset: DatasetMeta
