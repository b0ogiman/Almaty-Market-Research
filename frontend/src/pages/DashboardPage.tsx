import { useEffect } from "react";
import { useDashboardStore } from "../store/dashboardStore";
import AnalysisSummaryCards from "../components/AnalysisSummaryCards";
import OpportunityList from "../components/OpportunityList";
import DemandCompetitionCharts from "../components/DemandCompetitionCharts";
import TrendsChart from "../components/TrendsChart";
import DemographicsPanel from "../components/DemographicsPanel";
import { ArrowPathIcon, CheckCircleIcon } from "@heroicons/react/24/outline";

function DashboardPage() {
  const {
    loadOverview, loadingOverview, overviewError,
    analysisSummary, opportunities, districtChartData,
    collecting, collectMessage, collectData,
  } = useDashboardStore();

  useEffect(() => { void loadOverview(); }, [loadOverview]);

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
            Дашборд
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Обзор рынка Алматы — аналитика, конкуренция и возможности
          </p>
        </div>

        <div className="flex flex-col items-start sm:items-end gap-2">
          <button
            onClick={() => void collectData()}
            disabled={collecting}
            className="btn-ghost text-xs py-2"
          >
            {collecting ? (
              <>
                <span className="h-3.5 w-3.5 animate-spin rounded-full border border-slate-400 border-t-transparent" />
                Собираю данные…
              </>
            ) : (
              <>
                <ArrowPathIcon className="h-3.5 w-3.5" />
                Обновить данные (2GIS)
              </>
            )}
          </button>
          {collectMessage && (
            <p className="flex items-center gap-1.5 text-xs text-accent-400">
              <CheckCircleIcon className="h-3.5 w-3.5" />
              {collectMessage}
            </p>
          )}
        </div>
      </div>

      {overviewError && (
        <div className="rounded-2xl border border-red-500/30 bg-red-500/8 px-4 py-3 text-sm text-red-300">
          {overviewError}
        </div>
      )}

      {/* KPI cards */}
      <AnalysisSummaryCards loading={loadingOverview} summary={analysisSummary} />

      {/* Charts + Opportunities */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DemandCompetitionCharts
            loading={loadingOverview}
            summary={analysisSummary}
            districtChartData={districtChartData}
          />
        </div>
        <div className="lg:col-span-1">
          <OpportunityList loading={loadingOverview} opportunities={opportunities} />
        </div>
      </div>

      {/* Trends */}
      <TrendsChart />

      {/* Demographics */}
      <DemographicsPanel />
    </div>
  );
}

export default DashboardPage;
