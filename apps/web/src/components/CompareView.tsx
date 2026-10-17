"use client";

import React, { useEffect, useState } from "react";
import { LocationResult, CompareResult, SignalDelta } from "../lib/types";
import { api } from "../lib/api";
import { ArrowRightLeft, Trophy, AlertCircle, X, Sparkles } from "lucide-react";

interface Props {
  analysisId: string;
  allLocations: LocationResult[];
  compareIds: string[];
  onRemoveCompare: (locationId: string) => void;
  onClearCompare: () => void;
}

export default function CompareView({
  analysisId,
  allLocations,
  compareIds,
  onRemoveCompare,
  onClearCompare,
}: Props) {
  const [compareData, setCompareData] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (compareIds.length < 2) {
      setCompareData(null);
      return;
    }

    setLoading(true);
    setError(null);

    api
      .compareLocations(analysisId, compareIds)
      .then((data) => {
        setCompareData(data);
      })
      .catch((err) => {
        setError(err.message || "Failed to compare locations");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [analysisId, compareIds]);

  if (compareIds.length < 2) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl border-slate-800 space-y-3">
        <ArrowRightLeft className="w-10 h-10 text-slate-500 mx-auto" />
        <h3 className="text-base font-bold text-slate-200">Side-by-Side Zone Comparison</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto">
          Select at least 2 locations from the ranked list (click &quot;Compare&quot;) to inspect per-signal differentials, advantages, and trade-offs.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl space-y-2">
        <div className="w-6 h-6 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-slate-400">Computing deterministic signal deltas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300">
        <p className="font-semibold">Comparison error: {error}</p>
      </div>
    );
  }

  if (!compareData) return null;

  return (
    <div className="space-y-4 overflow-y-auto pr-1">
      {/* Header bar with shortlisted badges */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 flex-wrap">
          {compareData.locations.map((loc) => (
            <span
              key={loc.location_id}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-500/15 border border-indigo-500/30 text-xs font-semibold text-indigo-300"
            >
              #{loc.rank} {loc.display_name}
              <button
                type="button"
                onClick={() => onRemoveCompare(loc.location_id)}
                className="hover:text-white"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>

        <button
          type="button"
          onClick={onClearCompare}
          className="text-xs text-slate-400 hover:text-white underline underline-offset-2"
        >
          Clear All
        </button>
      </div>

      {/* Overall Score Comparison Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {compareData.locations.map((loc) => (
          <div
            key={loc.location_id}
            className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex flex-col items-center text-center shadow-lg"
          >
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Rank #{loc.rank}
            </span>
            <h4 className="text-xs font-semibold text-white truncate max-w-full mt-0.5">
              {loc.display_name}
            </h4>
            <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-300 mt-1">
              {loc.overall_score}
            </span>
            <span className="text-[10px] text-slate-500 capitalize">{loc.confidence} Conf.</span>
          </div>
        ))}
      </div>

      {/* Signal Deltas Table */}
      <div className="space-y-2 text-xs">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
          Per-Signal Comparative Breakdown
        </h4>

        <div className="space-y-2">
          {compareData.signal_deltas.map((delta) => {
            return (
              <div
                key={delta.signal_id}
                className="p-3 rounded-xl glass-panel border-slate-800/80 space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200 capitalize">
                    {delta.signal_id.replace(/_/g, " ")}
                  </span>

                  {delta.winner_location_id && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      <Trophy className="w-3 h-3 text-amber-400" />
                      Leader:{" "}
                      {
                        compareData.locations.find(
                          (l) => l.location_id === delta.winner_location_id
                        )?.display_name
                      }
                    </span>
                  )}
                </div>

                {/* Scores row */}
                <div className="flex items-center justify-between text-slate-400 text-[11px] bg-slate-950/40 p-2 rounded-lg">
                  {compareData.locations.map((loc) => {
                    const score = delta.scores[loc.location_id];
                    const isWinner = delta.winner_location_id === loc.location_id;
                    return (
                      <div key={loc.location_id} className="flex flex-col">
                        <span className="text-[10px] text-slate-500">#{loc.rank} {loc.display_name.split(" ")[0]}</span>
                        <span
                          className={`font-mono font-bold ${
                            isWinner ? "text-emerald-400" : "text-slate-300"
                          }`}
                        >
                          {score !== null ? `${score.toFixed(1)}/100` : "N/A"}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <p className="text-[11px] text-slate-400 italic">
                  {delta.delta_explanation}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
