import { FormEvent, useState } from "react";
import { useDashboardStore } from "../store/dashboardStore";

interface Props {
  onAnalyzed?: () => void;
}

function AnalysisForm({ onAnalyzed }: Props) {
  const [sector, setSector] = useState("food_service");
  const [district, setDistrict] = useState("All");
  const [submitting, setSubmitting] = useState(false);
  const runAnalysis = useDashboardStore((s) => s.runAnalysis);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await runAnalysis({ sector, district: district === "All" ? null : district });
      onAnalyzed?.();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4"
    >
      <div>
        <h2 className="text-sm font-semibold text-slate-100">
          Run market analysis
        </h2>
        <p className="mt-1 text-xs text-slate-400">
          Choose sector and district to analyze demand, competition, and
          opportunities in Almaty.
        </p>
      </div>

      <div className="space-y-1">
        <label className="text-xs font-medium text-slate-300">
          Sector
        </label>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-primary-500 focus:outline-none"
          value={sector}
          onChange={(e) => setSector(e.target.value)}
        >
          <option value="food_service">Food service</option>
          <option value="retail">Retail</option>
          <option value="services">Services</option>
          <option value="health_beauty">Health & beauty</option>
          <option value="education">Education</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div className="space-y-1">
        <label className="text-xs font-medium text-slate-300">
          District
        </label>
        <select
          className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:border-primary-500 focus:outline-none"
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
        >
          <option value="All">All districts</option>
          <option value="Bostandyk">Bostandyk</option>
          <option value="Almaly">Almaly</option>
          <option value="Medey">Medey</option>
          <option value="Auezov">Auezov</option>
          <option value="Turksib">Turksib</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="inline-flex w-full items-center justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {submitting ? "Analyzing…" : "Run analysis"}
      </button>
    </form>
  );
}

export default AnalysisForm;

