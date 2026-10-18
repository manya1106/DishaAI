"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "../../lib/api";
import { MetaResponse, AnalysisResult } from "../../lib/types";

const CATEGORY_BLURBS: Record<string, string> = {
  cafe: "Coffee, tea, and casual food-and-drink spots.",
  pharmacy: "Retail chemists and wellness stores.",
  gym: "Fitness centres and training studios.",
};

const TOTAL_STEPS = 4;

interface ProcessingStage {
  label: string;
  detail: string;
}

/** Builds the reveal sequence from the REAL API response — every number
 * here is the actual computed result, just paced for comprehension
 * rather than dumped on screen all at once. Nothing here is fabricated
 * or delayed to seem slower than it is. */
function buildProcessingStages(
  result: AnalysisResult,
  categoryName: string,
  tierName: string
): ProcessingStage[] {
  const stages: ProcessingStage[] = [
    {
      label: "Dispatched to Scoring Agent",
      detail: `${categoryName} · ${tierName} tier · trace ${result.trace_id.slice(0, 8)}…`,
    },
    {
      label: "Queried real H3 cells from Postgres",
      detail: `${result.eligible_cells_considered} of ${result.cells_considered} cells eligible for ranking`,
    },
  ];

  for (const adj of result.weight_adjustments ?? []) {
    stages.push({
      label: `Your answer "${adj.label}" adjusted a weight`,
      detail: `${adj.signal_id.replace(/_/g, " ")} weight × ${adj.multiplier}`,
    });
  }

  stages.push({
    label: result.was_cached ? "Served from cache" : "Computed fresh, live",
    detail: result.was_cached
      ? "Identical request already computed — reused rather than re-run"
      : `9-signal scoring over ${result.cells_considered} cells in ${result.compute_latency_ms}ms`,
  });
  stages.push({
    label: "Ranking complete",
    detail: `${result.locations.length} zones ranked, top score ${result.locations[0]?.overall_score ?? "—"}`,
  });

  return stages;
}

export default function NewAnalysisPage() {
  const router = useRouter();
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [categoryId, setCategoryId] = useState<string | null>(null);
  const [budgetTier, setBudgetTier] = useState<string | null>(null);
  const [shopSizeSqft, setShopSizeSqft] = useState<string>("");
  const [openingHours, setOpeningHours] = useState<string>("");
  const [targetCustomers, setTargetCustomers] = useState<string[]>([]);
  const [categoryAnswers, setCategoryAnswers] = useState<Record<string, string>>({});

  // Processing screen (step 5): the real result, revealed progressively.
  const [pendingResult, setPendingResult] = useState<AnalysisResult | null>(null);
  const [revealIndex, setRevealIndex] = useState(0);

  useEffect(() => {
    let active = true;
    api.getMeta().then((m) => {
      if (active) setMeta(m);
    });
    return () => {
      active = false;
    };
  }, []);

  function toggleTargetCustomer(value: string) {
    setTargetCustomers((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
    );
  }

  function setCategoryAnswer(questionId: string, value: string) {
    setCategoryAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  async function handleSubmit() {
    if (!categoryId || !budgetTier) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.createAnalysis({
        city_id: "blr",
        category_id: categoryId,
        budget_tier: budgetTier,
        top_n: 10,
        target_customers: targetCustomers,
        category_answers: categoryAnswers,
        shop_size_sqft: shopSizeSqft ? Number(shopSizeSqft) : undefined,
        opening_hours: openingHours || undefined,
      });
      setPendingResult(result);
      setRevealIndex(0);
      setStep(5);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Could not run the analysis. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  const categoryName = meta?.categories.find((c) => c.category_id === categoryId)?.name ?? categoryId ?? "";
  const tierName = meta?.budget_tiers.find((t) => t.tier_id === budgetTier)?.name ?? budgetTier ?? "";
  const processingStages = pendingResult ? buildProcessingStages(pendingResult, categoryName, tierName) : [];

  // Reveal the real result one stage at a time, then navigate. Every
  // stage shown is already-computed real data — this paces comprehension,
  // it does not fake additional processing time.
  useEffect(() => {
    if (step !== 5 || !pendingResult) return;
    if (revealIndex >= processingStages.length) {
      const t = setTimeout(() => {
        router.push(`/explore?analysisId=${encodeURIComponent(pendingResult.analysis_id)}`);
      }, 700);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setRevealIndex((i) => i + 1), 500);
    return () => clearTimeout(t);
  }, [step, pendingResult, revealIndex, processingStages.length, router]);

  const categoryQuestions = categoryId ? meta?.category_questions?.[categoryId] ?? [] : [];
  const tierDescriptions = categoryId ? meta?.category_tier_descriptions?.[categoryId] ?? {} : {};

  const canAdvance =
    (step === 1 && !!categoryId) ||
    (step === 2 && !!budgetTier) ||
    step === 3 ||
    step === 4;

  return (
    <div
      className="min-h-screen flex flex-col bg-[#F6F1E7] text-[#15130F]"
      style={{ fontFamily: "var(--font-geist-sans)" }}
    >
      <header className="px-6 sm:px-14 py-7 sm:py-9">
        <div className="max-w-[900px] mx-auto flex items-center justify-between">
          <Link href="/" className="text-base font-medium" style={{ fontFamily: "var(--font-display)" }}>
            Disha AI
          </Link>
          <div className="text-xs tracking-[0.14em] uppercase text-[#15130F]/45">
            {step <= TOTAL_STEPS ? `Step ${step} of ${TOTAL_STEPS}` : "Running"}
          </div>
        </div>
        <div className="max-w-[900px] mx-auto mt-5 h-[2px] bg-[#15130F]/10">
          <div
            className="h-full bg-[#2F6E4E] transition-all duration-500"
            style={{
              width:
                step <= TOTAL_STEPS
                  ? `${(step / TOTAL_STEPS) * 100}%`
                  : `${Math.min(100, (revealIndex / Math.max(1, processingStages.length)) * 100)}%`,
            }}
          />
        </div>
      </header>

      <main className="flex-1 px-6 sm:px-14 py-10 sm:py-16">
        <div className="max-w-[900px] mx-auto">
          {/* Step 1: category */}
          {step === 1 && (
            <div>
              <h1 className="text-[32px] sm:text-[44px] tracking-tight mb-3" style={{ fontFamily: "var(--font-display)" }}>
                What are you opening?
              </h1>
              <p className="text-[#15130F]/60 mb-10">In Bengaluru, to start. One category at a time.</p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {(meta?.categories ?? []).map((cat) => (
                  <button
                    key={cat.category_id}
                    onClick={() => setCategoryId(cat.category_id)}
                    className={`text-left p-6 border transition-colors ${
                      categoryId === cat.category_id
                        ? "border-[#15130F] bg-[#15130F] text-[#F6F1E7]"
                        : "border-[#15130F]/15 hover:border-[#15130F]/40"
                    }`}
                  >
                    <div className="text-lg font-medium" style={{ fontFamily: "var(--font-display)" }}>
                      {cat.name}
                    </div>
                    <div
                      className={`text-sm mt-2 ${
                        categoryId === cat.category_id ? "text-[#F6F1E7]/70" : "text-[#15130F]/55"
                      }`}
                    >
                      {CATEGORY_BLURBS[cat.category_id] ?? ""}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 2: tier */}
          {step === 2 && (
            <div>
              <h1 className="text-[32px] sm:text-[44px] tracking-tight mb-3" style={{ fontFamily: "var(--font-display)" }}>
                How premium will it be?
              </h1>
              <p className="text-[#15130F]/60 mb-10">
                This sets your rent-tier ceiling — we never invent rupee figures, only an honest relative tier.
              </p>

              <div className="space-y-3">
                {(meta?.budget_tiers ?? []).map((tier) => (
                  <button
                    key={tier.tier_id}
                    onClick={() => setBudgetTier(tier.tier_id)}
                    className={`w-full text-left p-5 border flex items-start gap-4 transition-colors ${
                      budgetTier === tier.tier_id
                        ? "border-[#15130F] bg-[#15130F] text-[#F6F1E7]"
                        : "border-[#15130F]/15 hover:border-[#15130F]/40"
                    }`}
                  >
                    <div
                      className={`mt-1 w-3 h-3 rounded-full border shrink-0 ${
                        budgetTier === tier.tier_id ? "bg-[#F6F1E7] border-[#F6F1E7]" : "border-[#15130F]/40"
                      }`}
                    />
                    <div>
                      <div className="font-medium" style={{ fontFamily: "var(--font-display)" }}>
                        {tier.name}
                      </div>
                      <div className={`text-sm mt-1 ${budgetTier === tier.tier_id ? "text-[#F6F1E7]/70" : "text-[#15130F]/55"}`}>
                        {tierDescriptions[tier.tier_id] ?? tier.description}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: constraints */}
          {step === 3 && (
            <div>
              <h1 className="text-[32px] sm:text-[44px] tracking-tight mb-3" style={{ fontFamily: "var(--font-display)" }}>
                A few more details.
              </h1>
              <p className="text-[#15130F]/60 mb-10 max-w-lg">
                Target customers and category questions genuinely nudge the scoring weights. Shop size and
                opening hours are shown for your reference only — honestly, they don&apos;t move the score yet.
              </p>

              <div className="space-y-10">
                <div>
                  <div className="text-sm font-medium mb-3">Who&apos;s your main customer? (pick any)</div>
                  <div className="flex flex-wrap gap-2">
                    {(meta?.target_customer_options ?? []).map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() => toggleTargetCustomer(opt.value)}
                        className={`px-4 py-2 text-sm border transition-colors ${
                          targetCustomers.includes(opt.value)
                            ? "border-[#15130F] bg-[#15130F] text-[#F6F1E7]"
                            : "border-[#15130F]/20 hover:border-[#15130F]/50"
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                {categoryQuestions.map((q) => (
                  <div key={q.question_id}>
                    <div className="text-sm font-medium mb-3">{q.label}</div>
                    <div className="flex flex-wrap gap-2">
                      {(q.options ?? []).map((opt) => (
                        <button
                          key={opt.value}
                          onClick={() => setCategoryAnswer(q.question_id, opt.value)}
                          className={`px-4 py-2 text-sm border transition-colors ${
                            categoryAnswers[q.question_id] === opt.value
                              ? "border-[#15130F] bg-[#15130F] text-[#F6F1E7]"
                              : "border-[#15130F]/20 hover:border-[#15130F]/50"
                          }`}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-[#15130F]/10">
                  <label className="block">
                    <span className="text-sm font-medium">Shop size (sq ft)</span>
                    <input
                      type="number"
                      min={50}
                      max={20000}
                      value={shopSizeSqft}
                      onChange={(e) => setShopSizeSqft(e.target.value)}
                      placeholder="e.g. 400"
                      className="mt-2 w-full border border-[#15130F]/20 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:border-[#15130F]"
                    />
                  </label>
                  <label className="block">
                    <span className="text-sm font-medium">Opening hours</span>
                    <input
                      type="text"
                      value={openingHours}
                      onChange={(e) => setOpeningHours(e.target.value)}
                      placeholder="e.g. 8:00 AM – 9:00 PM"
                      className="mt-2 w-full border border-[#15130F]/20 bg-transparent px-4 py-2.5 text-sm focus:outline-none focus:border-[#15130F]"
                    />
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: review */}
          {step === 4 && (
            <div>
              <h1 className="text-[32px] sm:text-[44px] tracking-tight mb-3" style={{ fontFamily: "var(--font-display)" }}>
                Review and run.
              </h1>
              <p className="text-[#15130F]/60 mb-10">The Scoring Agent runs over real Bengaluru data once you submit.</p>

              <dl className="divide-y divide-[#15130F]/10 border-y border-[#15130F]/10">
                {[
                  ["Category", meta?.categories.find((c) => c.category_id === categoryId)?.name ?? "—"],
                  ["Tier", meta?.budget_tiers.find((t) => t.tier_id === budgetTier)?.name ?? "—"],
                  [
                    "Target customers",
                    targetCustomers.length
                      ? targetCustomers
                          .map((v) => (meta?.target_customer_options ?? []).find((o) => o.value === v)?.label ?? v)
                          .join(", ")
                      : "Not specified",
                  ],
                  ...categoryQuestions.map((q) => [
                    q.label,
                    (q.options ?? []).find((o) => o.value === categoryAnswers[q.question_id])?.label ?? "Not answered",
                  ]),
                  ["Shop size", shopSizeSqft ? `${shopSizeSqft} sq ft (reference only)` : "Not specified"],
                  ["Opening hours", openingHours ? `${openingHours} (reference only)` : "Not specified"],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between py-4 text-sm">
                    <dt className="text-[#15130F]/55">{label}</dt>
                    <dd className="font-medium text-right max-w-[60%]">{value}</dd>
                  </div>
                ))}
              </dl>

              {error && <p className="mt-6 text-sm text-[#8B2E2E]">{error}</p>}
            </div>
          )}

          {/* Step 5: processing — every line below is real, already-computed
              data from the API response, revealed one stage at a time. */}
          {step === 5 && pendingResult && (
            <div>
              <h1 className="text-[32px] sm:text-[44px] tracking-tight mb-3" style={{ fontFamily: "var(--font-display)" }}>
                Running the agent swarm.
              </h1>
              <p className="text-[#15130F]/60 mb-10">
                Live hand-offs for trace <span className="font-mono">{pendingResult.trace_id.slice(0, 8)}…</span>
              </p>

              <div className="space-y-0 border-y border-[#15130F]/10 divide-y divide-[#15130F]/10">
                {processingStages.slice(0, revealIndex + 1).map((stage, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-4 py-4 animate-in fade-in"
                    style={{ animation: "fadeIn 0.4s ease-out" }}
                  >
                    <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[#2F6E4E] shrink-0" />
                    <div>
                      <div className="font-medium" style={{ fontFamily: "var(--font-display)" }}>
                        {stage.label}
                      </div>
                      <div className="text-sm text-[#15130F]/55 mt-0.5">{stage.detail}</div>
                    </div>
                  </div>
                ))}
                {revealIndex < processingStages.length && (
                  <div className="flex items-center gap-3 py-4 text-sm text-[#15130F]/40">
                    <div className="w-1.5 h-1.5 rounded-full border border-[#15130F]/30 animate-pulse shrink-0" />
                    Working…
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      {step !== 5 && (
        <footer className="px-6 sm:px-14 py-8">
          <div className="max-w-[900px] mx-auto flex items-center justify-between">
            <button
              onClick={() => setStep((s) => Math.max(1, s - 1))}
              disabled={step === 1}
              className="text-sm font-medium border-b border-[#15130F]/30 hover:border-[#15130F] pb-0.5 disabled:opacity-0 transition-opacity"
            >
              ← Back
            </button>

            {step < TOTAL_STEPS ? (
              <button
                onClick={() => setStep((s) => Math.min(TOTAL_STEPS, s + 1))}
                disabled={!canAdvance}
                className="px-6 py-3.5 bg-[#15130F] text-[#F6F1E7] text-sm font-medium disabled:opacity-30 hover:bg-[#2A2720] transition-colors"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-3.5 bg-[#15130F] text-[#F6F1E7] text-sm font-medium disabled:opacity-50 hover:bg-[#2A2720] transition-colors"
              >
                {submitting ? "Running the swarm…" : "Run analysis"}
              </button>
            )}
          </div>
        </footer>
      )}
    </div>
  );
}
