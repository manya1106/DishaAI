"use client";

import React, { useState } from "react";
import { LocationResult, EvidenceItem } from "../lib/types";
import {
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  BarChart3,
  Layers,
  Table as TableIcon,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface Props {
  location: LocationResult;
  evidence: EvidenceItem[];
}

export default function LocationReport({ location, evidence }: Props) {
  const [showEvidenceTable, setShowEvidenceTable] = useState(false);

  const locEvidence = evidence.filter((e) => e.location_id === location.location_id);

  return (
    <div className="space-y-5 overflow-y-auto pr-1">
      {/* Header Summary Card */}
      <div className="p-4 rounded-xl bg-gradient-to-br from-slate-900 to-slate-800/80 border border-slate-700/80 shadow-lg">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Rank #{location.rank}
              </span>
              <span className="text-xs text-slate-400">
                Confidence: <strong className="text-slate-200 capitalize">{location.confidence}</strong> ({Math.round(location.coverage * 100)}% coverage)
              </span>
            </div>
            <h2 className="text-lg font-extrabold text-white mt-1">
              {location.display_name}
            </h2>
          </div>

          <div className="flex flex-col items-end">
            <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-300">
              {location.overall_score}
            </span>
            <span className="text-[10px] text-slate-400">Overall Score (0-100)</span>
          </div>
        </div>

        {/* Why vs Neighbours */}
        {location.why_vs_neighbours.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-800 text-xs text-slate-300 bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/50">
            <strong className="text-emerald-400">Relative Rank Context:</strong>{" "}
            {location.why_vs_neighbours.join(" ")}
          </div>
        )}
      </div>

      {/* Nine Signal Bars */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
            <BarChart3 className="w-3.5 h-3.5 text-cyan-400" />
            Nine Location Signals (Normalized Relative Percentiles)
          </h3>
          <span className="text-[10px] text-slate-500">Weight & Contribution</span>
        </div>

        <div className="space-y-2.5">
          {location.signals.map((sig) => {
            const isUnavailable = sig.status === "unavailable" || sig.score === null;
            const scoreVal = sig.score ?? 0;

            return (
              <div
                key={sig.signal_id}
                className="p-3 rounded-lg glass-panel border-slate-800/80 hover:border-slate-700 transition-all text-xs"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-slate-200 capitalize">
                      {sig.signal_id.replace(/_/g, " ")}
                    </span>
                    {/* Provenance Badge */}
                    <span
                      className={`text-[9px] uppercase font-bold px-1.5 py-0.2 rounded border ${
                        sig.provenance === "measured"
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                          : sig.provenance === "estimated"
                          ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"
                          : sig.provenance === "heuristic"
                          ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                          : "bg-slate-700/30 text-slate-400 border-slate-600"
                      }`}
                    >
                      {sig.provenance}
                    </span>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="text-slate-400">
                      Wt: {(sig.effective_weight * 100).toFixed(0)}%
                    </span>
                    <span className="font-mono font-bold text-slate-100">
                      {isUnavailable ? "N/A" : `${scoreVal.toFixed(1)}/100`}
                    </span>
                    <span className="text-emerald-400 font-mono font-bold">
                      +{sig.contribution.toFixed(1)} pts
                    </span>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="w-full h-2 rounded-full bg-slate-800/80 overflow-hidden">
                  {isUnavailable ? (
                    <div className="w-full h-full bg-slate-700/40 repeating-diagonal-stripes" />
                  ) : (
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        scoreVal >= 70
                          ? "bg-gradient-to-r from-emerald-500 to-cyan-400"
                          : scoreVal >= 45
                          ? "bg-gradient-to-r from-cyan-500 to-blue-500"
                          : "bg-gradient-to-r from-amber-500 to-rose-500"
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
        {/* Strengths */}
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-emerald-500/20">
          <h4 className="font-bold text-emerald-400 flex items-center gap-1.5 mb-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            Key Strengths
          </h4>
          <ul className="space-y-1.5 text-slate-300">
            {location.strengths.length > 0 ? (
              location.strengths.map((str, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-emerald-400">•</span>
                  <span>{str}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-500 italic">No standout high-scoring outliers</li>
            )}
          </ul>
        </div>

        {/* Limitations */}
        <div className="p-3.5 rounded-xl bg-slate-900/60 border border-amber-500/20">
          <h4 className="font-bold text-amber-400 flex items-center gap-1.5 mb-2">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            Limitations & Risks
          </h4>
          <ul className="space-y-1.5 text-slate-300">
            {location.limitations.length > 0 ? (
              location.limitations.map((lim, idx) => (
                <li key={idx} className="flex items-start gap-1.5">
                  <span className="text-amber-400">•</span>
                  <span>{lim}</span>
                </li>
              ))
            ) : (
              <li className="text-slate-500 italic">Balanced distribution; no major constraints</li>
            )}
          </ul>
        </div>
      </div>

      {/* Raw Evidence Table Collapsible */}
      <div className="rounded-xl glass-panel border-slate-800/80 overflow-hidden text-xs">
        <button
          type="button"
          onClick={() => setShowEvidenceTable(!showEvidenceTable)}
          className="w-full p-3.5 flex items-center justify-between text-left text-slate-300 hover:text-white hover:bg-slate-800/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <TableIcon className="w-4 h-4 text-indigo-400" />
            <span className="font-bold">Raw OpenStreetMap Evidence Items ({locEvidence.length})</span>
          </div>
          {showEvidenceTable ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showEvidenceTable && (
          <div className="p-3 border-t border-slate-800/80 overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[10px] uppercase text-slate-400">
                  <th className="py-1.5 px-2">Evidence ID</th>
                  <th className="py-1.5 px-2">Label</th>
                  <th className="py-1.5 px-2">Raw Value</th>
                  <th className="py-1.5 px-2">Class</th>
                  <th className="py-1.5 px-2">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-[11px] text-slate-300">
                {locEvidence.map((ev) => (
                  <tr key={ev.evidence_id} className="hover:bg-slate-800/40">
                    <td className="py-1.5 px-2 font-mono text-[10px] text-emerald-400">{ev.evidence_id}</td>
                    <td className="py-1.5 px-2">{ev.label}</td>
                    <td className="py-1.5 px-2 font-semibold text-white">
                      {String(ev.value)} {ev.unit || ""}
                    </td>
                    <td className="py-1.5 px-2 capitalize">{ev.provenance}</td>
                    <td className="py-1.5 px-2 text-slate-400 text-[10px]">{ev.source}</td>
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
