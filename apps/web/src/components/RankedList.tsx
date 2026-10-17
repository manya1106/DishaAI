"use client";

import React from "react";
import { LocationResult } from "../lib/types";
import { Award, TrendingUp, CheckSquare, Square, ChevronRight } from "lucide-react";

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
    <div className="flex flex-col h-full space-y-2.5 overflow-y-auto pr-1">
      <div className="flex items-center justify-between px-1 pb-1">
        <h2 className="text-sm font-bold text-slate-200 tracking-wide uppercase flex items-center gap-1.5">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          Ranked Zones ({locations.length})
        </h2>
        <span className="text-[11px] text-slate-400">Relative City Percentile</span>
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
                ? "bg-slate-800/90 border-emerald-500/80 shadow-lg shadow-emerald-500/10 scale-[1.01]"
                : "glass-panel hover:bg-slate-800/50 hover:border-slate-700 border-slate-800/60"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-start gap-2.5">
                {/* Rank Chip */}
                <div
                  className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                    loc.rank === 1
                      ? "bg-gradient-to-tr from-amber-500 to-yellow-400 text-slate-950 shadow-md shadow-amber-500/30"
                      : loc.rank <= 3
                      ? "bg-gradient-to-tr from-emerald-500 to-cyan-400 text-slate-950 font-bold"
                      : "bg-slate-800 text-slate-300 border border-slate-700"
                  }`}
                >
                  #{loc.rank}
                </div>

                <div>
                  <h3 className="font-semibold text-sm text-slate-100 leading-snug">
                    {loc.display_name}
                  </h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`text-[10px] font-medium px-1.5 py-0.2 rounded border ${
                        loc.confidence === "high"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : loc.confidence === "medium"
                          ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
                          : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                      }`}
                    >
                      {loc.confidence} conf.
                    </span>

                    {loc.strengths[0] && (
                      <span className="text-[11px] text-slate-400 truncate max-w-[140px] sm:max-w-[170px]">
                        {loc.strengths[0]}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Overall Score & Compare Toggle */}
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                <div className="flex items-baseline gap-1">
                  <span className="text-base font-extrabold text-white">
                    {loc.overall_score}
                  </span>
                  <span className="text-[10px] text-slate-400">/100</span>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onToggleCompare(loc.location_id);
                  }}
                  className={`flex items-center gap-1 text-[11px] px-2 py-0.5 rounded transition-colors ${
                    isCompared
                      ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/50"
                  }`}
                  title="Add to side-by-side comparison"
                >
                  {isCompared ? (
                    <CheckSquare className="w-3 h-3 text-indigo-400" />
                  ) : (
                    <Square className="w-3 h-3" />
                  )}
                  <span>Compare</span>
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
