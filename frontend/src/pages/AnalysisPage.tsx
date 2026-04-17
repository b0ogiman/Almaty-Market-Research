import { useState } from "react";
import AnalysisForm from "../components/AnalysisForm";
import AnalysisResultPanel from "../components/AnalysisResultPanel";
import CompetitorsList from "../components/CompetitorsList";

function AnalysisPage() {
  const [refreshKey, setRefreshKey] = useState(0);
  const [filters, setFilters] = useState<{ sector: string | null; district: string | null }>({
    sector: "food_service",
    district: null,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent">
          Анализ рынка
        </h2>
        <p className="text-sm text-slate-500 mt-1">
          Выберите сектор и район — получите оценку спроса, конкуренции и топ конкурентов
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <AnalysisForm
            onAnalyzed={(sector, district) => {
              setRefreshKey((k) => k + 1);
              setFilters({ sector, district });
            }}
          />
        </div>
        <div className="lg:col-span-2">
          <AnalysisResultPanel refreshKey={refreshKey} />
        </div>
      </div>

      <CompetitorsList sector={filters.sector} district={filters.district} />
    </div>
  );
}

export default AnalysisPage;
