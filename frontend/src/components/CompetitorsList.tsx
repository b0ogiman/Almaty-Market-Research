import { useEffect, useState } from "react";
import { fetchCompetitors, type Competitor } from "../services/api";
import { TrophyIcon, MapPinIcon, StarIcon } from "@heroicons/react/24/outline";
import { FireIcon } from "@heroicons/react/24/solid";

interface Props {
  sector: string | null;
  district: string | null;
}

const DISTRICT_RU: Record<string, string> = {
  Bostandyq: "Бостандык", Almaly: "Алмалы", Medeu: "Медеу",
  Auezov: "Ауэзов", Alatau: "Алатау", Turksib: "Түрксіб",
  Zhetysu: "Жетісу", Nauryzbay: "Наурызбай",
};

function RatingBar({ rating, max = 5 }: { rating: number; max?: number }) {
  const pct = (rating / max) * 100;
  const color = rating >= 4.5 ? "#10b981" : rating >= 4.0 ? "#eab308" : "#f97316";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1 w-16 rounded-full bg-slate-800">
        <div className="h-1 rounded-full" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-semibold" style={{ color }}>{rating.toFixed(1)}</span>
    </div>
  );
}

function medalColor(i: number) {
  if (i === 0) return "text-yellow-400 bg-yellow-400/10";
  if (i === 1) return "text-slate-300 bg-slate-300/10";
  if (i === 2) return "text-orange-400 bg-orange-400/10";
  return "text-slate-600 bg-slate-800/40";
}

export default function CompetitorsList({ sector, district }: Props) {
  const [items, setItems] = useState<Competitor[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!sector) return;
    setLoading(true);
    fetchCompetitors({ sector, district, limit: 10 })
      .then(({ items, total }) => { setItems(items); setTotal(total); })
      .finally(() => setLoading(false));
  }, [sector, district]);

  if (!sector) return null;

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-yellow-500/10">
            <TrophyIcon className="h-5 w-5 text-yellow-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100">Топ конкурентов</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              {total > 0 ? `${total} заведений в выборке` : "По количеству отзывов"}
            </p>
          </div>
        </div>
        {total > 10 && (
          <span className="badge bg-slate-800 text-slate-400">
            Топ 10 из {total}
          </span>
        )}
      </div>

      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 animate-pulse rounded-xl bg-slate-800/60" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center py-10 text-center">
          <TrophyIcon className="h-10 w-10 text-slate-700 mb-3" />
          <p className="text-sm text-slate-500">Нет данных по выбранным фильтрам</p>
          <p className="text-xs text-slate-600 mt-1">Попробуйте другой сектор или район</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((c, i) => (
            <div
              key={c.id}
              className="group flex items-center gap-3 rounded-xl border border-slate-800/60
                         bg-slate-900/40 px-4 py-3 transition-all hover:border-slate-700 hover:bg-slate-800/40"
            >
              {/* Rank */}
              <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${medalColor(i)}`}>
                {i < 3 ? <FireIcon className="h-4 w-4" /> : i + 1}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <p className="truncate text-sm font-medium text-slate-200 group-hover:text-white">
                    {c.name}
                  </p>
                  {c.rating && <RatingBar rating={c.rating} />}
                </div>
                <div className="mt-1 flex items-center gap-3 text-xs text-slate-500">
                  {c.district && (
                    <span className="flex items-center gap-1">
                      <MapPinIcon className="h-3 w-3" />
                      {DISTRICT_RU[c.district] ?? c.district}
                    </span>
                  )}
                  {c.address && (
                    <span className="truncate">{c.address}</span>
                  )}
                </div>
              </div>

              {/* Review count */}
              {c.review_count && (
                <div className="shrink-0 text-right">
                  <div className="flex items-center gap-1 text-xs text-slate-400">
                    <StarIcon className="h-3.5 w-3.5 text-yellow-500/70" />
                    <span className="font-medium">{c.review_count.toLocaleString()}</span>
                  </div>
                  <p className="text-[10px] text-slate-600">отзывов</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
