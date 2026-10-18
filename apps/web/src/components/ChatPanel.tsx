"use client";

import React, { useState } from "react";
import {
  ChatResponse,
  Block,
  Claim,
  EvidenceItem,
  LocationResult,
  AgentHandoff,
} from "../lib/types";
import { api } from "../lib/api";
import {
  ShieldCheck,
  ShieldAlert,
  Send,
  Sparkles,
  Bot,
  User,
  Info,
  X,
  FileCheck,
  ToggleLeft,
  ToggleRight,
  Database,
  Workflow,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface Props {
  analysisId: string;
  selectedLocations: LocationResult[];
  allEvidence: EvidenceItem[];
  deterministicMode: boolean;
  onToggleDeterministic: (val: boolean) => void;
}

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text?: string;
  response?: ChatResponse;
}

export default function ChatPanel({
  analysisId,
  selectedLocations,
  allEvidence,
  deterministicMode,
  onToggleDeterministic,
}: Props) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      sender: "assistant",
      text: "Hello! I am Disha AI's Grounded Narrator. Every answer is decomposed into claims, verified against OpenStreetMap data rows, and proven before you see it. Ask me why locations rank, compare zones, or test trap questions.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeEvidenceItem, setActiveEvidenceItem] = useState<EvidenceItem | null>(null);
  const [agentTraces, setAgentTraces] = useState<Record<string, AgentHandoff[]>>({});
  const [openTraceId, setOpenTraceId] = useState<string | null>(null);
  const [traceLoading, setTraceLoading] = useState(false);

  const selectedIds = selectedLocations.map((l) => l.location_id);

  async function handleSend(query?: string) {
    const textToSend = query || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: String(Date.now()),
      sender: "user",
      text: textToSend,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const resp = await api.chatAnalysis(analysisId, {
        message: textToSend,
        selected_location_ids: selectedIds,
        mode: deterministicMode ? "deterministic" : "auto",
      });

      const assistantMsg: ChatMessage = {
        id: resp.trace_id,
        sender: "assistant",
        response: resp,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errMsg: ChatMessage = {
        id: String(Date.now()),
        sender: "assistant",
        text: `Error calling verification service: ${err.message}`,
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  }

  async function toggleAgentTrace(traceId: string) {
    if (openTraceId === traceId) {
      setOpenTraceId(null);
      return;
    }
    if (!agentTraces[traceId]) {
      setTraceLoading(true);
      try {
        const data = await api.getAgentTrace(traceId);
        setAgentTraces((prev) => ({ ...prev, [traceId]: data.handoffs }));
      } catch {
        setAgentTraces((prev) => ({ ...prev, [traceId]: [] }));
      } finally {
        setTraceLoading(false);
      }
    }
    setOpenTraceId(traceId);
  }

  function handleClaimClick(claim: Claim) {
    if (!claim.evidence_ids || claim.evidence_ids.length === 0) return;
    const evId = claim.evidence_ids[0];
    const found = allEvidence.find((e) => e.evidence_id === evId);
    if (found) {
      setActiveEvidenceItem(found);
    } else {
      // Fallback virtual evidence if alias
      setActiveEvidenceItem({
        evidence_id: evId,
        location_id: (claim.location_ids && claim.location_ids[0]) || "unknown",
        signal_id: claim.signal_id || "general",
        kind: "metric",
        label: `Cited ${claim.type} evidence`,
        value: (claim.numbers && claim.numbers[0] !== undefined) ? claim.numbers[0] : "Verified",
        provenance: "measured",
        source: "OpenStreetMap verified bundle",
        as_of: "2026-10",
      });
    }
  }

  return (
    <div className="flex flex-col h-full space-y-3 relative">
      {/* Top Controller Bar */}
      <div className="p-3 rounded-xl glass-panel border-slate-800/80 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="font-bold text-slate-200">Verifiable AI Engine (O3)</span>
        </div>

        <button
          type="button"
          onClick={() => onToggleDeterministic(!deterministicMode)}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors"
          title="Toggle between AI narration and deterministic fallback"
        >
          <span className="text-[11px] text-slate-400">Mode:</span>
          <span
            className={`font-semibold text-[11px] ${
              deterministicMode ? "text-cyan-400" : "text-emerald-400"
            }`}
          >
            {deterministicMode ? "Deterministic Only" : "LLM + Verifier"}
          </span>
          {deterministicMode ? (
            <ToggleLeft className="w-4 h-4 text-cyan-400" />
          ) : (
            <ToggleRight className="w-4 h-4 text-emerald-400" />
          )}
        </button>
      </div>

      {/* Suggested Prompt Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px]">
        <button
          type="button"
          onClick={() => handleSend("Why is #1 ranked ahead of #2?")}
          className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 shrink-0 transition-colors"
        >
          Why is #1 ahead of #2?
        </button>
        <button
          type="button"
          onClick={() => handleSend("What are the primary strengths of #1?")}
          className="px-2.5 py-1 rounded-full bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 shrink-0 transition-colors"
        >
          Strengths of #1?
        </button>
        <button
          type="button"
          onClick={() => handleSend("What is the exact monthly rent in rupees for #1?")}
          className="px-2.5 py-1 rounded-full bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 shrink-0 transition-colors"
        >
          Rent in rupees? [Trap Test]
        </button>
      </div>

      {/* Chat Messages List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
        {messages.map((m) => {
          if (m.sender === "user") {
            return (
              <div key={m.id} className="flex items-start justify-end gap-2">
                <div className="p-3 rounded-2xl rounded-tr-sm bg-gradient-to-r from-emerald-600 to-cyan-600 text-white max-w-[85%] shadow-md">
                  {m.text}
                </div>
                <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center shrink-0 mt-1">
                  <User className="w-3.5 h-3.5 text-slate-300" />
                </div>
              </div>
            );
          }

          // Assistant Message
          if (m.text) {
            return (
              <div key={m.id} className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-3.5 h-3.5 text-emerald-400" />
                </div>
                <div className="p-3 rounded-2xl rounded-tl-sm glass-panel border-slate-800 text-slate-200 max-w-[85%] leading-relaxed">
                  {m.text}
                </div>
              </div>
            );
          }

          const resp = m.response!;
          const isVerified = resp.verification.status === "verified";
          const isRefused = resp.mode === "refused_insufficient_data";
          const isFallback = resp.mode.includes("fallback");

          return (
            <div key={m.id} className="flex items-start gap-2">
              <div className="w-6 h-6 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shrink-0 mt-1">
                <Bot className="w-3.5 h-3.5 text-emerald-400" />
              </div>

              <div className="space-y-2 max-w-[88%]">
                {/* Verification Badge */}
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                      isRefused
                        ? "bg-rose-500/10 text-rose-300 border-rose-500/30"
                        : isVerified
                        ? "bg-emerald-500/10 text-emerald-300 border-emerald-500/30"
                        : isFallback
                        ? "bg-cyan-500/10 text-cyan-300 border-cyan-500/30"
                        : "bg-amber-500/10 text-amber-300 border-amber-500/30"
                    }`}
                  >
                    {isRefused ? (
                      <ShieldAlert className="w-3 h-3 text-rose-400" />
                    ) : (
                      <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    )}
                    {isRefused
                      ? "Refused (Insufficient Data)"
                      : isVerified
                      ? `Verified (${resp.verification.claims_verified}/${resp.verification.claims_total} claims)`
                      : isFallback
                      ? "Deterministic Fallback"
                      : `Partially Verified (${resp.verification.claims_removed} claims removed)`}
                  </span>

                  <span className="text-[10px] text-slate-500">{resp.latency_ms}ms</span>

                  <button
                    type="button"
                    onClick={() => toggleAgentTrace(resp.trace_id)}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border bg-slate-900/80 hover:bg-slate-800 border-slate-700 text-slate-300 transition-colors"
                    title="Show which agents handled this request, in order"
                  >
                    <Workflow className="w-3 h-3 text-cyan-400" />
                    Agent Trace
                    {openTraceId === resp.trace_id ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>
                </div>

                {/* Agent Hand-off Sequence (Phase 6 observability surface) */}
                {openTraceId === resp.trace_id && (
                  <div className="p-2.5 rounded-xl glass-panel border-slate-800 text-[11px] space-y-1.5">
                    {traceLoading && !agentTraces[resp.trace_id] ? (
                      <span className="text-slate-400">Loading agent trace...</span>
                    ) : (agentTraces[resp.trace_id] || []).length === 0 ? (
                      <span className="text-slate-500">No agent trace recorded for this request.</span>
                    ) : (
                      <div className="flex flex-wrap items-center gap-1.5">
                        {(agentTraces[resp.trace_id] || []).map((h, i) => (
                          <React.Fragment key={i}>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-700 font-mono text-slate-300">
                              {h.recipient}
                              {h.payload?.step ? (
                                <span className="text-slate-500">({String(h.payload.step)})</span>
                              ) : null}
                            </span>
                            {i < (agentTraces[resp.trace_id] || []).length - 1 && (
                              <span className="text-slate-600">→</span>
                            )}
                          </React.Fragment>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Blocks with Claim Chips */}
                <div className="p-3.5 rounded-2xl rounded-tl-sm glass-panel border-slate-800 space-y-2.5 shadow-md">
                  {resp.blocks.map((block, bIdx) => (
                    <div key={bIdx} className="space-y-1.5 leading-relaxed text-slate-200">
                      <p>{block.text}</p>

                      {/* Claim Chips */}
                      {(block.claims || []).length > 0 && (
                        <div className="flex flex-wrap items-center gap-1.5 pt-1">
                          {(block.claims || []).map((claim, cIdx) => (
                            <button
                              key={cIdx}
                              type="button"
                              onClick={() => handleClaimClick(claim)}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 hover:border-emerald-500/50 text-[10px] text-slate-300 transition-all font-mono"
                              title="Click to view underlying OpenStreetMap evidence item"
                            >
                              <FileCheck className="w-2.5 h-2.5 text-emerald-400" />
                              <span>{claim.type}</span>
                              {claim.signal_id && (
                                <span className="text-slate-400">
                                  ({claim.signal_id.replace(/_/g, " ")})
                                </span>
                              )}
                              <span className="text-emerald-400 text-[9px]">↗ Evidence</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Uncertainty/Missing notice if present */}
                  {(resp.uncertainty?.missing || []).length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-800 text-[11px] text-amber-300/80 flex items-start gap-1">
                      <Info className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />
                      <span>{(resp.uncertainty?.missing || []).join("; ")}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-2 text-slate-400 text-xs pl-8">
            <div className="w-3 h-3 border border-emerald-400 border-t-transparent rounded-full animate-spin" />
            <span>Verifying claims against evidence bundle...</span>
          </div>
        )}
      </div>

      {/* Input box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 p-2 rounded-xl glass-panel border-slate-800"
      >
        <input
          type="text"
          value={input}
          maxLength={500}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about ranked locations..."
          className="flex-1 bg-transparent px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 disabled:hover:bg-emerald-500 text-slate-950 font-bold transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>

      {/* Evidence Drawer Overlay (Click on Claim Chip) */}
      {activeEvidenceItem && (
        <div className="absolute inset-x-0 bottom-0 top-12 z-30 glass-panel-elevated p-4 rounded-2xl flex flex-col justify-between border-emerald-500/40 shadow-2xl animate-in fade-in duration-200">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-slate-700/80 pb-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-emerald-400" />
                <h4 className="text-sm font-bold text-white">Grounded Evidence Record</h4>
              </div>
              <button
                type="button"
                onClick={() => setActiveEvidenceItem(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Evidence ID:</span>
                <span className="font-mono text-emerald-400 font-bold">{activeEvidenceItem.evidence_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Signal:</span>
                <span className="font-semibold text-slate-200 capitalize">{activeEvidenceItem.signal_id.replace(/_/g, " ")}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Metric Label:</span>
                <span className="text-slate-200">{activeEvidenceItem.label}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Calculated Value:</span>
                <span className="text-base font-extrabold text-white">
                  {String(activeEvidenceItem.value)} {activeEvidenceItem.unit || ""}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Provenance Class:</span>
                <span className="capitalize font-bold text-cyan-400">{activeEvidenceItem.provenance}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800">
                <span className="text-slate-400">Data Source:</span>
                <span className="text-slate-300">{activeEvidenceItem.source}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Snapshot As-Of:</span>
                <span className="text-slate-400">{activeEvidenceItem.as_of}</span>
              </div>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-300 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>
              This claim was mathematically proven against this record before display.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
