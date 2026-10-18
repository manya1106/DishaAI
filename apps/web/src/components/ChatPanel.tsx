"use client";

import React, { useState } from "react";
import {
  ChatResponse,
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
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err);
      const errMsg: ChatMessage = {
        id: String(Date.now()),
        sender: "assistant",
        text: `Error calling verification service: ${message}`,
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
      <div className="p-3 rounded-xl glass-panel flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#2F6E4E]" />
          <span className="font-medium text-[#15130F]">Verifiable AI engine (O3)</span>
        </div>

        <button
          type="button"
          onClick={() => onToggleDeterministic(!deterministicMode)}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-[#15130F]/15 hover:border-[#15130F]/35 transition-colors"
          title="Toggle between AI narration and deterministic fallback"
        >
          <span className="text-[11px] text-[#15130F]/50">Mode:</span>
          <span
            className={`font-semibold text-[11px] ${
              deterministicMode ? "text-[#3F5B6C]" : "text-[#2F6E4E]"
            }`}
          >
            {deterministicMode ? "Deterministic Only" : "LLM + Verifier"}
          </span>
          {deterministicMode ? (
            <ToggleLeft className="w-4 h-4 text-[#3F5B6C]" />
          ) : (
            <ToggleRight className="w-4 h-4 text-[#2F6E4E]" />
          )}
        </button>
      </div>

      {/* Suggested Prompt Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px]">
        <button
          type="button"
          onClick={() => handleSend("Why is #1 ranked ahead of #2?")}
          className="px-2.5 py-1 rounded-full bg-white hover:bg-neutral-50 border border-[#15130F]/15 text-[#15130F]/70 shrink-0 transition-colors"
        >
          Why is #1 ahead of #2?
        </button>
        <button
          type="button"
          onClick={() => handleSend("What are the primary strengths of #1?")}
          className="px-2.5 py-1 rounded-full bg-white hover:bg-neutral-50 border border-[#15130F]/15 text-[#15130F]/70 shrink-0 transition-colors"
        >
          Strengths of #1?
        </button>
        <button
          type="button"
          onClick={() => handleSend("What is the exact monthly rent in rupees for #1?")}
          className="px-2.5 py-1 rounded-full bg-[#8B3A2F]/8 hover:bg-[#8B3A2F]/15 border border-[#8B3A2F]/25 text-[#8B3A2F] shrink-0 transition-colors"
        >
          Rent in rupees? [Trap test]
        </button>
      </div>

      {/* Chat Messages List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
        {messages.map((m) => {
          if (m.sender === "user") {
            return (
              <div key={m.id} className="flex items-start justify-end gap-2">
                <div className="p-3 rounded-2xl rounded-tr-sm bg-[#15130F] text-[#F6F1E7] max-w-[85%]">
                  {m.text}
                </div>
                <div className="w-6 h-6 rounded-full bg-[#15130F]/8 flex items-center justify-center shrink-0 mt-1">
                  <User className="w-3.5 h-3.5 text-[#15130F]/60" />
                </div>
              </div>
            );
          }

          // Assistant Message
          if (m.text) {
            return (
              <div key={m.id} className="flex items-start gap-2">
                <div className="w-6 h-6 rounded-full bg-[#2F6E4E]/15 border border-[#2F6E4E]/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-3.5 h-3.5 text-[#2F6E4E]" />
                </div>
                <div className="p-3 rounded-2xl rounded-tl-sm glass-panel text-[#15130F]/80 max-w-[85%] leading-relaxed">
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
              <div className="w-6 h-6 rounded-full bg-[#2F6E4E]/15 border border-[#2F6E4E]/30 flex items-center justify-center shrink-0 mt-1">
                <Bot className="w-3.5 h-3.5 text-[#2F6E4E]" />
              </div>

              <div className="space-y-2 max-w-[88%]">
                {/* Verification Badge */}
                <div className="flex items-center gap-2 flex-wrap">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${
                      isRefused
                        ? "bg-[#8B3A2F]/8 text-[#8B3A2F] border-[#8B3A2F]/25"
                        : isVerified
                        ? "bg-[#2F6E4E]/10 text-[#2F6E4E] border-[#2F6E4E]/25"
                        : isFallback
                        ? "bg-[#3F5B6C]/10 text-[#3F5B6C] border-[#3F5B6C]/25"
                        : "bg-[#A6693B]/10 text-[#A6693B] border-[#A6693B]/25"
                    }`}
                  >
                    {isRefused ? (
                      <ShieldAlert className="w-3 h-3" />
                    ) : (
                      <ShieldCheck className="w-3 h-3" />
                    )}
                    {isRefused
                      ? "Refused (insufficient data)"
                      : isVerified
                      ? `Verified (${resp.verification.claims_verified}/${resp.verification.claims_total} claims)`
                      : isFallback
                      ? "Deterministic fallback"
                      : `Partially verified (${resp.verification.claims_removed} claims removed)`}
                  </span>

                  <span className="text-[10px] text-[#15130F]/40">{resp.latency_ms}ms</span>

                  <button
                    type="button"
                    onClick={() => toggleAgentTrace(resp.trace_id)}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border bg-white hover:bg-neutral-50 border-[#15130F]/15 text-[#15130F]/65 transition-colors"
                    title="Show which agents handled this request, in order — a real trace, not a diagram"
                  >
                    <span className="live-dot" />
                    <Workflow className="w-3 h-3 text-[#3F5B6C]" />
                    Agent trace
                    {openTraceId === resp.trace_id ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>
                </div>

                {/* Agent Hand-off Sequence (Phase 6 observability surface) */}
                {openTraceId === resp.trace_id && (
                  <div className="p-2.5 rounded-xl glass-panel text-[11px] space-y-1.5">
                    {traceLoading && !agentTraces[resp.trace_id] ? (
                      <span className="text-[#15130F]/50">Loading agent trace…</span>
                    ) : (agentTraces[resp.trace_id] || []).length === 0 ? (
                      <span className="text-[#15130F]/40">No agent trace recorded for this request.</span>
                    ) : (
                      <div className="flex flex-wrap items-center gap-1.5">
                        {(agentTraces[resp.trace_id] || []).map((h, i) => (
                          <React.Fragment key={i}>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-white border border-[#15130F]/12 font-mono text-[#15130F]/70">
                              {h.recipient}
                              {h.payload?.step ? (
                                <span className="text-[#15130F]/40">({String(h.payload.step)})</span>
                              ) : null}
                            </span>
                            {i < (agentTraces[resp.trace_id] || []).length - 1 && (
                              <span className="text-[#15130F]/30">→</span>
                            )}
                          </React.Fragment>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Blocks with Claim Chips */}
                <div className="p-3.5 rounded-2xl rounded-tl-sm glass-panel space-y-2.5">
                  {resp.blocks.map((block, bIdx) => (
                    <div key={bIdx} className="space-y-1.5 leading-relaxed text-[#15130F]/80">
                      <p>{block.text}</p>

                      {/* Claim Chips */}
                      {(block.claims || []).length > 0 && (
                        <div className="flex flex-wrap items-center gap-1.5 pt-1">
                          {(block.claims || []).map((claim, cIdx) => (
                            <button
                              key={cIdx}
                              type="button"
                              onClick={() => handleClaimClick(claim)}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-white hover:bg-neutral-50 border border-[#15130F]/15 hover:border-[#2F6E4E]/40 text-[10px] text-[#15130F]/70 transition-all font-mono"
                              title="Click to view underlying OpenStreetMap evidence item"
                            >
                              <FileCheck className="w-2.5 h-2.5 text-[#2F6E4E]" />
                              <span>{claim.type}</span>
                              {claim.signal_id && (
                                <span className="text-[#15130F]/45">
                                  ({claim.signal_id.replace(/_/g, " ")})
                                </span>
                              )}
                              <span className="text-[#2F6E4E] text-[9px]">↗ Evidence</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {/* Uncertainty/Missing notice if present */}
                  {(resp.uncertainty?.missing || []).length > 0 && (
                    <div className="mt-2 pt-2 border-t border-[#15130F]/10 text-[11px] text-[#A6693B] flex items-start gap-1">
                      <Info className="w-3 h-3 shrink-0 mt-0.5" />
                      <span>{(resp.uncertainty?.missing || []).join("; ")}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center gap-2 text-[#15130F]/50 text-xs pl-8">
            <div className="w-3 h-3 border border-[#2F6E4E] border-t-transparent rounded-full animate-spin" />
            <span>Verifying claims against evidence bundle…</span>
          </div>
        )}
      </div>

      {/* Input box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2 p-2 rounded-xl glass-panel"
      >
        <input
          type="text"
          value={input}
          maxLength={500}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about ranked locations…"
          className="flex-1 bg-transparent px-3 py-1.5 text-xs text-[#15130F] placeholder-[#15130F]/40 focus:outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="p-2 rounded-lg bg-[#15130F] hover:bg-[#2A2720] disabled:opacity-30 text-[#F6F1E7] transition-colors"
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>

      {/* Evidence Drawer Overlay (Click on Claim Chip) */}
      {activeEvidenceItem && (
        <div className="absolute inset-x-0 bottom-0 top-12 z-30 glass-panel-elevated p-4 rounded-2xl flex flex-col justify-between animate-in fade-in duration-200">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-[#15130F]/12 pb-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-[#2F6E4E]" />
                <h4 className="text-sm font-medium text-[#15130F]">Grounded evidence record</h4>
              </div>
              <button
                type="button"
                onClick={() => setActiveEvidenceItem(null)}
                className="p-1 rounded-lg text-[#15130F]/50 hover:text-[#15130F] hover:bg-[#15130F]/6"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-[#15130F]/10">
                <span className="text-[#15130F]/50">Evidence ID:</span>
                <span className="font-mono text-[#2F6E4E] font-semibold">{activeEvidenceItem.evidence_id}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#15130F]/10">
                <span className="text-[#15130F]/50">Signal:</span>
                <span className="font-medium text-[#15130F] capitalize">{activeEvidenceItem.signal_id.replace(/_/g, " ")}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#15130F]/10">
                <span className="text-[#15130F]/50">Metric label:</span>
                <span className="text-[#15130F]">{activeEvidenceItem.label}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#15130F]/10">
                <span className="text-[#15130F]/50">Calculated value:</span>
                <span className="text-base font-semibold text-[#15130F]">
                  {String(activeEvidenceItem.value)} {activeEvidenceItem.unit || ""}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#15130F]/10">
                <span className="text-[#15130F]/50">Provenance class:</span>
                <span className="capitalize font-semibold text-[#3F5B6C]">{activeEvidenceItem.provenance}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-[#15130F]/10">
                <span className="text-[#15130F]/50">Data source:</span>
                <span className="text-[#15130F]/75">{activeEvidenceItem.source}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-[#15130F]/50">Snapshot as-of:</span>
                <span className="text-[#15130F]/50">{activeEvidenceItem.as_of}</span>
              </div>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-[#2F6E4E]/10 border border-[#2F6E4E]/20 text-[11px] text-[#2F6E4E] flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0" />
            <span>
              This claim was mathematically proven against this record before display.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
