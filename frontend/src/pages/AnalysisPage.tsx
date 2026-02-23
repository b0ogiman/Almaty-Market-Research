import { useState } from "react";
import AnalysisForm from "../components/AnalysisForm";
import AnalysisResultPanel from "../components/AnalysisResultPanel";

function AnalysisPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <div className="lg:col-span-1">
        <AnalysisForm onAnalyzed={() => setRefreshKey((k) => k + 1)} />
      </div>
      <div className="lg:col-span-2">
        <AnalysisResultPanel refreshKey={refreshKey} />
      </div>
    </div>
  );
}

export default AnalysisPage;

