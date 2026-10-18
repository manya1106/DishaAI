import React from "react";
import { DatasetMeta } from "../lib/types";
import { AlertTriangle, Database } from "lucide-react";

interface Props {
  dataset?: DatasetMeta;
}

export default function DataHonestyBanner({ dataset }: Props) {
  const isSimulated = dataset?.contains_simulated || dataset?.mode === "synthetic";
  const isLiveDb = dataset?.mode === "postgres";

  return (
    <div className="w-full bg-[#F6F1E7] border-t border-[#15130F]/10 px-4 py-2.5 text-xs text-[#15130F]/55">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-[#2F6E4E]" />
          <span>
            Data source: <strong className="text-[#15130F]">OpenStreetMap, real Bengaluru data</strong> (as of {dataset?.as_of || "2026-10"})
          </span>
          <span className="text-[#15130F]/25">|</span>
          <span>{dataset?.attribution || "© OpenStreetMap contributors (ODbL)"}</span>
        </div>

        <div className="flex items-center gap-2">
          {isSimulated ? (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#A6693B]/10 text-[#A6693B] border border-[#A6693B]/25 text-[11px] font-semibold">
              <AlertTriangle className="w-3 h-3" />
              SIMULATED DEMO FIXTURE
            </span>
          ) : isLiveDb ? (
            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#2F6E4E]/10 text-[#2F6E4E] border border-[#2F6E4E]/25 text-[11px] font-medium">
              <span className="live-dot" />
              LIVE POSTGRES — NOT A FIXTURE
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#2F6E4E]/10 text-[#2F6E4E] border border-[#2F6E4E]/25 text-[11px] font-medium">
              VERIFIED OFFLINE SNAPSHOT
            </span>
          )}
          <span className="hidden sm:inline text-[#15130F]/40 text-[11px]">
            Rent is heuristic tier (1–5) • Relative percentile scoring
          </span>
        </div>
      </div>
    </div>
  );
}
