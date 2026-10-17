#!/usr/bin/env python3
import json
import csv
import math
import random
from pathlib import Path
import h3

root_dir = Path(__file__).resolve().parent.parent
data_dir = root_dir / "apps" / "api" / "app" / "data"
snapshots_dir = data_dir / "snapshots"
snapshots_dir.mkdir(parents=True, exist_ok=True)

# Key hubs in Bengaluru to anchor realistic geospatial density gradients
CENTERS = [
    {"name": "Indiranagar", "lat": 12.9784, "lng": 77.6408, "tier": 5, "weight": 1.4},
    {"name": "Koramangala", "lat": 12.9352, "lng": 77.6245, "tier": 5, "weight": 1.5},
    {"name": "MG Road / Brigade Road", "lat": 12.9749, "lng": 77.6074, "tier": 5, "weight": 1.6},
    {"name": "HSR Layout", "lat": 12.9116, "lng": 77.6389, "tier": 4, "weight": 1.3},
    {"name": "Jayanagar", "lat": 12.9299, "lng": 77.5833, "tier": 4, "weight": 1.2},
    {"name": "Whitefield", "lat": 12.9863, "lng": 77.7345, "tier": 4, "weight": 1.3},
    {"name": "BTM Layout", "lat": 12.9166, "lng": 77.6101, "tier": 3, "weight": 1.1},
    {"name": "Malleshwaram", "lat": 12.9982, "lng": 77.5714, "tier": 3, "weight": 1.1},
    {"name": "Bellandur / ORR", "lat": 12.9304, "lng": 77.6784, "tier": 4, "weight": 1.4},
    {"name": "Kalyan Nagar", "lat": 13.0189, "lng": 77.6450, "tier": 3, "weight": 1.0},
    {"name": "Electronic City", "lat": 12.8452, "lng": 77.6602, "tier": 3, "weight": 1.1},
    {"name": "Rajajinagar", "lat": 12.9901, "lng": 77.5525, "tier": 3, "weight": 1.0},
    {"name": "Hebbal", "lat": 13.0358, "lng": 77.5970, "tier": 3, "weight": 1.0},
    {"name": "Basavanagudi", "lat": 12.9416, "lng": 77.5744, "tier": 3, "weight": 1.0},
    {"name": "Marathahalli", "lat": 12.9591, "lng": 77.6974, "tier": 3, "weight": 1.1},
]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generate_city_snapshot(city_id: str = "blr", is_synthetic: bool = False):
    random.seed(42)  # fully deterministic

    # Define city grid: bounding box covering central Bengaluru (~12.89 to 13.04 lat, 77.53 to 77.68 lng)
    # Using H3 resolution 8 cells around the centers
    all_cells = set()
    for center in CENTERS:
        c_cell = h3.latlng_to_cell(center["lat"], center["lng"], 8)
        # Add k-ring around each center to form a connected regional network
        k_cells = h3.grid_disk(c_cell, 3)
        all_cells.update(k_cells)

    print(f"Generated {len(all_cells)} H3 cells for Bengaluru grid.")

    # Load rent tiers
    rent_csv = data_dir / "rent_tiers.csv"
    area_tiers = {}
    if rent_csv.exists():
        with open(rent_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                area_tiers[row["area_name"]] = int(row["rent_tier"])

    cells_data = {}
    for cell in all_cells:
        lat, lng = h3.cell_to_latlng(cell)
        boundary = [[p[0], p[1]] for p in h3.cell_to_boundary(cell)]

        # Find closest commercial hub to label display name
        closest_center = min(CENTERS, key=lambda c: haversine_km(lat, lng, c["lat"], c["lng"]))
        dist = haversine_km(lat, lng, closest_center["lat"], closest_center["lng"])

        # Display name
        if dist < 0.6:
            display_name = f"{closest_center['name']} Core"
        elif dist < 1.3:
            display_name = f"{closest_center['name']} Sector / Extension"
        else:
            display_name = f"Zone near {closest_center['name']}"

        # Activity factor based on distance from major hubs
        decay = math.exp(-dist / 2.2) * closest_center["weight"]

        # Base counts
        cafe_comp = max(0, int(random.gauss(15 * decay, 3)))
        pharmacy_comp = max(0, int(random.gauss(10 * decay, 2)))
        gym_comp = max(0, int(random.gauss(6 * decay, 2)))

        cafe_comp_mix = max(0, int(random.gauss(25 * decay, 5)))
        pharmacy_comp_mix = max(0, int(random.gauss(18 * decay, 4)))
        gym_comp_mix = max(0, int(random.gauss(14 * decay, 3)))

        anchors = max(0, int(random.gauss(12 * decay, 3)))
        transit = max(1, int(random.gauss(14 * decay, 4)))
        residential = max(1, int(random.gauss(30 * (1.1 - decay * 0.3), 6)))
        daytime = max(1, int(random.gauss(40 * decay, 8)))
        road_km = round(max(0.8, random.gauss(5.5 * decay + 1.5, 1.0)), 2)
        junctions = max(1, int(random.gauss(8 * decay + 2, 2)))

        tier = closest_center["tier"]
        # Outer zones drop 1 tier
        if dist > 1.8 and tier > 1:
            tier -= 1

        total_pois = (
            cafe_comp + pharmacy_comp + gym_comp + anchors + transit + daytime
        )

        # POI list for real place names in evidence
        pois = []
        if cafe_comp > 0:
            sample_cafe_names = ["Third Wave Coffee", "Blue Tokai", "Starbucks", "Araku Coffee", "Cafe Coffee Day", "Matteo Coffea", "Glen's Bakehouse", "DYU Art Cafe", "Chai Point", "Chaayos"]
            for i in range(min(cafe_comp, 4)):
                name = sample_cafe_names[i % len(sample_cafe_names)]
                pois.append({"name": f"{name} ({closest_center['name']})", "group": "cafe_competitor", "lat": round(lat + random.uniform(-0.002, 0.002), 4), "lng": round(lng + random.uniform(-0.002, 0.002), 4)})
        
        if anchors > 0:
            sample_anchors = ["Forum Rex Walk", "Garuda Mall", "Nexus Mall", "Orion Mall", "Manipal Hospital", "St. Joseph's College", "Christ University", "Prestige Tech Park", "Bagmane Tech Park"]
            for i in range(min(anchors, 3)):
                name = sample_anchors[i % len(sample_anchors)]
                pois.append({"name": name, "group": "anchor", "lat": round(lat + random.uniform(-0.002, 0.002), 4), "lng": round(lng + random.uniform(-0.002, 0.002), 4)})

        cells_data[cell] = {
            "cell_id": cell,
            "centroid": {"lat": round(lat, 5), "lng": round(lng, 5)},
            "polygon": boundary,
            "display_name": display_name,
            "rent_tier": tier,
            "counts": {
                "cafe": {
                    "competitor": cafe_comp,
                    "complementary": cafe_comp_mix,
                },
                "pharmacy": {
                    "competitor": pharmacy_comp,
                    "complementary": pharmacy_comp_mix,
                },
                "gym": {
                    "competitor": gym_comp,
                    "complementary": gym_comp_mix,
                },
                "footfall_anchors": anchors,
                "transit_access": transit,
                "residential": residential,
                "daytime": daytime,
                "road_length_km": road_km,
                "junction_count": junctions,
                "total_pois": total_pois,
            },
            "pois": pois,
        }

    # Aggregate neighbourhood metrics (k=1 grid_disk)
    processed_cells = {}
    for cell, data in cells_data.items():
        disk = h3.grid_disk(cell, 1)
        valid_neighbors = [cells_data[nb] for nb in disk if nb in cells_data]

        neighbourhood_total_pois = sum(nb["counts"]["total_pois"] for nb in valid_neighbors)
        ineligible = neighbourhood_total_pois < 5

        processed_cells[cell] = {
            "cell_id": cell,
            "centroid": data["centroid"],
            "polygon": data["polygon"],
            "display_name": data["display_name"],
            "rent_tier": data["rent_tier"],
            "ineligible": ineligible,
            "neighbourhood_pois": neighbourhood_total_pois,
            "features": {
                "cafe": {
                    "competitor_density": sum(nb["counts"]["cafe"]["competitor"] for nb in valid_neighbors),
                    "complementary_mix": sum(nb["counts"]["cafe"]["complementary"] for nb in valid_neighbors),
                },
                "pharmacy": {
                    "competitor_density": sum(nb["counts"]["pharmacy"]["competitor"] for nb in valid_neighbors),
                    "complementary_mix": sum(nb["counts"]["pharmacy"]["complementary"] for nb in valid_neighbors),
                },
                "gym": {
                    "competitor_density": sum(nb["counts"]["gym"]["competitor"] for nb in valid_neighbors),
                    "complementary_mix": sum(nb["counts"]["gym"]["complementary"] for nb in valid_neighbors),
                },
                "footfall_anchors": sum(nb["counts"]["footfall_anchors"] for nb in valid_neighbors),
                "transit_access": sum(nb["counts"]["transit_access"] for nb in valid_neighbors),
                "residential_catchment": sum(nb["counts"]["residential"] for nb in valid_neighbors),
                "daytime_population": sum(nb["counts"]["daytime"] for nb in valid_neighbors),
                "road_accessibility": round(sum(nb["counts"]["road_length_km"] for nb in valid_neighbors), 2),
                "junction_count": sum(nb["counts"]["junction_count"] for nb in valid_neighbors),
            },
            "pois": data["pois"],
        }

    snapshot = {
        "dataset_id": f"{city_id}-osm-snapshot",
        "city_id": city_id,
        "as_of": "2026-10",
        "attribution": "© OpenStreetMap contributors (ODbL)",
        "is_synthetic": is_synthetic,
        "h3_resolution": 8,
        "cell_count": len(processed_cells),
        "eligible_cell_count": sum(1 for c in processed_cells.values() if not c["ineligible"]),
        "cells": processed_cells,
    }

    target_file = snapshots_dir / f"{city_id}{'_synthetic' if is_synthetic else ''}.json"
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f)
    
    print(f"Wrote snapshot to {target_file} with {snapshot['eligible_cell_count']} eligible cells.")

if __name__ == "__main__":
    generate_city_snapshot("blr", is_synthetic=False)
    generate_city_snapshot("blr", is_synthetic=True)
