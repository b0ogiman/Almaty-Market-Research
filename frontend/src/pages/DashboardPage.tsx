import { useEffect } from "react";
import { useDashboardStore } from "../store/dashboardStore";
import AnalysisSummaryCards from "../components/AnalysisSummaryCards";
import OpportunityList from "../components/OpportunityList";
import DemandCompetitionCharts from "../components/DemandCompetitionCharts";

function DashboardPage() {
  const {
    loadOverview,
    loadingOverview,
    overviewError,
    analysisSummary,
    opportunities
  } = useDashboardStore();

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Dashboard</h2>
          <p className="text-sm text-slate-400">
            Overview of market analysis, demand, competition, and opportunities.
          </p>
        </div>
      </div>

      {overviewError && (
        <div className="rounded-md border border-red-500/40 bg-red-500/10 px-4 py-2 text-sm text-red-200">
          {overviewError}
        </div>
      )}

      <AnalysisSummaryCards
        loading={loadingOverview}
        summary={analysisSummary}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DemandCompetitionCharts
            loading={loadingOverview}
            summary={analysisSummary}
          />
        </div>
        <div className="lg:col-span-1">
          <OpportunityList
            loading={loadingOverview}
            opportunities={opportunities}
          />
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;

