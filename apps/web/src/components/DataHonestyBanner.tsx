import React from "react";
import { DatasetMeta } from "../lib/types";
import { Info, AlertTriangle, Database } from "lucide-react";

interface Props {
  dataset?: DatasetMeta;
}

export default function DataHonestyBanner({ dataset }: Props) {
  const isSimulated = dataset?.contains_simulated || dataset?.mode === "synthetic";

  return (
    <div className="w-full glass-panel border-t border-slate-800/80 px-4 py-2.5 text-xs text-slate-400">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-emerald-400" />
          <span>
            Data Source: <strong className="text-slate-200">OpenStreetMap Snapshot</strong> (As-of: {dataset?.as_of || "2026-10"})
          </span>
          <span className="text-slate-600">|</span>
          <span>{dataset?.attribution || "© OpenStreetMap contributors (ODbL)"}</span>
        </div>

        <div className="flex items-center gap-2">
          {isSimulated ? (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px] font-semibold">
              <AlertTriangle className="w-3 h-3" />
              SIMULATED DEMO FIXTURE
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-medium">
              VERIFIED OFFLINE SNAPSHOT
            </span>
          )}
          <span className="hidden sm:inline text-slate-500 text-[11px]">
            Rent is heuristic tier (1-5) • Relative percentile scoring
          </span>
        </div>
      </div>
    </div>
  );
}
