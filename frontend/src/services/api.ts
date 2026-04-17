import axios from "axios";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 15000
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const message =
        error.response.data?.detail ||
        error.response.data?.message ||
        `Request failed with status ${error.response.status}`;
      return Promise.reject(new Error(message));
    }
    if (error.request) {
      return Promise.reject(
        new Error("No response from server. Please check your connection.")
      );
    }
    return Promise.reject(error);
  }
);

export interface AnalysisOverviewResponse {
  // The backend returns a list of analysis results; we summarise client-side.
}

export async function fetchHealth(): Promise<void> {
  await api.get("/health");
}

export interface Stats {
  total_listings: number;
  by_source: Record<string, number>;
  by_category: Record<string, number>;
}

export async function fetchStats(): Promise<Stats> {
  const res = await api.get("/stats");
  return res.data;
}

export interface AnalysisResult {
  id: string;
  sector: string;
  district: string;
  summary: string | null;
  score: number | null;
  insights: {
    demand_score?: number;
    gap_score?: number;
    target_district?: string;
    target_category?: string;
    trend?: { direction: string; slope: number };
    clusters?: Record<string, { count: number; avg_rating: number | null; categories: string[] }>;
  } | null;
  created_at: string;
}

export async function runMarketAnalysis(payload: {
  sector?: string | null;
  district?: string | null;
}): Promise<AnalysisResult> {
  const res = await api.post("/analysis/market", {
    sector: payload.sector ?? null,
    district: payload.district ?? null
  });
  return res.data;
}

export interface Opportunity {
  id: string;
  name: string;
  district: string | null;
  sector: string | null;
  score: number;
}

export async function fetchOpportunities(): Promise<Opportunity[]> {
  const res = await api.get("/opportunities");
  return res.data.items ?? res.data ?? [];
}

export interface AnalysisItem {
  id: string;
  created_at?: string;
  insights?: Record<string, unknown> | null;
}

export async function fetchAnalyses(): Promise<AnalysisItem[]> {
  const res = await api.get("/analysis", { params: { size: 50 } });
  return res.data.items ?? res.data ?? [];
}

export interface Competitor {
  id: string;
  name: string;
  category: string | null;
  category_normalized: string | null;
  district: string | null;
  address: string | null;
  rating: number | null;
  review_count: number | null;
}

export async function fetchCompetitors(params: {
  sector?: string | null;
  district?: string | null;
  limit?: number;
}): Promise<{ items: Competitor[]; total: number }> {
  const res = await api.get("/competitors", {
    params: {
      sector: params.sector ?? undefined,
      district: params.district ?? undefined,
      limit: params.limit ?? 10,
    },
  });
  return { items: res.data.items ?? [], total: res.data.total ?? 0 };
}

export async function triggerCollection(): Promise<{ message: string }> {
  const res = await api.post("/collect");
  return res.data;
}

export interface TrendPoint {
  snapshot_date: string;
  district: string;
  category: string | null;
  business_count: number;
  avg_rating: number | null;
  avg_review_count: number | null;
  competition_index: number | null;
}

export async function fetchTrends(params?: {
  district?: string;
  category?: string;
  days?: number;
}): Promise<TrendPoint[]> {
  const res = await api.get("/trends", { params });
  return res.data.items ?? [];
}

export interface DistrictDemographics {
  district: string;
  population: number;
  area_km2: number;
  avg_income_usd: number;
  density_per_km2: number;
  commercial_zones: string[];
  notes: string;
}

export async function fetchDemographics(): Promise<DistrictDemographics[]> {
  const res = await api.get("/demographics");
  return res.data.items ?? [];
}

export default api;

