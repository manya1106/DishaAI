"use client";

import React, { useState } from "react";
import { LocationResult, EvidenceItem } from "../lib/types";
import {
  CheckCircle2,
  AlertCircle,
  Table as TableIcon,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface Props {
  location: LocationResult;
  evidence: EvidenceItem[];
}

const PROVENANCE_STYLE: Record<string, string> = {
  measured: "bg-[#15130F]/8 text-[#15130F]/70 border-[#15130F]/20",
  estimated: "bg-[#3F5B6C]/10 text-[#3F5B6C] border-[#3F5B6C]/25",
  heuristic: "bg-[#A6693B]/10 text-[#A6693B] border-[#A6693B]/25",
  unavailable: "bg-[#8B3A2F]/10 text-[#8B3A2F] border-[#8B3A2F]/25",
};

export default function LocationReport({ location, evidence }: Props) {
  const [showEvidenceTable, setShowEvidenceTable] = useState(false);

  const locEvidence = evidence.filter((e) => e.location_id === location.location_id);

  return (
    <div className="space-y-5 overflow-y-auto pr-1">
      {/* Header Summary Card */}
      <div className="p-4 rounded-xl bg-[#15130F] text-[#F6F1E7]">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-[#2F6E4E]/25 text-[#2F6E4E]">
                Rank #{location.rank}
              </span>
              <span className="text-xs text-[#F6F1E7]/60">
                Confidence: <strong className="text-[#F6F1E7]/90 capitalize">{location.confidence}</strong> ({Math.round(location.coverage * 100)}% coverage)
              </span>
            </div>
            <h2 className="text-lg font-medium mt-1" style={{ fontFamily: "var(--font-display)" }}>
              {location.display_name}
            </h2>
          </div>

          <div className="flex flex-col items-end">
            <span className="text-3xl font-semibold" style={{ fontFamily: "var(--font-display)" }}>
              {location.overall_score}
            </span>
            <span className="text-[10px] text-[#F6F1E7]/50">Overall score (0–100)</span>
          </div>
        </div>

        {/* Why vs Neighbours */}
        {location.why_vs_neighbours.length > 0 && (
          <div className="mt-3 pt-3 border-t border-[#F6F1E7]/15 text-xs text-[#F6F1E7]/75">
            <strong className="text-[#2F6E4E]">Relative rank context:</strong>{" "}
            {location.why_vs_neighbours.join(" ")}
          </div>
        )}
      </div>

      {/* Nine Signal Bars */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-semibold text-[#15130F]/60 uppercase tracking-wider">
            Nine location signals
          </h3>
          <span className="text-[10px] text-[#15130F]/40">Weight &amp; contribution</span>
        </div>

        <div className="space-y-2.5">
          {location.signals.map((sig) => {
            const isUnavailable = sig.status === "unavailable" || sig.score === null;
            const scoreVal = sig.score ?? 0;

            return (
              <div
                key={sig.signal_id}
                className="p-3 rounded-lg bg-white border border-[#15130F]/12 shadow-sm hover:border-[#15130F]/22 hover:shadow-md transition-all text-xs"
              >
                <div className="flex items-center justify-between mb-1.5 flex-wrap gap-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-[#15130F] capitalize">
                      {sig.signal_id.replace(/_/g, " ")}
                    </span>
                    <span
                      className={`text-[9px] uppercase font-bold px-1.5 py-0.5 rounded border ${
                        PROVENANCE_STYLE[sig.provenance] ?? PROVENANCE_STYLE.unavailable
                      }`}
                    >
                      {sig.provenance}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-[#15130F]/45">
                      Wt: {(sig.effective_weight * 100).toFixed(0)}%
                    </span>
                    <span className="font-mono font-medium text-[#15130F]">
                      {isUnavailable ? "N/A" : `${scoreVal.toFixed(1)}/100`}
                    </span>
                    <span className="text-[#2F6E4E] font-mono font-medium">
                      +{sig.contribution.toFixed(1)} pts
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full h-1.5 rounded-full bg-[#15130F]/8 overflow-hidden">
                  {isUnavailable ? (
                    <div className="w-full h-full bg-[#15130F]/10" />
                  ) : (
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        scoreVal >= 70
                          ? "bg-[#2F6E4E]"
                          : scoreVal >= 45
                          ? "bg-[#3F5B6C]"
                          : "bg-[#A6693B]"
                      }`}
                      style={{ width: `${Math.max(4, scoreVal)}%` }}
                    />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Strengths & Limitations */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div className="p-3.5 rounded-xl bg-white border border-[#2F6E4E]/25 shadow-sm">
          <h4 className="font-semibold text-[#2F6E4E] flex items-center gap-1.5 mb-2">
            <CheckCircle2 className="w-4 h-4" />
            Key strengths
          </h4>
          <ul className="space-y-1.5 text-[#15130F]/70">
            {location.strengths.length > 0 ? (
              location.strengths.map((str, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-[#2F6E4E]">•</span>
                  <span>{str}</span>
                </li>
              ))
            ) : (
              <li className="text-[#15130F]/40 italic">No standout high-scoring outliers</li>
            )}
          </ul>
        </div>

        <div className="p-3.5 rounded-xl bg-white border border-[#A6693B]/25 shadow-sm">
          <h4 className="font-semibold text-[#A6693B] flex items-center gap-1.5 mb-2">
            <AlertCircle className="w-4 h-4" />
            Limitations &amp; risks
          </h4>
          <ul className="space-y-1.5 text-[#15130F]/70">
            {location.limitations.length > 0 ? (
              location.limitations.map((lim, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-[#A6693B]">•</span>
                  <span>{lim}</span>
                </li>
              ))
            ) : (
              <li className="text-[#15130F]/40 italic">Balanced distribution; no major constraints</li>
            )}
          </ul>
        </div>
      </div>

      {/* Raw Evidence Table Collapsible */}
      <div className="rounded-xl bg-white border border-[#15130F]/12 shadow-sm overflow-hidden text-xs">
        <button
          type="button"
          onClick={() => setShowEvidenceTable(!showEvidenceTable)}
          className="w-full p-3.5 flex items-center justify-between text-left text-[#15130F]/70 hover:text-[#15130F] hover:bg-[#15130F]/4 transition-colors"
        >
          <div className="flex items-center gap-2">
            <TableIcon className="w-4 h-4 text-[#3F5B6C]" />
            <span className="font-semibold">Raw OpenStreetMap evidence items ({locEvidence.length})</span>
          </div>
          {showEvidenceTable ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showEvidenceTable && (
          <div className="p-3 border-t border-[#15130F]/10 overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[#15130F]/10 text-[10px] uppercase text-[#15130F]/45">
                  <th className="py-1.5 px-2">Evidence ID</th>
                  <th className="py-1.5 px-2">Label</th>
                  <th className="py-1.5 px-2">Raw value</th>
                  <th className="py-1.5 px-2">Class</th>
                  <th className="py-1.5 px-2">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#15130F]/8 text-[11px] text-[#15130F]/75">
                {locEvidence.map((ev) => (
                  <tr key={ev.evidence_id} className="hover:bg-[#15130F]/4">
                    <td className="py-1.5 px-2 font-mono text-[10px] text-[#2F6E4E]">{ev.evidence_id}</td>
                    <td className="py-1.5 px-2">{ev.label}</td>
                    <td className="py-1.5 px-2 font-semibold text-[#15130F]">
                      {String(ev.value)} {ev.unit || ""}
                    </td>
                    <td className="py-1.5 px-2 capitalize">{ev.provenance}</td>
                    <td className="py-1.5 px-2 text-[#15130F]/45 text-[10px]">{ev.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
