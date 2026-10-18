"use client";

import React, { Suspense, useEffect, useRef, useState, useMemo } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Navbar from "../../components/Navbar";
import MapComponent from "../../components/MapComponent";
import LocationReport from "../../components/LocationReport";
import CompareView from "../../components/CompareView";
import ChatPanel from "../../components/ChatPanel";
import DataHonestyBanner from "../../components/DataHonestyBanner";
import { api } from "../../lib/api";
import {
  AnalysisResult,
  MetaResponse,
} from "../../lib/types";
import {
  Compass,
  FileText,
  ArrowRightLeft,
  MessageSquare,
  Sparkles,
  Loader2,
  AlertCircle,
  CheckSquare,
  Square,
  Table as TableIcon,
} from "lucide-react";

function tryDecodeAnalysisId(id: string | null): { city_id?: string; category_id?: string; budget_tier?: string } | null {
  if (!id) return null;
  try {
    const base64 = id.replace(/-/g, "+").replace(/_/g, "/");
    const padding = "=".repeat((4 - (base64.length % 4)) % 4);
    if (typeof window !== "undefined") {
      const decoded = window.atob(base64 + padding);
      return JSON.parse(decoded);
    }
  } catch {
    // fallback
  }
  return null;
}

function heatColor(t: number): string {
  const clamped = Math.max(0, Math.min(1, t));
  const lightness = 95 - clamped * 45;
  return `hsl(145, 45%, ${lightness}%)`;
}

function ExploreContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const analysisIdParam = searchParams.get("analysisId");
  const decodedInit = useMemo(() => tryDecodeAnalysisId(analysisIdParam), [analysisIdParam]);

  // URL state defaults with decoded awareness
  const cityParam = searchParams.get("city") || decodedInit?.city_id || "blr";
  const categoryParam = searchParams.get("category") || decodedInit?.category_id || "cafe";
  const tierParam = searchParams.get("tier") || decodedInit?.budget_tier || "medium";

  const skipNextDropdownFetch = useRef(!!analysisIdParam);

  // Form selections
  const [selectedCity, setSelectedCity] = useState(cityParam);
  const [selectedCategory, setSelectedCategory] = useState(categoryParam);
  const [selectedTier, setSelectedTier] = useState(tierParam);

  // Metadata & Analysis Data
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // User UI state
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(null);
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"report" | "matrix" | "compare" | "chat">("report");
  const [deterministicMode, setDeterministicMode] = useState(false);

  // Fetch Metadata
  useEffect(() => {
    api
      .getMeta()
      .then((m) => setMeta(m))
      .catch((err) => console.error("Failed to load metadata:", err));
  }, []);

  // Load an analysis already computed by the /new-analysis wizard, once.
  useEffect(() => {
    if (!analysisIdParam) return;
    let active = true;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.getAnalysis(analysisIdParam);
        if (!active) return;
        setAnalysis(res);
        setSelectedCity(res.inputs.city_id);
        setSelectedCategory(res.inputs.category_id);
        setSelectedTier(res.inputs.budget_tier);
        if (res.locations.length > 0) {
          setSelectedLocationId(res.locations[0].location_id);
          if (res.locations.length >= 2) {
            setCompareIds([res.locations[0].location_id, res.locations[1].location_id]);
          }
        }
      } catch (err: unknown) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load the analysis from the wizard");
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [analysisIdParam]);

  // Fetch Analysis (dropdown-driven path)
  useEffect(() => {
    if (skipNextDropdownFetch.current) {
      skipNextDropdownFetch.current = false;
      return;
    }

    let active = true;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.createAnalysis({
          city_id: selectedCity,
          category_id: selectedCategory,
          budget_tier: selectedTier,
          top_n: 10,
        });
        if (!active) return;
        setAnalysis(res);
        if (res.locations.length > 0) {
          setSelectedLocationId(res.locations[0].location_id);
          if (res.locations.length >= 2) {
            setCompareIds([res.locations[0].location_id, res.locations[1].location_id]);
          }
        }
      } catch (err: unknown) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load analysis results");
      } finally {
        if (active) setLoading(false);
      }
    })();

    return () => {
      active = false;
    };
  }, [selectedCity, selectedCategory, selectedTier]);

  function handleAnalyzeSubmit(e: React.FormEvent) {
    e.preventDefault();
    router.push(
      `/explore?city=${selectedCity}&category=${selectedCategory}&tier=${selectedTier}`
    );
  }

  function handleSelectLocation(locationId: string) {
    setSelectedLocationId(locationId);
    if (activeTab === "matrix") {
      setActiveTab("report");
    }
  }

  function handleToggleCompare(locationId: string) {
    setCompareIds((prev) => {
      if (prev.includes(locationId)) {
        return prev.filter((id) => id !== locationId);
      }
      if (prev.length >= 3) {
        return [prev[1], prev[2], locationId];
      }
      return [...prev, locationId];
    });
  }

  const selectedLocation =
    analysis?.locations.find((l) => l.location_id === selectedLocationId) ||
    analysis?.locations[0] ||
    null;

  // Real KPI stats populated from the live analysis response
  const bestScore = analysis?.locations[0]?.overall_score ?? null;
  const zonesRanked = analysis?.locations.length ?? 0;
  const highConfidenceCount = analysis?.locations.filter((l) => l.confidence === "high").length ?? 0;
  const isLivePostgres = analysis?.dataset.mode === "postgres";

  // Matrix calculation data
  const signalKeys = useMemo(() => {
    if (!analysis?.weights) return [];
    return Object.keys(analysis.weights);
  }, [analysis?.weights]);

  const columnMax = useMemo(() => {
    if (!analysis || signalKeys.length === 0) return {};
    const maxes: Record<string, number> = {};
    for (const key of signalKeys) {
      const vals = analysis.locations.map(
        (loc) => loc.signals.find((s) => s.signal_id === key)?.contribution ?? 0
      );
      maxes[key] = Math.max(...vals, 0.1);
    }
    return maxes;
  }, [analysis, signalKeys]);

  return (
    <div className="min-h-screen flex flex-col bg-[#F6F1E7] text-[#15130F]" style={{ fontFamily: "var(--font-geist-sans)" }}>
      <Navbar />

      {/* ── Control & KPI Bar ───────────────────────────────────────────── */}
      <div className="bg-[#F6F1E7] border-b border-[#15130F]/10">
        <div className="px-4 sm:px-8 py-3">
          <div className="max-w-[1600px] mx-auto flex flex-wrap items-center justify-between gap-4">
            <form onSubmit={handleAnalyzeSubmit} className="flex flex-wrap items-center gap-3">
              {/* City */}
              <div className="flex items-center gap-1.5 text-xs">
                <span className="text-[#15130F]/50 font-medium">City:</span>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="bg-white border border-[#15130F]/20 rounded-lg px-2.5 py-1.5 text-[#15130F] font-medium focus:outline-none focus:border-[#15130F]"
                >
                  <option value="blr">Bengaluru (Bangalore)</option>
                </select>
              </div>
              {/* Category */}
              <div className="flex items-center gap-1.5 text-xs">
                <span className="text-[#15130F]/50 font-medium">Category:</span>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="bg-white border border-[#15130F]/20 rounded-lg px-2.5 py-1.5 text-[#15130F] font-medium focus:outline-none focus:border-[#15130F]"
                >
                  <option value="cafe">Café / Specialty Coffee</option>
                  <option value="pharmacy">Pharmacy / Chemist</option>
                  <option value="gym">Fitness Centre / Gym</option>
                </select>
              </div>
              {/* Budget */}
              <div className="flex items-center gap-1.5 text-xs">
                <span className="text-[#15130F]/50 font-medium">Budget:</span>
                <select
                  value={selectedTier}
                  onChange={(e) => setSelectedTier(e.target.value)}
                  className="bg-white border border-[#15130F]/20 rounded-lg px-2.5 py-1.5 text-[#15130F] font-medium focus:outline-none focus:border-[#15130F]"
                >
                  <option value="low">Budget (Tiers 1-2)</option>
                  <option value="medium">Standard (Tiers 1-3)</option>
                  <option value="high">Flagship (Tiers 1-5)</option>
                </select>
              </div>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-1.5 rounded-lg bg-[#15130F] hover:bg-[#2A2720] text-[#F6F1E7] font-medium text-xs flex items-center gap-1.5 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Scoring…</span>
                  </>
                ) : (
                  <>
                    <Compass className="w-3.5 h-3.5" />
                    <span>Analyze</span>
                  </>
                )}
              </button>
            </form>

            {/* AI mode toggle */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-[#15130F]/50">AI mode:</span>
              <button
                type="button"
                onClick={() => setDeterministicMode(!deterministicMode)}
                className={`px-2.5 py-1 rounded-lg border font-medium transition-colors flex items-center gap-1.5 ${
                  deterministicMode
                    ? "bg-[#3F5B6C]/10 text-[#3F5B6C] border-[#3F5B6C]/25"
                    : "bg-[#2F6E4E]/10 text-[#2F6E4E] border-[#2F6E4E]/25"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{deterministicMode ? "Deterministic Only" : "LLM + Verifier"}</span>
              </button>
            </div>
          </div>
        </div>

        {/* KPI Strip */}
        {analysis && (
          <div className="px-4 sm:px-8 pb-3">
            <div className="max-w-[1600px] mx-auto bg-white rounded-xl border border-[#15130F]/15 shadow-sm grid grid-cols-2 sm:grid-cols-4 divide-x divide-y sm:divide-y-0 divide-[#15130F]/12">
              <div className="px-5 py-3">
                <div className="text-2xl font-semibold text-[#15130F]" style={{ fontFamily: "var(--font-display)" }}>
                  {bestScore ?? "—"}
                </div>
                <div className="text-[11px] text-[#15130F]/55 mt-0.5 font-medium">Best score</div>
              </div>
              <div className="px-5 py-3">
                <div className="text-2xl font-semibold text-[#15130F]" style={{ fontFamily: "var(--font-display)" }}>
                  {zonesRanked}
                </div>
                <div className="text-[11px] text-[#15130F]/55 mt-0.5 font-medium">Candidate zones</div>
              </div>
              <div className="px-5 py-3">
                <div className="text-2xl font-semibold text-[#15130F]" style={{ fontFamily: "var(--font-display)" }}>
                  {highConfidenceCount}
                </div>
                <div className="text-[11px] text-[#15130F]/55 mt-0.5 font-medium">High-confidence zones</div>
              </div>
              <div className="px-5 py-3 bg-[#2F6E4E]/6 rounded-r-xl">
                <div className="text-2xl font-semibold text-[#2F6E4E] flex items-center gap-2" style={{ fontFamily: "var(--font-display)" }}>
                  {isLivePostgres && <span className="live-dot" />}
                  {isLivePostgres ? "Live" : "Snapshot"}
                </div>
                <div className="text-[11px] text-[#2F6E4E]/80 mt-0.5 font-medium">
                  {isLivePostgres ? "Real Postgres data, this request" : analysis.dataset.mode}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── Main Layout: Map (flex-1) + Right Sidebar (480px) ───────────── */}
      <main className="flex-1 flex overflow-hidden" style={{ height: "calc(100vh - 165px)", minHeight: 540 }}>
        {loading && !analysis && (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-[#15130F]/45">
            <Loader2 className="w-8 h-8 animate-spin text-[#2F6E4E]" />
            <p className="text-sm">Computing relative percentile scores…</p>
          </div>
        )}

        {error && !analysis && (
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="p-5 rounded-xl bg-[#8B3A2F]/8 border border-[#8B3A2F]/25 text-[#8B3A2F] text-sm max-w-md">
              <AlertCircle className="w-5 h-5 mb-2" />
              <p className="font-semibold">Error loading results:</p>
              <p className="mt-1 text-xs">{error}</p>
            </div>
          </div>
        )}

        {analysis && (
          <>
            {/* ── Map Column with Floating Overlays ────────────────── */}
            <div className="relative flex-1 min-w-0 p-4 pr-2">
              <div className="relative w-full h-full rounded-[24px] overflow-hidden border border-neutral-200 shadow-sm">
                <MapComponent
                  locations={analysis.locations}
                  heatmap={analysis.heatmap}
                  selectedLocationId={selectedLocationId}
                  onSelectLocation={handleSelectLocation}
                />

                {/* Score + Confidence Overlay — Top-Left */}
                {selectedLocation && (
                  <div className="absolute top-5 left-5 z-[400] flex gap-3 pointer-events-none">
                    <div className="bg-white/90 backdrop-blur-md px-5 py-3.5 rounded-2xl shadow-sm border border-neutral-200">
                      <div className="text-3xl font-bold tracking-tight tabular-nums text-[#15130F]">
                        {selectedLocation.overall_score.toFixed(1)}
                      </div>
                      <div className="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mt-0.5">
                        Peak Score
                      </div>
                    </div>
                    <div className="bg-white/90 backdrop-blur-md px-5 py-3.5 rounded-2xl shadow-sm border border-neutral-200">
                      <div className="text-3xl font-bold tracking-tight tabular-nums text-[#15130F]">
                        {Math.round(selectedLocation.coverage * 100)}%
                      </div>
                      <div className="text-[10px] font-semibold text-neutral-500 uppercase tracking-widest mt-0.5">
                        Confidence
                      </div>
                    </div>
                  </div>
                )}

                {/* Zone Selector Pills — Bottom-Left */}
                <div className="absolute bottom-5 left-5 z-[400] flex gap-2 flex-wrap max-w-[70%]">
                  {analysis.locations.slice(0, 6).map((loc) => {
                    const isSelected = loc.location_id === selectedLocationId;
                    const isCompared = compareIds.includes(loc.location_id);
                    return (
                      <div key={loc.location_id} className="flex items-center gap-1">
                        <button
                          onClick={() => handleSelectLocation(loc.location_id)}
                          className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold shadow-sm border transition-colors ${
                            isSelected
                              ? "bg-[#15130F] text-white border-[#15130F]"
                              : "bg-white/90 text-neutral-700 border-neutral-200 hover:bg-white"
                          }`}
                        >
                          #{loc.rank} {loc.display_name.split(" ").slice(0, 3).join(" ")}
                        </button>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleToggleCompare(loc.location_id); }}
                          title={isCompared ? "Remove from compare" : "Add to compare"}
                          className={`p-1 rounded-full border transition-colors ${
                            isCompared
                              ? "bg-[#2F6E4E]/15 border-[#2F6E4E]/35 text-[#2F6E4E]"
                              : "bg-white/80 border-neutral-200 text-neutral-400 hover:text-neutral-700"
                          }`}
                        >
                          {isCompared
                            ? <CheckSquare className="w-3 h-3" />
                            : <Square className="w-3 h-3" />
                          }
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* ── Right Sidebar (480px) ─────────────────────────────── */}
            <div className="w-[480px] shrink-0 flex flex-col bg-[#f5f5f7] p-4 pl-2 overflow-hidden">
              <div className="flex flex-col h-full bg-[#f5f5f7] rounded-[24px] overflow-hidden">

                {/* Zone Header */}
                {selectedLocation && (
                  <div className="bg-white px-6 py-4 border-b border-neutral-200 shrink-0">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-[#15130F] text-white">
                            Rank #{selectedLocation.rank}
                          </span>
                          <span
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                              selectedLocation.confidence === "high"
                                ? "bg-[#2F6E4E]/10 text-[#2F6E4E] border-[#2F6E4E]/30"
                                : selectedLocation.confidence === "medium"
                                ? "bg-[#A6693B]/10 text-[#A6693B] border-[#A6693B]/30"
                                : "bg-[#8B3A2F]/10 text-[#8B3A2F] border-[#8B3A2F]/30"
                            }`}
                          >
                            {selectedLocation.confidence} conf.
                          </span>
                        </div>
                        <h2 className="text-xl font-bold tracking-tight text-[#15130F]" style={{ fontFamily: "var(--font-display)" }}>
                          {selectedLocation.display_name}
                        </h2>
                        <p className="text-xs text-neutral-500 mt-0.5 font-medium capitalize">
                          {selectedCategory} &middot; {selectedTier} tier &middot; {Math.round(selectedLocation.coverage * 100)}% data coverage
                        </p>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-3xl font-bold tabular-nums text-[#15130F]" style={{ fontFamily: "var(--font-display)" }}>
                          {selectedLocation.overall_score.toFixed(1)}
                        </div>
                        <div className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest">
                          Score / 100
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Tab Bar */}
                <div className="flex items-center gap-0 bg-white border-b border-neutral-200 shrink-0 px-4">
                  {(["report", "matrix", "compare", "chat"] as const).map((tab) => (
                    <button
                      key={tab}
                      type="button"
                      onClick={() => setActiveTab(tab)}
                      className={`flex items-center gap-1.5 px-3.5 py-3 text-xs font-semibold border-b-2 transition-colors ${
                        activeTab === tab
                          ? "border-[#15130F] text-[#15130F]"
                          : "border-transparent text-neutral-400 hover:text-neutral-700"
                      }`}
                    >
                      {tab === "report" && <FileText className="w-3.5 h-3.5" />}
                      {tab === "matrix" && <TableIcon className="w-3.5 h-3.5" />}
                      {tab === "compare" && <ArrowRightLeft className="w-3.5 h-3.5" />}
                      {tab === "chat" && <MessageSquare className="w-3.5 h-3.5" />}
                      <span className="capitalize">{tab === "chat" ? "Ask AI" : tab === "matrix" ? "Matrix Working" : tab}</span>
                      {tab === "compare" && compareIds.length > 0 && (
                        <span className="w-4 h-4 rounded-full bg-[#2F6E4E]/20 text-[#2F6E4E] text-[10px] font-bold flex items-center justify-center">
                          {compareIds.length}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                {/* Tab Content — Scrollable */}
                <div className="flex-1 overflow-y-auto p-4 space-y-0">
                  {/* Tab 1: Detailed Single Zone Working Report */}
                  {activeTab === "report" && selectedLocation && (
                    <LocationReport
                      location={selectedLocation}
                      evidence={analysis.evidence}
                    />
                  )}

                  {/* Tab 2: Full Multi-Zone Signal Contribution Matrix (Nasiko style) */}
                  {activeTab === "matrix" && (
                    <div className="space-y-4">
                      <div className="p-4 rounded-2xl bg-white border border-neutral-200 shadow-sm space-y-2">
                        <div className="flex items-center justify-between">
                          <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
                            Signal Contribution Matrix
                          </h3>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-semibold text-neutral-400">Low</span>
                            <div className="w-16 h-2 rounded-full" style={{ background: "linear-gradient(90deg, hsl(145, 45%, 95%), hsl(145, 45%, 50%))" }} />
                            <span className="text-[10px] font-semibold text-neutral-400">High</span>
                          </div>
                        </div>
                        <p className="text-xs text-neutral-500 leading-relaxed">
                          All 9 deterministic signals for candidate zones. Shaded against other zones on the same signal, proving the mathematical distribution.
                        </p>
                      </div>

                      <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm overflow-hidden p-3">
                        <div className="overflow-x-auto">
                          <table className="w-full text-xs min-w-[540px] border-separate border-spacing-1">
                            <thead>
                              <tr>
                                <th className="text-left text-neutral-400 font-semibold uppercase tracking-wide pb-2 pr-2 sticky left-0 bg-white">
                                  Zone
                                </th>
                                {signalKeys.map((k) => (
                                  <th
                                    key={k}
                                    title={k.replace(/_/g, " ")}
                                    className="text-center text-neutral-400 font-semibold uppercase tracking-wide pb-2 px-1 text-[10px]"
                                  >
                                    {k.slice(0, 4)}
                                  </th>
                                ))}
                                <th className="text-right text-neutral-400 font-semibold uppercase tracking-wide pb-2 pl-2">
                                  Total
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {analysis.locations.map((loc) => {
                                const isCurrent = loc.location_id === selectedLocationId;
                                return (
                                  <tr
                                    key={loc.location_id}
                                    onClick={() => setSelectedLocationId(loc.location_id)}
                                    className={`cursor-pointer transition-colors ${
                                      isCurrent ? "font-bold" : "hover:bg-neutral-50"
                                    }`}
                                  >
                                    <td className="py-1.5 pr-2 truncate max-w-[120px] sticky left-0 bg-white">
                                      #{loc.rank} {loc.display_name.split(" ")[0]}
                                    </td>
                                    {signalKeys.map((k) => {
                                      const sig = loc.signals.find((s) => s.signal_id === k);
                                      const contrib = sig?.contribution ?? 0;
                                      const t = contrib / (columnMax[k] || 1);
                                      return (
                                        <td
                                          key={k}
                                          className="text-center tabular-nums font-mono text-[11px] rounded p-1"
                                          style={{
                                            background: heatColor(t),
                                            color: t > 0.6 ? "#15130F" : "#555",
                                          }}
                                          title={`${k.replace(/_/g, " ")}: +${contrib.toFixed(1)} pts (Score: ${sig?.score ?? "N/A"})`}
                                        >
                                          {contrib.toFixed(1)}
                                        </td>
                                      );
                                    })}
                                    <td className="text-right pl-2 font-bold tabular-nums font-mono text-[#2F6E4E]">
                                      {loc.overall_score.toFixed(1)}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tab 3: Compare */}
                  {activeTab === "compare" && (
                    <CompareView
                      analysisId={analysis.analysis_id}
                      allLocations={analysis.locations}
                      compareIds={compareIds}
                      onRemoveCompare={(id) => setCompareIds((prev) => prev.filter((i) => i !== id))}
                      onClearCompare={() => setCompareIds([])}
                    />
                  )}

                  {/* Tab 4: Ask AI Chat */}
                  {activeTab === "chat" && (
                    <ChatPanel
                      analysisId={analysis.analysis_id}
                      selectedLocations={analysis.locations.filter((l) =>
                        l.location_id === selectedLocationId || compareIds.includes(l.location_id)
                      )}
                      allEvidence={analysis.evidence}
                      deterministicMode={deterministicMode}
                      onToggleDeterministic={setDeterministicMode}
                    />
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </main>

      {/* Data Honesty Footer Banner */}
      <DataHonestyBanner dataset={analysis?.dataset} />
    </div>
  );
}

export default function ExplorePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#F6F1E7] flex items-center justify-center text-[#15130F]/50 text-sm">Loading Disha AI…</div>}>
      <ExploreContent />
    </Suspense>
  );
}
