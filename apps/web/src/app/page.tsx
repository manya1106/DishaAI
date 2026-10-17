import React from "react";
import Link from "next/link";
import Navbar from "../components/Navbar";
import {
  Compass,
  ShieldCheck,
  BarChart3,
  MapPin,
  CheckCircle2,
  ArrowRight,
  Database,
  Lock,
  Layers,
  Sparkles,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-slate-950">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 px-4 sm:px-8">
        {/* Background glow effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-gradient-to-tr from-emerald-500/20 via-cyan-500/20 to-indigo-500/20 blur-[120px] rounded-full pointer-events-none" />

        <div className="max-w-5xl mx-auto text-center space-y-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-emerald-500/30 text-emerald-400 text-xs font-semibold shadow-lg shadow-emerald-500/10">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Problem Statement O3 — Trustworthy & Verifiable AI</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-[1.1]">
            Find the Best Business Location.{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-cyan-400 to-indigo-400">
              Prove Every Single Claim.
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Shop owners usually pick locations by gut feel or hallucinatory AI advice.
            Disha scores urban zones with a deterministic 9-signal engine and forces the AI
            to cite proof for every word it speaks.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              href="/explore?city=blr&category=cafe&tier=medium"
              className="px-7 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-bold text-sm flex items-center gap-2 shadow-xl shadow-emerald-500/25 transition-all transform hover:-translate-y-0.5"
            >
              <span>Launch Bengaluru Demo</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/trust"
              className="px-7 py-3.5 rounded-xl glass-panel hover:bg-slate-800 text-slate-200 font-semibold text-sm flex items-center gap-2 border border-slate-700/80 transition-colors"
            >
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>Inspect Verification Pipeline</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Stats Bar */}
      <section className="border-y border-slate-800/80 bg-slate-900/40 py-6 px-4">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-1">
            <div className="text-2xl sm:text-3xl font-black text-emerald-400">0</div>
            <div className="text-xs text-slate-400">Leaked Unsupported Claims</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl sm:text-3xl font-black text-cyan-400">100%</div>
            <div className="text-xs text-slate-400">Speculative Trap Refusal Rate</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl sm:text-3xl font-black text-indigo-400">9 Signals</div>
            <div className="text-xs text-slate-400">Deterministic Relative Scoring</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl sm:text-3xl font-black text-white">417 Cells</div>
            <div className="text-xs text-slate-400">H3 Spatial Index (Bengaluru)</div>
          </div>
        </div>
      </section>

      {/* The 3 Core Pillars */}
      <section className="py-20 px-4 sm:px-8 max-w-6xl mx-auto space-y-12">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Why Disha AI is Truly Trustworthy
          </h2>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">
            Built from first principles to eradicate generative hallucinations in high-stakes retail decisions.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Pillar 1 */}
          <div className="p-6 rounded-2xl glass-panel border-slate-800 space-y-4 hover:border-emerald-500/40 transition-colors">
            <div className="w-11 h-11 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <BarChart3 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Deterministic 9-Signal Scoring</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Competition density, transit access, gap opportunity, footfall anchors, and daytime commercial activity
              are calculated with pure mathematical functions. Results are 100% reproducible.
            </p>
          </div>

          {/* Pillar 2 */}
          <div className="p-6 rounded-2xl glass-panel border-slate-800 space-y-4 hover:border-cyan-500/40 transition-colors">
            <div className="w-11 h-11 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">V1–V9 Claim Verifier</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Every sentence generated by the model must cite explicit evidence IDs from the computed bundle.
              Code-level rules verify numbers, ranks, and polarity before the user ever sees a word.
            </p>
          </div>

          {/* Pillar 3 */}
          <div className="p-6 rounded-2xl glass-panel border-slate-800 space-y-4 hover:border-indigo-500/40 transition-colors">
            <div className="w-11 h-11 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-white">Honest Provenance & Limits</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              We never fabricate real rent prices or made-up footfall figures. Rent is represented honestly as a
              team-assigned heuristic tier (1-5) and labelled accordingly.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800/80 py-8 px-4 text-center text-xs text-slate-500">
        <p>© 2026 Disha AI • Open-Source Location Intelligence under MIT License • Data: © OpenStreetMap contributors</p>
      </footer>
    </div>
  );
}
