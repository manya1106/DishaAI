"use client";

import React, { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import { LocationResult, GeoJSONFeatureCollection } from "../lib/types";

// Explicit worker URL configuration for bundlers / Turbopack
if (typeof window !== "undefined") {
  maplibregl.config.WORKER_URL = "/maplibre-gl-worker.mjs";
}

type Map = maplibregl.Map;
type Marker = maplibregl.Marker;

interface Props {
  locations: LocationResult[];
  heatmap?: GeoJSONFeatureCollection;
  selectedLocationId: string | null;
  onSelectLocation: (locationId: string) => void;
}

const DEFAULT_STYLE =
  process.env.NEXT_PUBLIC_MAP_STYLE_URL ||
  "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

export default function MapComponent({
  locations,
  heatmap,
  selectedLocationId,
  onSelectLocation,
}: Props) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);
  const markersRef = useRef<Marker[]>([]);
  const [isMapLoaded, setIsMapLoaded] = useState(false);

  // Initialize Map
  useEffect(() => {
    if (!mapContainer.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: mapContainer.current,
      style: DEFAULT_STYLE,
      center: [77.62, 12.96], // Central Bengaluru
      zoom: 11.5,
      pitch: 30,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

    map.on("load", () => {
      mapRef.current = map;
      setIsMapLoaded(true);
    });

    map.on("error", (e) => {
      console.warn("MapLibre event:", e.error?.message || e);
    });

    return () => {
      map.remove();
      mapRef.current = null;
      setIsMapLoaded(false);
    };
  }, []);

  // Update Heatmap Layer when data changes or map finishes loading
  useEffect(() => {
    if (!mapRef.current || !isMapLoaded) return;
    renderHeatmapLayer(mapRef.current, heatmap);
  }, [heatmap, isMapLoaded]);

  function renderHeatmapLayer(map: Map, geojson?: GeoJSONFeatureCollection) {
    if (!geojson) return;

    // Check if source exists, update or add
    const source = map.getSource("h3-hex-source") as maplibregl.GeoJSONSource | undefined;
    if (source) {
      source.setData(geojson as any);
    } else {
      map.addSource("h3-hex-source", {
        type: "geojson",
        data: geojson as any,
      });

      map.addLayer({
        id: "h3-hex-fill",
        type: "fill",
        source: "h3-hex-source",
        paint: {
          "fill-color": [
            "interpolate",
            ["linear"],
            ["get", "overall_score"],
            40,
            "#3b82f6", // blue
            60,
            "#06b6d4", // cyan
            70,
            "#10b981", // emerald
            85,
            "#f59e0b", // amber gold
          ],
          "fill-opacity": 0.45,
        },
      });

      map.addLayer({
        id: "h3-hex-borders",
        type: "line",
        source: "h3-hex-source",
        paint: {
          "line-color": "#ffffff",
          "line-width": 1,
          "line-opacity": 0.35,
        },
      });

      // Click on polygon to select
      map.on("click", "h3-hex-fill", (e) => {
        if (e.features && e.features[0]?.properties?.location_id) {
          onSelectLocation(e.features[0].properties.location_id);
        }
      });
    }
  }

  // Update Numbered Location Markers
  useEffect(() => {
    if (!mapRef.current || !isMapLoaded) return;

    // Clear previous markers
    markersRef.current.forEach((m) => m.remove());
    markersRef.current = [];

    locations.forEach((loc) => {
      const el = document.createElement("div");
      const isSelected = loc.location_id === selectedLocationId;

      el.className = `disha-map-marker ${
        isSelected ? "disha-marker-active" : ""
      } ${
        loc.rank === 1
          ? "w-9 h-9 text-sm bg-gradient-to-tr from-amber-500 to-yellow-300 text-slate-950 font-black border-2 border-amber-200"
          : loc.rank <= 3
          ? "w-8 h-8 text-xs bg-gradient-to-tr from-emerald-500 to-cyan-400 text-slate-950 font-extrabold border border-emerald-200"
          : "w-7 h-7 text-xs bg-slate-900 text-emerald-400 border border-slate-700 font-bold"
      }`;

      el.innerHTML = `<span>${loc.rank}</span>`;
      el.addEventListener("click", () => {
        onSelectLocation(loc.location_id);
      });

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([loc.centroid.lng, loc.centroid.lat])
        .addTo(mapRef.current!);

      markersRef.current.push(marker);
    });
  }, [locations, selectedLocationId, isMapLoaded]);

  // Fly to selected location
  useEffect(() => {
    if (!mapRef.current || !selectedLocationId) return;
    const selected = locations.find((l) => l.location_id === selectedLocationId);
    if (selected) {
      mapRef.current.flyTo({
        center: [selected.centroid.lng, selected.centroid.lat],
        zoom: 13,
        essential: true,
        duration: 1000,
      });
    }
  }, [selectedLocationId]);

  return (
    <div className="relative w-full h-full min-h-[450px] rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-10 glass-panel px-3.5 py-2.5 rounded-xl text-xs space-y-1.5 shadow-xl pointer-events-none">
        <div className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider">
          Location Score Heatmap
        </div>
        <div className="flex items-center gap-2">
          <div className="h-2 w-32 rounded bg-gradient-to-r from-blue-500 via-cyan-400 via-emerald-400 to-amber-400" />
          <span className="text-[10px] text-slate-400">40 → 90+</span>
        </div>
        <div className="text-[10px] text-slate-500">
          Showing H3 Hexagons (Res 8) & Top 10 Zones
        </div>
      </div>
    </div>
  );
}
