# Contracts Changelog

## [1.0.0] - 2026-10-17
### Initial Contract Freeze
- Added `/health` returning `HealthResponse`.
- Added `/api/v1/meta` returning cities, categories, budget tiers, signals metadata, default weights, dataset attribution.
- Added `/api/v1/analyses` (POST to create analysis, GET by ID).
- Added `/api/v1/analyses/{id}/locations/{location_id}` (GET location report).
- Added `/api/v1/analyses/{id}/compare` (POST to compare 2-3 locations with per-signal deltas).
- Added `/api/v1/analyses/{id}/chat` (POST verified AI chat with single-sentence blocks, claims, evidence IDs, polarity).
- Added `/api/v1/trust/stats` (GET live & evaluation trust metrics).
- Added `/api/v1/trust/traces/{trace_id}` (GET trace inspection detail).
