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

export async function runMarketAnalysis(payload: {
  sector?: string | null;
  district?: string | null;
}): Promise<void> {
  await api.post("/analysis/market", {
    sector: payload.sector ?? null,
    district: payload.district ?? null
  });
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
  const res = await api.get("/analysis");
  return res.data.items ?? res.data ?? [];
}

export default api;

