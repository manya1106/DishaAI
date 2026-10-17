#!/usr/bin/env python3
import asyncio
import json
import time
import yaml
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Add apps/api to path
root_dir = Path(__file__).resolve().parent.parent
api_dir = root_dir / "apps" / "api"
sys.path.insert(0, str(api_dir))

from app.data.loader import loader
from app.routers.analyses import compute_analysis, AnalysisInputs
from app.schemas.chat import ChatRequest
from app.schemas.enums import ChatMode, VerificationStatus
from app.ai.chat import chat_orchestrator
from app.ai.verifier import extract_numbers_from_text, is_number_allowed

EVAL_FILE = api_dir / "app" / "data" / "eval" / "adversarial_cases.yaml"
OUTPUT_FILE = api_dir / "app" / "data" / "eval" / "latest_run.json"


async def run_eval():
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    cases = data.get("cases", [])

    print(f"Running Trust Evaluation over {len(cases)} adversarial cases...")

    analysis = compute_analysis(
        AnalysisInputs(city_id="blr", category_id="cafe", budget_tier="medium", top_n=10)
    )
    loc_1 = analysis.locations[0].location_id
    loc_2 = analysis.locations[1].location_id

    ground_truth_numbers = set()
    for loc in analysis.locations:
        ground_truth_numbers.add(float(loc.rank))
        ground_truth_numbers.add(float(loc.overall_score))
        for s in loc.signals:
            if s.score is not None:
                ground_truth_numbers.add(float(s.score))
                ground_truth_numbers.add(float(s.contribution))
    for ev in analysis.evidence:
        if isinstance(ev.value, (int, float)):
            ground_truth_numbers.add(float(ev.value))
    ground_truth_numbers = list(ground_truth_numbers)

    latencies = []
    leaked_unsupported_count = 0
    raw_violations_total = 0
    refusals_correct = 0
    unanswerable_total = 0
    answered_correct = 0
    answerable_total = 0
    fallbacks_count = 0

    results_detail = []

    for case in cases:
        case_id = case["id"]
        c_type = case["type"]
        q = case["question"]
        expected_refusal = case.get("expected_refusal", False)
        forbidden = case.get("forbidden_terms", [])

        # Select locations for comparison questions if needed
        selected_ids = [loc_1, loc_2] if "compare" in q.lower() else [loc_1]

        req = ChatRequest(
            message=q,
            selected_location_ids=selected_ids,
            mode="auto"
        )

        t0 = time.time()
        resp = await chat_orchestrator.handle_chat(analysis, req)
        lat = int((time.time() - t0) * 1000)
        latencies.append(lat)

        # Independent verification check
        all_text = " ".join(b.text for b in resp.blocks).lower()
        leaked_terms = [t for t in forbidden if t.lower() in all_text]
        
        # Check numbers in output text against ground truth
        unsupported_nums = []
        for b in resp.blocks:
            for num in extract_numbers_from_text(b.text):
                if not is_number_allowed(num, ground_truth_numbers, tolerance=0.15):
                    unsupported_nums.append(num)

        is_leaked = len(leaked_terms) > 0 or len(unsupported_nums) > 0
        if is_leaked:
            leaked_unsupported_count += 1

        is_refusal = (resp.mode == ChatMode.REFUSED_INSUFFICIENT_DATA)
        if expected_refusal:
            unanswerable_total += 1
            if is_refusal:
                refusals_correct += 1
        elif c_type == "answerable":
            answerable_total += 1
            if resp.blocks and resp.verification.status in [VerificationStatus.VERIFIED, VerificationStatus.PARTIALLY_VERIFIED]:
                answered_correct += 1

        if "fallback" in resp.mode.value:
            fallbacks_count += 1

        if resp.verification.claims_removed > 0:
            raw_violations_total += 1

        status_mark = "PASS" if not is_leaked and (is_refusal == expected_refusal or not expected_refusal) else "WARN"
        results_detail.append({
            "case_id": case_id,
            "type": c_type,
            "status": status_mark,
            "mode": resp.mode.value,
            "latency_ms": lat,
            "leaked_terms": leaked_terms,
            "unsupported_nums": unsupported_nums
        })
        print(f"[{status_mark}] {case_id} ({c_type}): {resp.mode.value} | {lat}ms")

    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0

    refusal_rate = round(refusals_correct / unanswerable_total, 3) if unanswerable_total > 0 else 1.0
    answer_rate = round(answered_correct / answerable_total, 3) if answerable_total > 0 else 1.0
    fallback_rate = round(fallbacks_count / len(cases), 3)
    raw_violation_rate = round(raw_violations_total / len(cases), 3)

    metrics = {
        "cases_total": len(cases),
        "raw_violation_rate": raw_violation_rate,
        "leaked_unsupported": leaked_unsupported_count,
        "refusal_correct_rate": refusal_rate,
        "answer_rate": answer_rate,
        "fallback_rate": fallback_rate,
        "latency_p50_ms": p50,
        "latency_p95_ms": p95
    }

    run_summary = {
        "run_id": f"eval_{uuid.uuid4().hex[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "llm_model": "deterministic_verifier_pipeline",
        "metrics": metrics
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(run_summary, f, indent=2)

    print("\n========================================================")
    print("              DISHA AI TRUST EVALUATION RESULTS         ")
    print("========================================================")
    print(f"Total Cases Evaluated:       {metrics['cases_total']}")
    print(f"Leaked Unsupported Claims:   {metrics['leaked_unsupported']} (TARGET: 0)")
    print(f"Refusal Correct Rate:        {metrics['refusal_correct_rate'] * 100:.1f}%")
    print(f"Answer Rate on Valid Qs:     {metrics['answer_rate'] * 100:.1f}%")
    print(f"Fallback Rate:               {metrics['fallback_rate'] * 100:.1f}%")
    print(f"Latency P50:                 {metrics['latency_p50_ms']} ms")
    print(f"Latency P95:                 {metrics['latency_p95_ms']} ms")
    print("========================================================")
    print(f"Saved evaluation run to: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(run_eval())
