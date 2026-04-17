import { create } from "zustand";
import { devtools } from "zustand/middleware";
import {
  fetchAnalyses,
  fetchHealth,
  fetchOpportunities,
  fetchStats,
  runMarketAnalysis,
  triggerCollection,
  type Opportunity as ApiOpportunity,
  type AnalysisResult,
  type AnalysisItem,
} from "../services/api";
import type { AnalysisSummary } from "../components/AnalysisSummaryCards";
import type { OpportunityItem } from "../components/OpportunityList";

export interface DistrictChartRow {
  district: string;
  demand: number;
  competition: number;
  score: number;
}

interface DashboardState {
  loadingOverview: boolean;
  overviewError: string | null;
  analysisSummary: AnalysisSummary | null;
  opportunities: OpportunityItem[];
  districtChartData: DistrictChartRow[];
  lastAnalysis: AnalysisResult | null;
  analysisError: string | null;
  collecting: boolean;
  collectMessage: string | null;

  loadOverview: () => Promise<void>;
  runAnalysis: (payload: { sector?: string | null; district?: string | null }) => Promise<void>;
  collectData: () => Promise<void>;
}

function buildDistrictChart(analyses: AnalysisItem[]): DistrictChartRow[] {
  const seen = new Map<string, DistrictChartRow>();
  for (const item of analyses) {
    const ins = (item as AnalysisResult).insights;
    const district = ins?.target_district ?? (item as AnalysisResult).district;
    if (!district || district === "all" || seen.has(district)) continue;
    const demand = ins?.demand_score ?? 0;
    const gap = ins?.gap_score ?? 0;
    seen.set(district, {
      district,
      demand: Math.round(demand * 100) / 100,
      competition: Math.round((1 - gap) * 100) / 100,
      score: Math.round(((item as AnalysisResult).score ?? 0) * 100) / 100,
    });
  }
  return Array.from(seen.values()).slice(0, 8);
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    (set) => ({
      loadingOverview: false,
      overviewError: null,
      analysisSummary: null,
      opportunities: [],
      districtChartData: [],
      lastAnalysis: null,
      analysisError: null,
      collecting: false,
      collectMessage: null,

      async loadOverview() {
        set({ loadingOverview: true, overviewError: null });
        try {
          await fetchHealth();
          const [analyses, ops, stats] = await Promise.all([
            fetchAnalyses(),
            fetchOpportunities(),
            fetchStats(),
          ]);

          const districtChartData = buildDistrictChart(analyses);

          const topByScore = [...(analyses as AnalysisResult[])]
            .filter((a) => a.score != null)
            .sort((a, b) => (b.score ?? 0) - (a.score ?? 0));

          const summary: AnalysisSummary = {
            totalListings: stats.total_listings,
            avgRating: 4.2,
            avgSentiment: 0.6,
            topDistrict: topByScore[0]?.insights?.target_district ?? ops[0]?.district ?? undefined,
            topSector: topByScore[0]?.sector ?? ops[0]?.sector ?? undefined,
          };

          const mappedOps: OpportunityItem[] = (ops as ApiOpportunity[]).map((o) => ({
            id: o.id,
            name: o.name,
            district: o.district ?? "Unknown",
            sector: o.sector ?? "General",
            score: o.score,
          }));

          set({
            analysisSummary: summary,
            opportunities: mappedOps,
            districtChartData,
            loadingOverview: false,
            overviewError: null,
          });
        } catch (err) {
          const message = err instanceof Error ? err.message : "Failed to load overview.";
          set({ loadingOverview: false, overviewError: message });
        }
      },

      async runAnalysis(payload) {
        set({ analysisError: null });
        try {
          const result = await runMarketAnalysis(payload);
          set({ lastAnalysis: result });
        } catch (err) {
          const message = err instanceof Error ? err.message : "Analysis failed.";
          set({ analysisError: message });
        }
      },

      async collectData() {
        set({ collecting: true, collectMessage: null });
        try {
          const res = await triggerCollection();
          set({ collectMessage: res.message });
        } catch (err) {
          const message = err instanceof Error ? err.message : "Collection failed.";
          set({ collectMessage: message });
        } finally {
          set({ collecting: false });
        }
      },
    }),
    { name: "dashboard-store" }
  )
);
