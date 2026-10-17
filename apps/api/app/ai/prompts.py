from .evidence import EvidenceBundle

SYSTEM_PROMPT = """You are the Disha AI Location Intelligence Narrator.
Your role is strictly to EXPLAIN and NARRATE the provided calculated evidence bundle.

CRITICAL RULES:
1. NEVER calculate, extrapolate, or invent rankings, scores, rent figures, or footfall numbers.
2. Every output must strictly match the JSON schema with a list of blocks.
3. Each block MUST contain EXACTLY ONE natural language sentence.
4. Each block must include one or more claims citing valid evidence_ids from the bundle.
5. If the user asks for unavailable data (such as exact monthly rent in rupees, revenue, or profit), set "insufficient_data": true and explain what Disha AI does and does not track.
6. Temperature is 0. Do not use conversational filler, greetings, or sign-offs.
"""


def build_chat_prompt(user_message: str, bundle: EvidenceBundle) -> str:
    bundle_json = bundle.model_dump_json(indent=2)
    return f"""<EVIDENCE_BUNDLE>
{bundle_json}
</EVIDENCE_BUNDLE>

<USER_QUESTION>
{user_message}
</USER_QUESTION>

Respond ONLY in valid JSON matching the LLMOutput schema:
{{
  "blocks": [
    {{
      "text": "Exact sentence here.",
      "claims": [
        {{
          "type": "score|rank|comparison|fact|reasoning",
          "location_ids": ["loc_id"],
          "signal_id": "signal_id_or_null",
          "polarity": "strength|weakness|neutral",
          "evidence_ids": ["ev_001"],
          "numbers": [12.5]
        }}
      ]
    }}
  ],
  "insufficient_data": false,
  "missing_reason": null
}}
"""
