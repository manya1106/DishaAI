"use client";

import React, { useEffect, useState } from "react";
import { LocationResult, CompareResult } from "../lib/types";
import { api } from "../lib/api";
import { ArrowRightLeft, Trophy, X } from "lucide-react";

interface Props {
  analysisId: string;
  allLocations: LocationResult[];
  compareIds: string[];
  onRemoveCompare: (locationId: string) => void;
  onClearCompare: () => void;
}

export default function CompareView({
  analysisId,
  compareIds,
  onRemoveCompare,
  onClearCompare,
}: Props) {
  const [compareData, setCompareData] = useState<CompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (compareIds.length < 2) return;

    let active = true;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.compareLocations(analysisId, compareIds);
        if (active) setCompareData(data);
      } catch (err: unknown) {
        if (active) setError(err instanceof Error ? err.message : "Failed to compare locations");
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [analysisId, compareIds]);

  if (compareIds.length < 2) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-[#15130F]/12 shadow-sm space-y-3">
        <ArrowRightLeft className="w-9 h-9 text-[#15130F]/30 mx-auto" strokeWidth={1.5} />
        <h3 className="text-base font-medium text-[#15130F]" style={{ fontFamily: "var(--font-display)" }}>
          Side-by-side zone comparison
        </h3>
        <p className="text-xs text-[#15130F]/55 max-w-sm mx-auto">
          Select at least 2 locations from the ranked list (click &quot;Compare&quot;) to inspect per-signal differentials, advantages, and trade-offs.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-8 text-center bg-white rounded-2xl border border-[#15130F]/12 shadow-sm space-y-2">
        <div className="w-6 h-6 border-2 border-[#2F6E4E] border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-xs text-[#15130F]/55">Computing deterministic signal deltas…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-xl bg-[#8B3A2F]/8 border border-[#8B3A2F]/25 text-xs text-[#8B3A2F]">
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
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-[#3F5B6C]/10 border border-[#3F5B6C]/25 text-xs font-medium text-[#3F5B6C]"
            >
              #{loc.rank} {loc.display_name}
              <button
                type="button"
                onClick={() => onRemoveCompare(loc.location_id)}
                className="hover:opacity-70"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>

        <button
          type="button"
          onClick={onClearCompare}
          className="text-xs text-[#15130F]/50 hover:text-[#15130F] underline underline-offset-2"
        >
          Clear all
        </button>
      </div>

      {/* Overall Score Comparison Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {compareData.locations.map((loc) => (
          <div
            key={loc.location_id}
            className="p-3 rounded-xl bg-white border border-[#15130F]/12 shadow-sm flex flex-col items-center text-center"
          >
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#15130F]/45">
              Rank #{loc.rank}
            </span>
            <h4 className="text-xs font-medium text-[#15130F] truncate max-w-full mt-0.5">
              {loc.display_name}
            </h4>
            <span className="text-2xl font-semibold text-[#2F6E4E] mt-1" style={{ fontFamily: "var(--font-display)" }}>
              {loc.overall_score}
            </span>
            <span className="text-[10px] text-[#15130F]/45 capitalize">{loc.confidence} conf.</span>
          </div>
        ))}
      </div>

      {/* Signal Deltas Table */}
      <div className="space-y-2 text-xs">
        <h4 className="text-xs font-semibold text-[#15130F]/60 uppercase tracking-wider">
          Per-signal comparative breakdown
        </h4>

        <div className="space-y-2">
          {compareData.signal_deltas.map((delta) => {
            return (
              <div
                key={delta.signal_id}
                className="p-3 rounded-xl bg-white border border-[#15130F]/12 shadow-sm space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-[#15130F] capitalize">
                    {delta.signal_id.replace(/_/g, " ")}
                  </span>

                  {delta.winner_location_id && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-[#2F6E4E] bg-[#2F6E4E]/10 px-2 py-0.5 rounded border border-[#2F6E4E]/20">
                      <Trophy className="w-3 h-3" />
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
                <div className="flex items-center justify-between text-[#15130F]/50 text-[11px] bg-[#15130F]/5 p-2 rounded-lg">
                  {compareData.locations.map((loc) => {
                    const score = delta.scores[loc.location_id];
                    const isWinner = delta.winner_location_id === loc.location_id;
                    return (
                      <div key={loc.location_id} className="flex flex-col">
                        <span className="text-[10px] text-[#15130F]/40">#{loc.rank} {loc.display_name.split(" ")[0]}</span>
                        <span
                          className={`font-mono font-semibold ${
                            isWinner ? "text-[#2F6E4E]" : "text-[#15130F]/70"
                          }`}
                        >
                          {score !== null ? `${score.toFixed(1)}/100` : "N/A"}
                        </span>
                      </div>
                    );
                  })}
                </div>

                <p className="text-[11px] text-[#15130F]/50 italic">
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
