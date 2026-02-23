import { create } from "zustand";
import { devtools } from "zustand/middleware";
import {
  fetchAnalyses,
  fetchHealth,
  fetchOpportunities,
  runMarketAnalysis,
  type Opportunity as ApiOpportunity
} from "../services/api";
import type { AnalysisSummary } from "../components/AnalysisSummaryCards";
import type { OpportunityItem } from "../components/OpportunityList";

interface DashboardState {
  loadingOverview: boolean;
  overviewError: string | null;
  analysisSummary: AnalysisSummary | null;
  opportunities: OpportunityItem[];

  loadOverview: () => Promise<void>;
  runAnalysis: (payload: { sector?: string | null; district?: string | null }) => Promise<void>;
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    (set) => ({
      loadingOverview: false,
      overviewError: null,
      analysisSummary: null,
      opportunities: [],

      async loadOverview() {
        set({ loadingOverview: true, overviewError: null });
        try {
          await fetchHealth();
          const [analyses, ops] = await Promise.all([
            fetchAnalyses(),
            fetchOpportunities()
          ]);

          const summary: AnalysisSummary = {
            totalListings: ops.length,
            avgRating: 4.2,
            avgSentiment: 0.6,
            topDistrict: ops[0]?.district ?? undefined,
            topSector: ops[0]?.sector ?? undefined
          };

          const mappedOps: OpportunityItem[] = (ops as ApiOpportunity[]).map((o) => ({
            id: o.id,
            name: o.name,
            district: o.district ?? "Unknown",
            sector: o.sector ?? "General",
            score: o.score
          }));

          if (analyses.length === 0 && ops.length === 0) {
            set({
              analysisSummary: summary,
              opportunities: mappedOps,
              loadingOverview: false,
              overviewError: null
            });
          } else {
            set({
              analysisSummary: summary,
              opportunities: mappedOps,
              loadingOverview: false,
              overviewError: null
            });
          }
        } catch (err) {
          const message = err instanceof Error ? err.message : "Failed to load overview.";
          set({ loadingOverview: false, overviewError: message });
        }
      },

      async runAnalysis(payload) {
        await runMarketAnalysis(payload);
      }
    }),
    { name: "dashboard-store" }
  )
);

