"use client";

import React, { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Navbar from "../../components/Navbar";
import MapComponent from "../../components/MapComponent";
import RankedList from "../../components/RankedList";
import LocationReport from "../../components/LocationReport";
import CompareView from "../../components/CompareView";
import ChatPanel from "../../components/ChatPanel";
import DataHonestyBanner from "../../components/DataHonestyBanner";
import { api } from "../../lib/api";
import {
  AnalysisResult,
  MetaResponse,
  LocationResult,
  EvidenceItem,
} from "../../lib/types";
import {
  Compass,
  FileText,
  ArrowRightLeft,
  MessageSquare,
  Sparkles,
  Loader2,
  AlertCircle,
  HelpCircle,
} from "lucide-react";

function ExploreContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // URL state defaults
  const cityParam = searchParams.get("city") || "blr";
  const categoryParam = searchParams.get("category") || "cafe";
  const tierParam = searchParams.get("tier") || "medium";

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
  const [activeTab, setActiveTab] = useState<"report" | "compare" | "chat">("report");
  const [deterministicMode, setDeterministicMode] = useState(false);

  // Fetch Metadata
  useEffect(() => {
    api
      .getMeta()
      .then((m) => setMeta(m))
      .catch((err) => console.error("Failed to load metadata:", err));
  }, []);

  // Fetch Analysis
  useEffect(() => {
    setLoading(true);
    setError(null);

    api
      .createAnalysis({
        city_id: selectedCity,
        category_id: selectedCategory,
        budget_tier: selectedTier,
        top_n: 10,
      })
      .then((res) => {
        setAnalysis(res);
        if (res.locations.length > 0) {
          setSelectedLocationId(res.locations[0].location_id);
          // Default compare to top 2
          if (res.locations.length >= 2) {
            setCompareIds([res.locations[0].location_id, res.locations[1].location_id]);
          }
        }
      })
      .catch((err) => {
        setError(err.message || "Failed to load analysis results");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [selectedCity, selectedCategory, selectedTier]);

  function handleAnalyzeSubmit(e: React.FormEvent) {
    e.preventDefault();
    router.push(
      `/explore?city=${selectedCity}&category=${selectedCategory}&tier=${selectedTier}`
    );
  }

  function handleSelectLocation(locationId: string) {
    setSelectedLocationId(locationId);
    setActiveTab("report");
  }

  function handleToggleCompare(locationId: string) {
    setCompareIds((prev) => {
      if (prev.includes(locationId)) {
        return prev.filter((id) => id !== locationId);
      }
      if (prev.length >= 3) {
        return [prev[1], prev[2], locationId]; // keep max 3
      }
      return [...prev, locationId];
    });
  }

  const selectedLocation =
    analysis?.locations.find((l) => l.location_id === selectedLocationId) ||
    analysis?.locations[0] ||
    null;

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <Navbar />

      {/* Control Selector Bar */}
      <section className="glass-panel border-b border-slate-800/80 px-4 sm:px-8 py-3.5 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <form
            onSubmit={handleAnalyzeSubmit}
            className="flex flex-wrap items-center gap-3"
          >
            {/* City Selector */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-medium">City:</span>
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-white font-semibold focus:outline-none focus:border-emerald-500"
              >
                <option value="blr">Bengaluru (Bangalore)</option>
              </select>
            </div>

            {/* Category Selector */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-medium">Category:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-white font-semibold focus:outline-none focus:border-emerald-500"
              >
                <option value="cafe">Café / Specialty Coffee</option>
                <option value="pharmacy">Pharmacy / Chemist</option>
                <option value="gym">Fitness Centre / Gym</option>
              </select>
            </div>

            {/* Budget Tier Selector */}
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-slate-400 font-medium">Budget:</span>
              <select
                value={selectedTier}
                onChange={(e) => setSelectedTier(e.target.value)}
                className="bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-white font-semibold focus:outline-none focus:border-emerald-500"
              >
                <option value="low">Budget (Tiers 1-2)</option>
                <option value="medium">Standard (Tiers 1-3)</option>
                <option value="high">Flagship (Tiers 1-5)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shadow-md shadow-emerald-500/20 transition-all disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Scoring...</span>
                </>
              ) : (
                <>
                  <Compass className="w-3.5 h-3.5" />
                  <span>Analyze</span>
                </>
              )}
            </button>
          </form>

          {/* AI Narration Toggle */}
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">AI Mode:</span>
            <button
              type="button"
              onClick={() => setDeterministicMode(!deterministicMode)}
              className={`px-2.5 py-1 rounded-lg border font-semibold transition-colors flex items-center gap-1.5 ${
                deterministicMode
                  ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/30"
                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{deterministicMode ? "Deterministic Only" : "LLM + Verifier"}</span>
            </button>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-5 min-h-[600px]">
        {/* Left Column: Ranked Locations (3.5 cols) */}
        <section className="lg:col-span-4 h-[650px] flex flex-col glass-panel rounded-2xl p-4 border-slate-800/80 shadow-xl">
          {loading && !analysis ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-2 text-slate-400">
              <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
              <p className="text-xs">Computing relative percentile scores...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
              <AlertCircle className="w-5 h-5 mb-1" />
              <p className="font-bold">Error loading locations:</p>
              <p>{error}</p>
            </div>
          ) : analysis ? (
            <RankedList
              locations={analysis.locations}
              selectedLocationId={selectedLocationId}
              compareIds={compareIds}
              onSelectLocation={handleSelectLocation}
              onToggleCompare={handleToggleCompare}
            />
          ) : null}
        </section>

        {/* Center Column: Map (4.5 cols) */}
        <section className="lg:col-span-4 h-[650px] rounded-2xl overflow-hidden shadow-xl">
          {analysis ? (
            <MapComponent
              locations={analysis.locations}
              heatmap={analysis.heatmap}
              selectedLocationId={selectedLocationId}
              onSelectLocation={handleSelectLocation}
            />
          ) : (
            <div className="w-full h-full glass-panel rounded-2xl flex items-center justify-center text-slate-500 text-xs">
              Map loading...
            </div>
          )}
        </section>

        {/* Right Column: Multi-tab Panel (4 cols) */}
        <section className="lg:col-span-4 h-[650px] flex flex-col glass-panel rounded-2xl p-4 border-slate-800/80 shadow-xl">
          {/* Tab Headers */}
          <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-900 border border-slate-800 text-xs mb-3">
            <button
              type="button"
              onClick={() => setActiveTab("report")}
              className={`flex-1 py-1.5 rounded-lg font-semibold flex items-center justify-center gap-1.5 transition-all ${
                activeTab === "report"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              <span>Report</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("compare")}
              className={`flex-1 py-1.5 rounded-lg font-semibold flex items-center justify-center gap-1.5 transition-all ${
                activeTab === "compare"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <ArrowRightLeft className="w-3.5 h-3.5 text-indigo-400" />
              <span>Compare</span>
              {compareIds.length > 0 && (
                <span className="w-4 h-4 rounded-full bg-indigo-500/20 text-indigo-400 text-[10px] font-bold flex items-center justify-center">
                  {compareIds.length}
                </span>
              )}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("chat")}
              className={`flex-1 py-1.5 rounded-lg font-semibold flex items-center justify-center gap-1.5 transition-all ${
                activeTab === "chat"
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />
              <span>Ask AI</span>
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-hidden">
            {analysis && (
              <>
                {activeTab === "report" && selectedLocation && (
                  <LocationReport
                    location={selectedLocation}
                    evidence={analysis.evidence}
                  />
                )}

                {activeTab === "compare" && (
                  <CompareView
                    analysisId={analysis.analysis_id}
                    allLocations={analysis.locations}
                    compareIds={compareIds}
                    onRemoveCompare={(id) => setCompareIds((prev) => prev.filter((i) => i !== id))}
                    onClearCompare={() => setCompareIds([])}
                  />
                )}

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
              </>
            )}
          </div>
        </section>
      </main>

      {/* Data Honesty Footer Banner */}
      <DataHonestyBanner dataset={analysis?.dataset} />
    </div>
  );
}

export default function ExplorePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 text-sm">Loading Disha AI...</div>}>
      <ExploreContent />
    </Suspense>
  );
}
