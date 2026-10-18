#!/usr/bin/env python3
"""Ingest the real OSM dataset (D:\\Projects\\Nasiko_Buildathon) into Postgres.

Phase D (plan.md). Reads raw OSM elements for Bengaluru from the
SiteScout project's fetched dataset, assigns each element to an H3
res-8 cell, aggregates per-cell signal counts using Disha AI's own
category_taxonomy.yaml (not SiteScout's config - see plan.md D-notes),
and upserts cities / h3_cells / pois into Postgres.

Idempotent: re-running this script for the same city upserts on
natural keys (h3_index; (osm_type, osm_id) for pois) rather than
duplicating rows.

Known simplifications (logged in progress.md, not silently assumed):
- "Neighbourhood" signals are the exact cell plus its 1-ring of H3
  neighbours (h3.grid_disk(cell, 1)), not a precise radius/decay
  model.
- road_accessibility / junction_count are approximated from counts of
  trunk/primary/secondary road ways near a cell, not true line-length
  or intersection geometry (see _ROAD_WEIGHTS below).
- A cell's locality/rent_tier comes from the nearest named OSM place
  (amenity=place_of_worship-style place nodes), matched against
  apps/api/app/data/rent_tiers.csv by substring; cells with no
  reasonably close named place default to the DEFAULT_UNASSIGNED tier.
- Landuse/building "area" elements are represented by their OSM
  "center"/"bounds" centroid, not full polygon coverage.
"""

import argparse
import asyncio
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import h3
import yaml

API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from app.db.base import engine
from app.db.models import POI, City, H3Cell
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

OSM_DIR = Path(r"D:\Projects\Nasiko_Buildathon\data\raw\osm\bengaluru\latest")
CONFIG_DIR = API_DIR / "app" / "scoring" / "configs"
RENT_CSV = API_DIR / "app" / "data" / "rent_tiers.csv"

CITY_SLUG = "blr"
H3_RES = 8
CATEGORIES = ["cafe", "pharmacy", "gym"]

# Road class -> weight for the road_accessibility proxy (see module docstring).
_ROAD_WEIGHTS = {"trunk": 3.0, "primary": 2.0, "secondary": 1.0}

# Files that feed POI/signal aggregation. landuse/places are handled with
# lighter touch (landuse only for residential signal, places only for
# locality assignment) - see main().
_POI_FILES = ["buildings", "education", "finance", "food", "health", "leisure", "retail", "work"]


def load_category_taxonomy() -> dict:
    with open(CONFIG_DIR / "category_taxonomy.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)["categories"]


def load_rent_tiers() -> list[tuple[str, int]]:
    rows = []
    with open(RENT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["area_name"] == "DEFAULT_UNASSIGNED":
                continue
            rows.append((row["area_name"], int(row["rent_tier"])))
    return rows


def default_rent_tier() -> int:
    with open(RENT_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["area_name"] == "DEFAULT_UNASSIGNED":
                return int(row["rent_tier"])
    return 3


def get_point(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    if "center" in element:
        return element["center"]["lat"], element["center"]["lon"]
    if "bounds" in element:
        b = element["bounds"]
        return (b["minlat"] + b["maxlat"]) / 2.0, (b["minlon"] + b["maxlon"]) / 2.0
    return None


def tags_match(tags: dict, selectors: dict[str, list[str]]) -> bool:
    for key, allowed in selectors.items():
        if tags.get(key) in allowed:
            return True
    return False


def haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def load_osm_file(group: str) -> list[dict]:
    path = OSM_DIR / f"{group}.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)["elements"]


def main(top_n_eligible_check: int = 10) -> None:
    taxonomy = load_category_taxonomy()
    rent_tiers = load_rent_tiers()
    default_tier = default_rent_tier()

    union_anchors: dict[str, list[str]] = {}
    union_daytime: dict[str, list[str]] = {}
    union_transit: dict[str, list[str]] = {}
    union_residential: dict[str, list[str]] = {}
    for cat_cfg in taxonomy.values():
        for role_dict, union_dict in (
            (cat_cfg.get("anchors", {}), union_anchors),
            (cat_cfg.get("daytime", {}), union_daytime),
            (cat_cfg.get("transit", {}), union_transit),
            (cat_cfg.get("residential", {}), union_residential),
        ):
            for k, vals in role_dict.items():
                union_dict.setdefault(k, [])
                for v in vals:
                    if v not in union_dict[k]:
                        union_dict[k].append(v)

    competitor_counts: dict[str, dict[str, int]] = {}
    complement_counts: dict[str, dict[str, int]] = {}
    anchor_counts: dict[str, int] = {}
    daytime_counts: dict[str, int] = {}
    transit_counts: dict[str, int] = {}
    residential_counts: dict[str, int] = {}
    road_weighted: dict[str, float] = {}
    road_way_count: dict[str, int] = {}
    poi_rows: list[dict] = []

    def bump(d: dict, key: str, amount: int = 1) -> None:
        d[key] = d.get(key, 0) + amount

    print("Loading POI-bearing OSM files...")
    for group in _POI_FILES:
        elements = load_osm_file(group)
        print(f"  {group}: {len(elements)} elements")
        for el in elements:
            point = get_point(el)
            if point is None:
                continue
            tags = el.get("tags", {})
            cell = h3.latlng_to_cell(point[0], point[1], H3_RES)

            for cat in CATEGORIES:
                cat_cfg = taxonomy[cat]
                if tags_match(tags, cat_cfg.get("competitors", {})):
                    competitor_counts.setdefault(cell, {}).setdefault(cat, 0)
                    bump(competitor_counts[cell], cat)
                if tags_match(tags, cat_cfg.get("complements", {})):
                    complement_counts.setdefault(cell, {}).setdefault(cat, 0)
                    bump(complement_counts[cell], cat)

            if tags_match(tags, union_anchors):
                bump(anchor_counts, cell)
            if tags_match(tags, union_daytime):
                bump(daytime_counts, cell)
            if tags_match(tags, union_transit):
                bump(transit_counts, cell)
            if tags_match(tags, union_residential):
                bump(residential_counts, cell)

            name = tags.get("name")
            label = tags.get("amenity") or tags.get("shop") or tags.get("leisure") or tags.get("office") or tags.get("building")
            if name or label:
                poi_rows.append({
                    "osm_type": el["type"],
                    "osm_id": el["id"],
                    "h3_index": cell,
                    "category": group,
                    "group_tag": label,
                    "name": name,
                    "tags": tags,
                    "lat": point[0],
                    "lng": point[1],
                })

    print("Loading landuse.json (residential signal only)...")
    for el in load_osm_file("landuse"):
        point = get_point(el)
        if point is None:
            continue
        tags = el.get("tags", {})
        if tags_match(tags, union_residential):
            cell = h3.latlng_to_cell(point[0], point[1], H3_RES)
            bump(residential_counts, cell)

    print("Loading roads.json (road_accessibility proxy)...")
    for el in load_osm_file("roads"):
        point = get_point(el)
        if point is None:
            continue
        highway = el.get("tags", {}).get("highway")
        weight = _ROAD_WEIGHTS.get(highway)
        if weight is None:
            continue
        cell = h3.latlng_to_cell(point[0], point[1], H3_RES)
        road_weighted[cell] = road_weighted.get(cell, 0.0) + weight
        bump(road_way_count, cell)

    print("Loading places.json (locality assignment)...")
    named_places: list[tuple[str, float, float]] = []
    for el in load_osm_file("places"):
        point = get_point(el)
        name = el.get("tags", {}).get("name")
        if point and name:
            named_places.append((name, point[0], point[1]))
    print(f"  {len(named_places)} named places")

    all_cells = set(competitor_counts) | set(complement_counts) | set(anchor_counts) | \
        set(daytime_counts) | set(transit_counts) | set(residential_counts) | \
        set(road_weighted) | {p["h3_index"] for p in poi_rows}
    print(f"Total populated cells (pre-neighbourhood aggregation): {len(all_cells)}")

    poi_cell_counts: dict[str, int] = {}
    for p in poi_rows:
        bump(poi_cell_counts, p["h3_index"])

    def nearest_place(lat: float, lng: float) -> str | None:
        best, best_d = None, float("inf")
        for name, plat, plng in named_places:
            d = haversine_km((lat, lng), (plat, plng))
            if d < best_d:
                best, best_d = name, d
        return best if best_d <= 5.0 else None

    def rent_tier_for(locality: str | None) -> int:
        if not locality:
            return default_tier
        locality_lower = locality.lower()
        for area_name, tier in rent_tiers:
            area_lower = area_name.lower()
            if locality_lower in area_lower or area_lower in locality_lower:
                return tier
        return default_tier

    def nsum(counts: dict[str, int], ring: list[str]) -> int:
        return sum(counts.get(c, 0) for c in ring)

    def ncat(counts: dict[str, dict[str, int]], cat: str, ring: list[str]) -> int:
        return sum(counts.get(c, {}).get(cat, 0) for c in ring)

    cells_payload = []
    for cell in all_cells:
        ring = h3.grid_disk(cell, 1)

        features: dict[str, Any] = {
            cat: {
                "competitor_density": ncat(competitor_counts, cat, ring),
                "complementary_mix": ncat(complement_counts, cat, ring),
            }
            for cat in CATEGORIES
        }
        features["footfall_anchors"] = nsum(anchor_counts, ring)
        features["transit_access"] = nsum(transit_counts, ring)
        features["residential_catchment"] = nsum(residential_counts, ring)
        features["daytime_population"] = nsum(daytime_counts, ring)
        features["road_accessibility"] = round(sum(road_weighted.get(c, 0.0) for c in ring), 2)
        features["junction_count"] = sum(road_way_count.get(c, 0) for c in ring)

        neighbourhood_pois = sum(poi_cell_counts.get(c, 0) for c in ring)

        lat, lng = h3.cell_to_latlng(cell)
        boundary = [[v[0], v[1]] for v in h3.cell_to_boundary(cell)]
        locality = nearest_place(lat, lng)
        rent_tier = rent_tier_for(locality)
        display_name = f"Zone near {locality}" if locality else f"Zone {cell[-6:]}"

        cells_payload.append({
            "h3_index": cell,
            "centroid": (lat, lng),
            "boundary": boundary,
            "display_name": display_name,
            "locality_name": locality,
            "rent_tier": rent_tier,
            "ineligible": neighbourhood_pois < 5,
            "neighbourhood_pois": neighbourhood_pois,
            "features": features,
        })

    eligible = [c for c in cells_payload if not c["ineligible"]]
    print(f"Eligible cells: {len(eligible)} / {len(cells_payload)} total")
    if len(eligible) < top_n_eligible_check:
        print(
            f"WARNING: only {len(eligible)} eligible cells, fewer than the "
            f"{top_n_eligible_check} the API/tests request as top_n. "
            "Scoring will still work but will return fewer than top_n results."
        )

    asyncio.run(_write_to_db(cells_payload, poi_rows))


async def _write_to_db(cells_payload: list[dict], poi_rows: list[dict]) -> None:
    if engine is None:
        raise RuntimeError("DATABASE_URL is not configured")

    bbox = {
        "min_lat": min(c["centroid"][0] for c in cells_payload),
        "max_lat": max(c["centroid"][0] for c in cells_payload),
        "min_lng": min(c["centroid"][1] for c in cells_payload),
        "max_lng": max(c["centroid"][1] for c in cells_payload),
    }

    async with AsyncSession(engine) as session:
        existing = await session.execute(select(City).where(City.slug == CITY_SLUG))
        city = existing.scalar_one_or_none()
        if city is None:
            city = City(slug=CITY_SLUG, name="Bengaluru", country="India", bbox=bbox, h3_resolution=H3_RES)
            session.add(city)
            await session.flush()
        else:
            city.bbox = bbox
        city_id = city.id
        await session.commit()

        print(f"Upserting {len(cells_payload)} H3 cells...")
        for i in range(0, len(cells_payload), 500):
            batch = cells_payload[i:i + 500]
            stmt = pg_insert(H3Cell).values([
                {
                    "h3_index": c["h3_index"],
                    "city_id": city_id,
                    "centroid": f"SRID=4326;POINT({c['centroid'][1]} {c['centroid'][0]})",
                    "boundary": c["boundary"],
                    "display_name": c["display_name"],
                    "locality_name": c["locality_name"],
                    "rent_tier": c["rent_tier"],
                    "ineligible": c["ineligible"],
                    "neighbourhood_pois": c["neighbourhood_pois"],
                    "features": c["features"],
                }
                for c in batch
            ])
            stmt = stmt.on_conflict_do_update(
                index_elements=["h3_index"],
                set_={
                    "display_name": stmt.excluded.display_name,
                    "locality_name": stmt.excluded.locality_name,
                    "rent_tier": stmt.excluded.rent_tier,
                    "ineligible": stmt.excluded.ineligible,
                    "neighbourhood_pois": stmt.excluded.neighbourhood_pois,
                    "features": stmt.excluded.features,
                    "boundary": stmt.excluded.boundary,
                },
            )
            await session.execute(stmt)
        await session.commit()

        print(f"Upserting {len(poi_rows)} POIs...")
        for i in range(0, len(poi_rows), 1000):
            batch = poi_rows[i:i + 1000]
            stmt = pg_insert(POI).values([
                {
                    "osm_type": p["osm_type"],
                    "osm_id": p["osm_id"],
                    "h3_index": p["h3_index"],
                    "category": p["category"],
                    "group_tag": p["group_tag"],
                    "name": p["name"],
                    "tags": p["tags"],
                    "geom": f"SRID=4326;POINT({p['lng']} {p['lat']})",
                }
                for p in batch
            ])
            stmt = stmt.on_conflict_do_update(
                index_elements=["osm_type", "osm_id"],
                set_={
                    "h3_index": stmt.excluded.h3_index,
                    "category": stmt.excluded.category,
                    "group_tag": stmt.excluded.group_tag,
                    "name": stmt.excluded.name,
                    "tags": stmt.excluded.tags,
                    "geom": stmt.excluded.geom,
                },
            )
            await session.execute(stmt)
        await session.commit()

    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-n-check", type=int, default=10)
    args = parser.parse_args()
    main(top_n_eligible_check=args.top_n_check)
