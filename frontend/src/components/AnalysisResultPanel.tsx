import { useDashboardStore } from "../store/dashboardStore";
import { ChartBarIcon, MapPinIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, MinusIcon } from "@heroicons/react/24/outline";
import { SparklesIcon } from "@heroicons/react/24/solid";

const SECTOR_RU: Record<string, string> = {
  food_service: "Общепит", retail: "Ритейл", services: "Услуги",
  health: "Здоровье", beauty: "Красота", fitness: "Фитнес",
  education: "Образование", other: "Другое", all: "Все секторы",
};
const DISTRICT_RU: Record<string, string> = {
  Bostandyq: "Бостандык", Almaly: "Алмалы", Medeu: "Медеу",
  Auezov: "Ауэзов", Alatau: "Алатау", Turksib: "Түрксіб",
  Zhetysu: "Жетісу", Nauryzbay: "Наурызбай", all: "Все районы",
};

function ScoreRing({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.6 ? "#10b981" : score >= 0.35 ? "#f59e0b" : "#ef4444";
  const r = 22, c = 28, circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <div className="flex flex-col items-center">
      <svg width={56} height={56} viewBox="0 0 56 56">
        <circle cx={c} cy={c} r={r} fill="none" stroke="#1e293b" strokeWidth={4} />
        <circle
          cx={c} cy={c} r={r} fill="none"
          stroke={color} strokeWidth={4}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 28 28)"
        />
        <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle"
          fill={color} fontSize={13} fontWeight="700">{pct}</text>
      </svg>
      <span className="text-[10px] text-slate-500 mt-0.5">балл</span>
    </div>
  );
}

function MetricBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const color = value >= 0.6 ? "bg-accent-500" : value >= 0.35 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="font-semibold text-slate-200">{pct}%</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-slate-800">
        <div className={`h-1.5 rounded-full transition-all duration-700 ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

interface Props { refreshKey: number }

function AnalysisResultPanel(_: Props) {
  const { lastAnalysis, analysisError } = useDashboardStore();

  if (analysisError) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/8 p-5 text-sm text-red-300">
        <strong>Ошибка:</strong> {analysisError}
      </div>
    );
  }

  if (!lastAnalysis) {
    return (
      <div className="card flex flex-col items-center justify-center py-16 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-600/10 ring-1 ring-primary-500/20 mb-4">
          <ChartBarIcon className="h-7 w-7 text-primary-500/60" />
        </div>
        <p className="text-sm font-medium text-slate-300">Результаты анализа появятся здесь</p>
        <p className="mt-1 text-xs text-slate-500">Выберите параметры и нажмите «Запустить анализ»</p>
      </div>
    );
  }

  const ins = lastAnalysis.insights;
  const score = lastAnalysis.score ?? 0;
  const clusters = ins?.clusters ? Object.entries(ins.clusters) : [];
  const sectorLabel = SECTOR_RU[lastAnalysis.sector] ?? lastAnalysis.sector;
  const districtLabel = DISTRICT_RU[lastAnalysis.district] ?? lastAnalysis.district;
  const targetDistrictLabel = ins?.target_district ? (DISTRICT_RU[ins.target_district] ?? ins.target_district) : null;

  return (
    <div className="space-y-4">
      {/* Header card */}
      <div className="card-glow p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <span className="badge bg-primary-600/20 text-primary-300 ring-1 ring-primary-500/30">
                {sectorLabel}
              </span>
              <span className="badge bg-slate-800 text-slate-400">
                {districtLabel}
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">{lastAnalysis.summary}</p>
          </div>
          <ScoreRing score={score} />
        </div>
      </div>

      {/* Metrics */}
      {ins && (ins.demand_score !== undefined || ins.gap_score !== undefined) && (
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-4 w-4 text-primary-400" />
            <h3 className="text-sm font-semibold text-slate-100">Ключевые метрики</h3>
          </div>
          {ins.demand_score !== undefined && (
            <MetricBar label="Спрос" value={ins.demand_score} />
          )}
          {ins.gap_score !== undefined && (
            <MetricBar label="Рыночный пробел" value={ins.gap_score} />
          )}
          <MetricBar label="Итоговый балл" value={score} />
        </div>
      )}

      {/* Recommendation */}
      {targetDistrictLabel && (
        <div className="rounded-2xl border border-accent-500/25 bg-accent-500/5 p-5">
          <div className="flex items-center gap-2 mb-3">
            <MapPinIcon className="h-4 w-4 text-accent-400" />
            <h3 className="text-sm font-semibold text-accent-400">Рекомендация</h3>
          </div>
          <p className="text-sm text-slate-200">
            Лучший район для входа:{" "}
            <span className="font-bold text-accent-400">{targetDistrictLabel}</span>
          </p>
          {ins?.trend && (
            <div className="mt-2 flex items-center gap-1.5 text-xs text-slate-400">
              {ins.trend.direction === "up" ? (
                <ArrowTrendingUpIcon className="h-4 w-4 text-accent-400" />
              ) : ins.trend.direction === "down" ? (
                <ArrowTrendingDownIcon className="h-4 w-4 text-red-400" />
              ) : (
                <MinusIcon className="h-4 w-4 text-slate-500" />
              )}
              <span>
                Тренд:{" "}
                <span className={ins.trend.direction === "up" ? "text-accent-400" : ins.trend.direction === "down" ? "text-red-400" : "text-slate-400"}>
                  {ins.trend.direction === "up" ? "растёт" : ins.trend.direction === "down" ? "снижается" : "стабильный"}
                </span>
              </span>
            </div>
          )}
        </div>
      )}

      {/* Clusters */}
      {clusters.length > 0 && (
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-100 mb-3">Кластеры конкурентов</h3>
          <div className="space-y-2">
            {clusters.map(([key, cl]) => (
              <div key={key} className="flex items-center justify-between rounded-xl bg-slate-800/40 px-4 py-3 text-xs">
                <div>
                  <span className="font-medium text-slate-200">Группа {Number(key) + 1}</span>
                  <span className="ml-2 text-slate-500">{cl.categories.slice(0, 2).join(", ")}</span>
                </div>
                <div className="flex items-center gap-3 text-slate-400">
                  <span>{cl.count} заведений</span>
                  {cl.avg_rating && <span className="text-yellow-400">★ {cl.avg_rating.toFixed(1)}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <p className="text-right text-xs text-slate-700">
        {new Date(lastAnalysis.created_at).toLocaleString("ru-KZ")}
      </p>
    </div>
  );
}

export default AnalysisResultPanel;
