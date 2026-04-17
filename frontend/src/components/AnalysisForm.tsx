import { FormEvent, useState } from "react";
import { useDashboardStore } from "../store/dashboardStore";
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon } from "@heroicons/react/24/outline";

interface Props {
  onAnalyzed?: (sector: string, district: string | null) => void;
}

const SECTORS = [
  { value: "food_service", label: "Общепит" },
  { value: "retail",       label: "Ритейл" },
  { value: "services",     label: "Услуги" },
  { value: "health",       label: "Здоровье и медицина" },
  { value: "beauty",       label: "Красота и уход" },
  { value: "fitness",      label: "Фитнес и спорт" },
  { value: "education",    label: "Образование" },
  { value: "other",        label: "Другое" },
];

const DISTRICTS = [
  { value: "All",       label: "Все районы" },
  { value: "Bostandyq", label: "Бостандык" },
  { value: "Almaly",    label: "Алмалы" },
  { value: "Medeu",     label: "Медеу" },
  { value: "Auezov",    label: "Ауэзов" },
  { value: "Alatau",    label: "Алатау" },
  { value: "Turksib",   label: "Түрксіб" },
  { value: "Zhetysu",   label: "Жетісу" },
  { value: "Nauryzbay", label: "Наурызбай" },
];

function AnalysisForm({ onAnalyzed }: Props) {
  const [sector, setSector] = useState("food_service");
  const [district, setDistrict] = useState("All");
  const [submitting, setSubmitting] = useState(false);
  const runAnalysis = useDashboardStore((s) => s.runAnalysis);
  const analysisError = useDashboardStore((s) => s.analysisError);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      const d = district === "All" ? null : district;
      await runAnalysis({ sector, district: d });
      onAnalyzed?.(sector, d);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card p-6 space-y-5">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-600/20 ring-1 ring-primary-500/30">
          <AdjustmentsHorizontalIcon className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h2 className="font-semibold text-slate-100">Параметры анализа</h2>
          <p className="text-xs text-slate-500">Выберите сектор и район</p>
        </div>
      </div>

      <div>
        <label className="label">Сектор бизнеса</label>
        <select className="input" value={sector} onChange={(e) => setSector(e.target.value)}>
          {SECTORS.map((s) => (
            <option key={s.value} value={s.value}>{s.label}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="label">Район Алматы</label>
        <select className="input" value={district} onChange={(e) => setDistrict(e.target.value)}>
          {DISTRICTS.map((d) => (
            <option key={d.value} value={d.value}>{d.label}</option>
          ))}
        </select>
      </div>

      {analysisError && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/8 px-4 py-3 text-xs text-red-300">
          {analysisError}
        </div>
      )}

      <button type="submit" disabled={submitting} className="btn-primary w-full">
        {submitting ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Анализирую…
          </>
        ) : (
          <>
            <MagnifyingGlassIcon className="h-4 w-4" />
            Запустить анализ
          </>
        )}
      </button>
    </form>
  );
}

export default AnalysisForm;
