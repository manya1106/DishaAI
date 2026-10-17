import {
  MetaResponse,
  AnalysisResult,
  ReportResponse,
  CompareResult,
  ChatResponse,
  TrustStatsResponse,
  HealthResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const IS_MOCK = process.env.NEXT_PUBLIC_API_MOCK === "1";

// Cache for mock fixtures
let mockAnalysis: AnalysisResult | null = null;

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!resp.ok) {
    let errMessage = `HTTP ${resp.status}: ${resp.statusText}`;
    try {
      const errData = await resp.json();
      if (errData?.error?.message) {
        errMessage = errData.error.message;
      }
    } catch {
      // ignore
    }
    throw new Error(errMessage);
  }

  return (await resp.json()) as T;
}

export const api = {
  async getHealth(): Promise<HealthResponse> {
    if (IS_MOCK) {
      return {
        status: "ok",
        version: "1.0.0",
        data_mode: "mock_fixtures",
        db: "disabled",
        llm: "configured",
      };
    }
    return fetchJson<HealthResponse>(`${API_BASE}/health`);
  },

  async getMeta(): Promise<MetaResponse> {
    if (IS_MOCK) {
      return {
        cities: [
          {
            city_id: "blr",
            name: "Bengaluru",
            country: "India",
            center: { lat: 12.9716, lng: 77.5946 },
            h3_resolution: 8,
          },
        ],
        categories: [
          { category_id: "cafe", name: "Café / Specialty Coffee" },
          { category_id: "pharmacy", name: "Pharmacy / Retail Chemist" },
          { category_id: "gym", name: "Fitness Centre / Gym" },
        ],
        budget_tiers: [
          {
            tier_id: "low",
            name: "Budget / Value",
            max_acceptable_tier: 2,
            description: "Prioritizes low-overhead locations.",
          },
          {
            tier_id: "medium",
            name: "Standard / Growth",
            max_acceptable_tier: 3,
            description: "Accepts up to tier 3 prime commercial rents.",
          },
          {
            tier_id: "high",
            name: "Premium / Flagship",
            max_acceptable_tier: 5,
            description: "Willing to invest in highest-tier luxury areas.",
          },
        ],
        signals: [
          {
            signal_id: "competition_density",
            name: "Competition Density",
            better_when: "lower",
            provenance: "measured",
            description: "Density of same-category competitors in neighbourhood.",
          },
          {
            signal_id: "gap_opportunity",
            name: "Gap Opportunity",
            better_when: "higher",
            provenance: "estimated",
            description: "Ratio of demand proxies to direct competitors.",
          },
          {
            signal_id: "footfall_anchors",
            name: "Footfall Anchors",
            better_when: "higher",
            provenance: "estimated",
            description: "Malls, colleges, markets, and hospitals.",
          },
          {
            signal_id: "transit_access",
            name: "Transit Access",
            better_when: "higher",
            provenance: "measured",
            description: "Bus stop and metro connectivity.",
          },
          {
            signal_id: "complementary_mix",
            name: "Complementary Mix",
            better_when: "higher",
            provenance: "measured",
            description: "Synergetic businesses driving shared foot traffic.",
          },
          {
            signal_id: "residential_catchment",
            name: "Residential Catchment",
            better_when: "higher",
            provenance: "estimated",
            description: "Local household and apartment building density.",
          },
          {
            signal_id: "daytime_population",
            name: "Daytime Population",
            better_when: "higher",
            provenance: "estimated",
            description: "Commercial, office, and tech park daytime presence.",
          },
          {
            signal_id: "road_accessibility",
            name: "Road Accessibility",
            better_when: "higher",
            provenance: "measured",
            description: "Arterial road length and junction network density.",
          },
          {
            signal_id: "rent_efficiency",
            name: "Rent Efficiency",
            better_when: "higher",
            provenance: "heuristic",
            description: "Affordability alignment with selected budget tier.",
          },
        ],
        default_weights: {
          cafe: {
            competition_density: 0.12,
            gap_opportunity: 0.12,
            footfall_anchors: 0.16,
            transit_access: 0.1,
            complementary_mix: 0.1,
            residential_catchment: 0.08,
            daytime_population: 0.14,
            road_accessibility: 0.06,
            rent_efficiency: 0.12,
          },
        },
        dataset: {
          id: "blr-osm-snapshot",
          mode: "mock",
          as_of: "2026-10",
          attribution: "© OpenStreetMap contributors (ODbL)",
          contains_simulated: true,
        },
      };
    }
    return fetchJson<MetaResponse>(`${API_BASE}/api/v1/meta`);
  },

  async createAnalysis(payload: {
    city_id: string;
    category_id: string;
    budget_tier: string;
    top_n?: number;
    weight_overrides?: Record<string, number>;
  }): Promise<AnalysisResult> {
    if (IS_MOCK) {
      if (!mockAnalysis) {
        mockAnalysis = (await import(
          "../fixtures/analysis_cafe_medium.json"
        )) as unknown as AnalysisResult;
      }
      return mockAnalysis;
    }
    return fetchJson<AnalysisResult>(`${API_BASE}/api/v1/analyses`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getAnalysis(analysisId: string): Promise<AnalysisResult> {
    if (IS_MOCK) {
      return this.createAnalysis({
        city_id: "blr",
        category_id: "cafe",
        budget_tier: "medium",
      });
    }
    return fetchJson<AnalysisResult>(`${API_BASE}/api/v1/analyses/${analysisId}`);
  },

  async getLocationReport(
    analysisId: string,
    locationId: string
  ): Promise<ReportResponse> {
    if (IS_MOCK) {
      return (await import(
        "../fixtures/report_blr_loc1.json"
      )) as unknown as ReportResponse;
    }
    return fetchJson<ReportResponse>(
      `${API_BASE}/api/v1/analyses/${analysisId}/locations/${locationId}`
    );
  },

  async compareLocations(
    analysisId: string,
    locationIds: string[]
  ): Promise<CompareResult> {
    if (IS_MOCK) {
      return (await import(
        "../fixtures/compare_sample.json"
      )) as unknown as CompareResult;
    }
    return fetchJson<CompareResult>(
      `${API_BASE}/api/v1/analyses/${analysisId}/compare`,
      {
        method: "POST",
        body: JSON.stringify({ location_ids: locationIds }),
      }
    );
  },

  async chatAnalysis(
    analysisId: string,
    payload: {
      message: string;
      selected_location_ids: string[];
      history?: Array<{ role: string; content: string }>;
      mode?: "auto" | "deterministic";
    }
  ): Promise<ChatResponse> {
    if (IS_MOCK) {
      const msg = payload.message.toLowerCase();
      if (msg.includes("rent in rupees") || msg.includes("revenue")) {
        return (await import(
          "../fixtures/chat_refusal.json"
        )) as unknown as ChatResponse;
      }
      return (await import(
        "../fixtures/chat_verified.json"
      )) as unknown as ChatResponse;
    }
    return fetchJson<ChatResponse>(
      `${API_BASE}/api/v1/analyses/${analysisId}/chat`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  async getTrustStats(): Promise<TrustStatsResponse> {
    return fetchJson<TrustStatsResponse>(`${API_BASE}/api/v1/trust/stats`);
  },
};
