import { useEffect } from "react";
import { useDashboardStore } from "../store/dashboardStore";
import DemandCompetitionCharts from "./DemandCompetitionCharts";
import OpportunityList from "./OpportunityList";

interface Props {
  refreshKey: number;
}

function AnalysisResultPanel({ refreshKey }: Props) {
  const {
    loadOverview,
    loadingOverview,
    overviewError,
    analysisSummary,
    opportunities
  } = useDashboardStore();

  useEffect(() => {
    void loadOverview();
  }, [loadOverview, refreshKey]);

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-100">
            Latest analysis results
          </h2>
          <p className="text-xs text-slate-400">
            Summary of demand, competition, sentiment, and opportunities for
            Almaty.
          </p>
        </div>
      </div>

      {overviewError && (
        <div className="rounded-md border border-red-500/40 bg-red-500/10 px-3 py-2 text-xs text-red-200">
          {overviewError}
        </div>
      )}

      <DemandCompetitionCharts
        loading={loadingOverview}
        summary={analysisSummary}
      />

      <OpportunityList
        loading={loadingOverview}
        opportunities={opportunities}
      />
    </div>
  );
}

export default AnalysisResultPanel;

