"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
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
  "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

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

  const renderHeatmapLayer = useCallback(
    (map: Map, geojson?: GeoJSONFeatureCollection) => {
      if (!geojson) return;

      const geojsonData = geojson as unknown as Parameters<maplibregl.GeoJSONSource["setData"]>[0];

      // Check if source exists, update or add
      const source = map.getSource("h3-hex-source") as maplibregl.GeoJSONSource | undefined;
      if (source) {
        source.setData(geojsonData);
      } else {
        map.addSource("h3-hex-source", {
          type: "geojson",
          data: geojsonData,
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
    },
    [onSelectLocation]
  );

  // Update Heatmap Layer when data changes or map finishes loading
  useEffect(() => {
    if (!mapRef.current || !isMapLoaded) return;
    renderHeatmapLayer(mapRef.current, heatmap);
  }, [heatmap, isMapLoaded, renderHeatmapLayer]);

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
          ? "w-9 h-9 text-sm bg-[#15130F] text-[#F6F1E7] font-black border-2 border-[#2F6E4E]"
          : loc.rank <= 3
          ? "w-8 h-8 text-xs bg-[#2F6E4E] text-[#F6F1E7] font-extrabold border border-[#F6F1E7]"
          : "w-7 h-7 text-xs bg-[#F6F1E7] text-[#15130F] border border-[#15130F]/30 font-bold"
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

  // Handle container resize
  useEffect(() => {
    if (!mapRef.current || !mapContainer.current) return;
    const resizeObserver = new ResizeObserver(() => {
      mapRef.current?.resize();
    });
    resizeObserver.observe(mapContainer.current);
    return () => {
      resizeObserver.disconnect();
    };
  }, [isMapLoaded]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />

      {/* Map Legend Overlay — bottom-right matching Nasiko */}
      <div className="absolute bottom-5 right-5 z-10 bg-white/90 backdrop-blur-md px-4 py-2.5 rounded-2xl text-xs space-y-1 shadow-sm border border-neutral-200 pointer-events-none">
        <div className="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mb-1">
          Score Gradient
        </div>
        <div className="w-32 h-2 rounded-full mb-1" style={{ background: "linear-gradient(90deg, #3b82f6, #10b981, #f59e0b, #ef4444)" }} />
        <div className="flex justify-between text-[10px] font-semibold text-neutral-400">
          <span>Lower (40)</span>
          <span>Higher (90+)</span>
        </div>
      </div>
    </div>
  );
}
