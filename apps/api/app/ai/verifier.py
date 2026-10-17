import re

from ..schemas.chat import Block, Claim, LLMOutput
from ..schemas.enums import ClaimPolarity, ClaimType, VerificationStatus
from .evidence import EvidenceBundle

FORBIDDEN_KEYWORDS = [
    "revenue", "profit", "monthly rent in rupees", "₹", "rs.", "inr", "lakhs", "crores", "footfall count"
]

NUMBER_PATTERN = re.compile(r"#?(\d+(?:\.\d+)?)%?")


def extract_numbers_from_text(text: str) -> list[float]:
    matches = NUMBER_PATTERN.findall(text)
    numbers = []
    for m in matches:
        try:
            numbers.append(float(m))
        except ValueError:
            continue
    return numbers


def is_number_allowed(num: float, allowed_numbers: list[float], tolerance: float = 0.15) -> bool:
    for allowed in allowed_numbers:
        # Check absolute or relative tolerance
        if abs(num - allowed) <= tolerance:
            return True
        if allowed != 0 and abs((num - allowed) / allowed) <= tolerance:
            return True
    return False


class Verifier:
    def verify(
        self,
        llm_output: LLMOutput,
        bundle: EvidenceBundle
    ) -> tuple[list[Block], list[str], VerificationStatus]:
        violations: list[str] = []
        verified_blocks: list[Block] = []

        initial_block_count = len(llm_output.blocks)
        if initial_block_count == 0:
            return [], ["V1_EMPTY_OUTPUT: LLM output contained zero blocks"], VerificationStatus.REJECTED_FALLBACK

        loc_lookup = {l.location_id: l for l in bundle.selected_locations}

        for block_idx, block in enumerate(llm_output.blocks):
            block_violations: list[str] = []
            text = block.text.strip()
            numbers_in_text = extract_numbers_from_text(text)

            # Rule V8: Sentence contains number but no claim carries it
            if numbers_in_text and not block.claims:
                block_violations.append(f"V8_UNCITED_NUMBERS: Block contains numbers {numbers_in_text} with no claims")

            # Rule V7: Forbidden topics (unsupported currency/revenue/profit)
            text_lower = text.lower()
            for kw in FORBIDDEN_KEYWORDS:
                if kw in text_lower:
                    # If currency or revenue mentioned, check if it was explicitly substantiated
                    block_violations.append(f"V7_FORBIDDEN_TOPIC: Block mentions forbidden speculative term '{kw}'")
                    break

            # Rule V4: Check location names mentioned in text
            # Check if text mentions words like "Zone in <X>" where X is completely unknown
            # Basic entity verification against allowed_names
            # If text has "#N" check if N is an allowed rank
            for m in re.finditer(r"#(\d+)", text):
                rank_num = float(m.group(1))
                if rank_num not in bundle.allowed_numbers:
                    block_violations.append(f"V4_UNKNOWN_RANK: Text mentions rank #{int(rank_num)} not in analysis context")

            verified_claims: list[Claim] = []

            for claim_idx, claim in enumerate(block.claims):
                # Rule V2: Every claim must cite evidence IDs that exist in bundle
                for ev_id in claim.evidence_ids:
                    if ev_id not in bundle.evidence_lookup:
                        block_violations.append(f"V2_UNKNOWN_EVIDENCE_ID: Claim cites unknown evidence ID '{ev_id}'")

                # Rule V3: Numeric consistency check
                for num in claim.numbers:
                    if not is_number_allowed(num, bundle.allowed_numbers):
                        block_violations.append(f"V3_UNSUPPORTED_NUMBER: Claim number {num} does not match any evidence")

                # Check numbers in text match claim numbers or allowed numbers
                for text_num in numbers_in_text:
                    if not is_number_allowed(text_num, bundle.allowed_numbers):
                        block_violations.append(f"V3_TEXT_NUMBER_MISMATCH: Number {text_num} in text not grounded in evidence")

                # Rule V5: Rank and comparison claims validity
                if claim.type == ClaimType.RANK:
                    for lid in claim.location_ids:
                        if lid in loc_lookup:
                            loc = loc_lookup[lid]
                            # If claim gives numbers, one of them must match loc.rank
                            if claim.numbers and float(loc.rank) not in claim.numbers:
                                block_violations.append(f"V5_INVALID_RANK: Claimed rank does not match actual rank {loc.rank}")

                if claim.type == ClaimType.COMPARISON and len(claim.location_ids) >= 2:
                    lid_a, lid_b = claim.location_ids[0], claim.location_ids[1]
                    if lid_a in loc_lookup and lid_b in loc_lookup:
                        loc_a = loc_lookup[lid_a]
                        loc_b = loc_lookup[lid_b]
                        if claim.signal_id:
                            sig_a = loc_a.signals.get(claim.signal_id, {})
                            sig_b = loc_b.signals.get(claim.signal_id, {})
                            score_a = sig_a.get("score")
                            score_b = sig_b.get("score")
                            if (
                                score_a is not None
                                and score_b is not None
                                and claim.polarity == ClaimPolarity.STRENGTH
                                and score_a < score_b
                            ):
                                block_violations.append(
                                    f"V5_CONTRADICTORY_COMPARISON: Claim states {loc_a.display_name} leads on {claim.signal_id}, but score is lower ({score_a} vs {score_b})"
                                )
                        else:
                            # Compare overall score
                            if claim.polarity == ClaimPolarity.STRENGTH and loc_a.overall_score < loc_b.overall_score:
                                block_violations.append(f"V5_CONTRADICTORY_OVERALL: Claim states {loc_a.display_name} leads, but overall score is lower")

                # Rule V6: Polarity consistency
                if claim.signal_id and claim.type in [ClaimType.FACT, ClaimType.SCORE]:
                    for lid in claim.location_ids:
                        if lid in loc_lookup:
                            loc = loc_lookup[lid]
                            sig = loc.signals.get(claim.signal_id, {})
                            sc = sig.get("score")
                            if sc is not None:
                                if claim.polarity == ClaimPolarity.STRENGTH and sc < 50.0:
                                    block_violations.append(f"V6_POLARITY_MISMATCH: Claimed strength on signal {claim.signal_id} with low score {sc}")
                                elif claim.polarity == ClaimPolarity.WEAKNESS and sc > 45.0:
                                    block_violations.append(f"V6_POLARITY_MISMATCH: Claimed weakness on signal {claim.signal_id} with high score {sc}")

                # If claim had no fatal violation, add to verified_claims
                verified_claims.append(Claim(
                    claim_id=f"c_{block_idx}_{claim_idx}",
                    type=claim.type,
                    location_ids=claim.location_ids,
                    signal_id=claim.signal_id,
                    polarity=claim.polarity,
                    evidence_ids=claim.evidence_ids,
                    numbers=claim.numbers,
                    verified=True
                ))

            if block_violations:
                violations.extend(block_violations)
            else:
                verified_blocks.append(Block(
                    text=text,
                    claims=verified_claims
                ))

        # Rule V9: If more than half the blocks were removed, trigger full fallback
        removed_count = initial_block_count - len(verified_blocks)
        if len(verified_blocks) == 0:
            return [], violations, VerificationStatus.REJECTED_FALLBACK

        if removed_count > (initial_block_count / 2):
            violations.append(f"V9_THRESHOLD_EXCEEDED: {removed_count}/{initial_block_count} blocks failed verification; discarding all")
            return [], violations, VerificationStatus.REJECTED_FALLBACK

        if removed_count > 0:
            return verified_blocks, violations, VerificationStatus.PARTIALLY_VERIFIED

        return verified_blocks, violations, VerificationStatus.VERIFIED


verifier = Verifier()
