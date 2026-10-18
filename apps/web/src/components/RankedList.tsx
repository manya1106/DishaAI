"use client";

import React from "react";
import { LocationResult } from "../lib/types";
import { CheckSquare, Square } from "lucide-react";

interface Props {
  locations: LocationResult[];
  selectedLocationId: string | null;
  compareIds: string[];
  onSelectLocation: (locationId: string) => void;
  onToggleCompare: (locationId: string) => void;
}

export default function RankedList({
  locations,
  selectedLocationId,
  compareIds,
  onSelectLocation,
  onToggleCompare,
}: Props) {
  return (
    <div className="flex flex-col h-full space-y-2 overflow-y-auto pr-1">
      <div className="flex items-center justify-between px-1 pb-1">
        <h2
          className="text-sm font-semibold text-[#15130F] tracking-tight"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Ranked zones ({locations.length})
        </h2>
        <span className="text-[11px] text-[#15130F]/50">Relative city percentile</span>
      </div>

      {locations.map((loc) => {
        const isSelected = loc.location_id === selectedLocationId;
        const isCompared = compareIds.includes(loc.location_id);

        return (
          <div
            key={loc.location_id}
            onClick={() => onSelectLocation(loc.location_id)}
            className={`p-3.5 rounded-xl transition-all cursor-pointer border ${
              isSelected
                ? "bg-[#15130F] border-[#15130F] shadow-md"
                : "bg-white border-[#15130F]/15 hover:border-[#15130F]/35 shadow-sm hover:shadow-md"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-2.5">
                {/* Rank Chip */}
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                    loc.rank === 1
                      ? "bg-[#2F6E4E] text-[#F6F1E7]"
                      : loc.rank <= 3
                      ? isSelected
                        ? "bg-[#F6F1E7] text-[#15130F]"
                        : "bg-[#2F6E4E]/15 text-[#2F6E4E]"
                      : isSelected
                      ? "bg-[#F6F1E7]/20 text-[#F6F1E7]"
                      : "bg-[#15130F]/8 text-[#15130F]/60"
                  }`}
                >
                  #{loc.rank}
                </div>

                <div>
                  <h3 className={`font-semibold text-sm leading-snug ${isSelected ? "text-[#F6F1E7]" : "text-[#15130F]"}`}>
                    {loc.display_name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`text-[10px] font-semibold px-1.5 py-0.5 rounded border ${
                        isSelected
                          ? "border-[#F6F1E7]/35 text-[#F6F1E7]/85"
                          : loc.confidence === "high"
                          ? "bg-[#2F6E4E]/10 text-[#2F6E4E] border-[#2F6E4E]/30"
                          : loc.confidence === "medium"
                          ? "bg-[#A6693B]/10 text-[#A6693B] border-[#A6693B]/30"
                          : "bg-[#8B3A2F]/10 text-[#8B3A2F] border-[#8B3A2F]/30"
                      }`}
                    >
                      {loc.confidence} conf.
                    </span>

                    {loc.strengths[0] && (
                      <span className={`text-[11px] truncate max-w-[140px] sm:max-w-[170px] ${isSelected ? "text-[#F6F1E7]/65" : "text-[#15130F]/55"}`}>
                        {loc.strengths[0]}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Overall Score & Compare Toggle */}
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                <div className="flex items-baseline gap-1">
                  <span className={`text-lg font-semibold ${isSelected ? "text-[#F6F1E7]" : "text-[#15130F]"}`} style={{ fontFamily: "var(--font-display)" }}>
                    {loc.overall_score}
                  </span>
                  <span className={`text-[10px] ${isSelected ? "text-[#F6F1E7]/55" : "text-[#15130F]/40"}`}>/100</span>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleCompare(loc.location_id);
                  }}
                  className={`flex items-center gap-1 text-[11px] px-2 py-0.5 rounded transition-colors ${
                    isCompared
                      ? "bg-[#2F6E4E]/15 text-[#2F6E4E] border border-[#2F6E4E]/35"
                      : isSelected
                      ? "text-[#F6F1E7]/65 hover:text-[#F6F1E7]"
                      : "text-[#15130F]/50 hover:text-[#15130F]"
                  }`}
                  title="Add to side-by-side comparison"
                >
                  {isCompared ? (
                    <CheckSquare className="w-3 h-3" />
                  ) : (
                    <Square className="w-3 h-3" />
                  )}
                  <span>Compare</span>
                </button>
              </div>
            </div>

            {/* Score bar — the visual "██" the SiteScout wireframe shows next to each rank */}
            <div className={`mt-2.5 h-1.5 rounded-full overflow-hidden ${isSelected ? "bg-[#F6F1E7]/20" : "bg-[#15130F]/8"}`}>
              <div
                className={`h-full rounded-full ${
                  isSelected
                    ? "bg-[#F6F1E7]"
                    : loc.rank === 1
                    ? "bg-[#2F6E4E]"
                    : loc.rank <= 3
                    ? "bg-[#2F6E4E]/70"
                    : "bg-[#15130F]/40"
                }`}
                style={{ width: `${Math.max(4, loc.overall_score)}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
