import { useEffect, useState } from "react";
import { fetchDemographics, type DistrictDemographics } from "../services/api";
import { UsersIcon, ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/outline";

const DISTRICT_RU: Record<string, string> = {
  Bostandyq: "Бостандык", Almaly: "Алмалы", Medeu: "Медеу",
  Auezov: "Ауэзов", Alatau: "Алатау", Turksib: "Түрксіб",
  Zhetysu: "Жетісу", Nauryzbay: "Наурызбай",
};

function MiniBar({ value, max, color }: { value: number; max: number; color: string }) {
  const pct = Math.round((value / max) * 100);
  return (
    <div className="h-1 w-full rounded-full bg-slate-800">
      <div className="h-1 rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
    </div>
  );
}

function incomeLabel(income: number) {
  if (income >= 700) return { text: "Высокий", color: "text-accent-400 bg-accent-500/10" };
  if (income >= 500) return { text: "Средний", color: "text-yellow-400 bg-yellow-500/10" };
  return { text: "Ниже среднего", color: "text-orange-400 bg-orange-500/10" };
}

export default function DemographicsPanel() {
  const [items, setItems] = useState<DistrictDemographics[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetchDemographics().then(setItems).finally(() => setLoading(false));
  }, []);

  const maxPop = Math.max(...items.map((i) => i.population), 1);
  const maxIncome = Math.max(...items.map((i) => i.avg_income_usd), 1);
  const maxDensity = Math.max(...items.map((i) => i.density_per_km2), 1);

  return (
    <div className="card p-5">
      <div className="flex items-center gap-3 mb-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600/15">
          <UsersIcon className="h-5 w-5 text-primary-400" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-100">Демография районов Алматы</h3>
          <p className="text-xs text-slate-500 mt-0.5">Источник: stat.gov.kz, 2023</p>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-2xl bg-slate-800/60" />
          ))}
        </div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {items.map((d) => {
            const isOpen = expanded === d.district;
            const inc = incomeLabel(d.avg_income_usd);
            return (
              <button
                key={d.district}
                onClick={() => setExpanded(isOpen ? null : d.district)}
                className={`rounded-2xl border p-4 text-left transition-all ${
                  isOpen
                    ? "border-primary-500/30 bg-primary-600/8 shadow-[0_0_20px_rgba(139,92,246,0.08)]"
                    : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-800/40"
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="font-semibold text-slate-200 text-sm">
                    {DISTRICT_RU[d.district] ?? d.district}
                  </span>
                  {isOpen
                    ? <ChevronUpIcon className="h-4 w-4 text-slate-500 shrink-0" />
                    : <ChevronDownIcon className="h-4 w-4 text-slate-600 shrink-0" />
                  }
                </div>

                <p className="text-xl font-bold text-slate-100 mb-1">
                  {(d.population / 1000).toFixed(0)}
                  <span className="text-sm font-normal text-slate-500 ml-1">тыс.</span>
                </p>

                <div className="space-y-1.5 mb-3">
                  <MiniBar value={d.population} max={maxPop} color="#8b5cf6" />
                  <MiniBar value={d.avg_income_usd} max={maxIncome} color="#10b981" />
                  <MiniBar value={d.density_per_km2} max={maxDensity} color="#f97316" />
                </div>

                <span className={`badge text-[10px] font-medium ${inc.color}`}>
                  {inc.text} доход
                </span>

                {isOpen && (
                  <div className="mt-3 border-t border-slate-700/50 pt-3 space-y-1.5 text-xs text-slate-400">
                    <div className="flex justify-between">
                      <span>Площадь</span>
                      <span className="text-slate-300">{d.area_km2} км²</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Ср. доход</span>
                      <span className="text-slate-300">${d.avg_income_usd}/мес</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Плотность</span>
                      <span className="text-slate-300">{d.density_per_km2.toLocaleString()} чел/км²</span>
                    </div>
                    <div className="mt-2 text-slate-500">
                      <span className="text-slate-600">Торговые зоны: </span>
                      {d.commercial_zones.join(", ")}
                    </div>
                    <p className="italic text-slate-600 leading-relaxed">{d.notes}</p>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}

      <div className="mt-4 flex items-center gap-4 text-xs text-slate-600">
        <span className="flex items-center gap-1.5"><span className="h-1.5 w-4 rounded-full bg-primary-500" /> Население</span>
        <span className="flex items-center gap-1.5"><span className="h-1.5 w-4 rounded-full bg-accent-500" /> Доход</span>
        <span className="flex items-center gap-1.5"><span className="h-1.5 w-4 rounded-full bg-orange-500" /> Плотность</span>
      </div>
    </div>
  );
}
