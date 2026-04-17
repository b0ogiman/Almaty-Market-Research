import { BoltIcon } from "@heroicons/react/24/solid";
import { MapPinIcon } from "@heroicons/react/24/outline";

export interface OpportunityItem {
  id: string;
  name: string;
  district: string;
  sector: string;
  score: number;
}

interface Props {
  loading: boolean;
  opportunities: OpportunityItem[];
}

const SECTOR_RU: Record<string, string> = {
  food_service: "Общепит",
  retail: "Ритейл",
  services: "Услуги",
  health: "Здоровье",
  beauty: "Красота",
  fitness: "Фитнес",
  education: "Образование",
  other: "Другое",
  general: "Общее",
};

function scoreColor(score: number) {
  if (score >= 0.6) return "bg-accent-500/15 text-accent-400 ring-1 ring-accent-500/20";
  if (score >= 0.35) return "bg-yellow-500/15 text-yellow-400 ring-1 ring-yellow-500/20";
  return "bg-red-500/15 text-red-400 ring-1 ring-red-500/20";
}

function OpportunityList({ loading, opportunities }: Props) {
  return (
    <div className="card p-5 h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-slate-100">Возможности</h3>
          <p className="text-xs text-slate-500 mt-0.5">По спросу и конкуренции</p>
        </div>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-600/15">
          <BoltIcon className="h-4 w-4 text-primary-400" />
        </div>
      </div>

      <div className="space-y-2 max-h-[480px] overflow-y-auto pr-1">
        {loading && Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-14 animate-pulse rounded-xl bg-slate-800/60" />
        ))}

        {!loading && opportunities.length === 0 && (
          <div className="flex flex-col items-center py-8 text-center">
            <BoltIcon className="h-8 w-8 text-slate-700 mb-2" />
            <p className="text-sm text-slate-500">Нет данных</p>
            <p className="text-xs text-slate-600 mt-1">Запустите анализ рынка</p>
          </div>
        )}

        {opportunities.map((o) => (
          <div
            key={o.id}
            className="group rounded-xl border border-slate-800/60 bg-slate-900/40 px-3.5 py-3
                       transition-all hover:border-slate-700 hover:bg-slate-800/40"
          >
            <div className="flex items-center justify-between gap-2">
              <span className="truncate text-sm font-medium text-slate-200">{o.name}</span>
              <span className={`badge shrink-0 ${scoreColor(o.score)}`}>
                {Math.round(o.score * 100)}
              </span>
            </div>
            <div className="mt-1.5 flex items-center gap-3 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <MapPinIcon className="h-3 w-3" />
                {o.district}
              </span>
              <span>{SECTOR_RU[o.sector] ?? o.sector}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OpportunityList;
