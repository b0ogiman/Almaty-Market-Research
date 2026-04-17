import { useEffect, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend,
} from "recharts";
import { fetchTrends, type TrendPoint } from "../services/api";
import { ArrowTrendingUpIcon } from "@heroicons/react/24/outline";

const DISTRICTS = ["Bostandyq", "Almaly", "Auezov", "Medeu", "Alatau", "Turksib", "Zhetysu", "Nauryzbay"];
const DISTRICT_RU: Record<string, string> = {
  Bostandyq: "Бостандык", Almaly: "Алмалы", Medeu: "Медеу",
  Auezov: "Ауэзов", Alatau: "Алатау", Turksib: "Түрксіб",
  Zhetysu: "Жетісу", Nauryzbay: "Наурызбай",
};
const COLORS = ["#10b981", "#8b5cf6", "#f97316", "#3b82f6", "#ec4899", "#14b8a6", "#eab308", "#ef4444"];

interface ChartRow { date: string; [district: string]: number | string }

export default function TrendsChart() {
  const [data, setData] = useState<ChartRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    fetchTrends({ days })
      .then((points: TrendPoint[]) => {
        const byDate: Record<string, ChartRow> = {};
        for (const p of points) {
          if (!byDate[p.snapshot_date]) byDate[p.snapshot_date] = { date: p.snapshot_date };
          byDate[p.snapshot_date][p.district] = ((byDate[p.snapshot_date][p.district] as number) ?? 0) + p.business_count;
        }
        setData(Object.values(byDate).sort((a, b) => (a.date > b.date ? 1 : -1)));
      })
      .finally(() => setLoading(false));
  }, [days]);

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent-500/15">
            <ArrowTrendingUpIcon className="h-5 w-5 text-accent-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-100">Динамика бизнесов по районам</h3>
            <p className="text-xs text-slate-500 mt-0.5">Количество заведений за период</p>
          </div>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded-xl border border-slate-700 bg-slate-800/60 px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-primary-500"
        >
          <option value={7}>7 дней</option>
          <option value={30}>30 дней</option>
          <option value={90}>90 дней</option>
        </select>
      </div>

      <div className="h-60">
        {loading ? (
          <div className="h-full animate-pulse rounded-xl bg-slate-800/40" />
        ) : data.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <ArrowTrendingUpIcon className="h-8 w-8 text-slate-700 mb-2" />
            <p className="text-sm text-slate-500">Данные появятся после первого сбора</p>
            <p className="text-xs text-slate-600 mt-1">Каждую ночь в 02:00 или вручную через кнопку</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="date" stroke="#475569" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
              <YAxis stroke="#475569" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", borderRadius: "12px", fontSize: 12 }}
                formatter={(v: number, name: string) => [v, DISTRICT_RU[name] ?? name]}
              />
              <Legend formatter={(v) => DISTRICT_RU[v] ?? v} wrapperStyle={{ fontSize: 11 }} />
              {DISTRICTS.map((d, i) => (
                <Line key={d} type="monotone" dataKey={d} stroke={COLORS[i % COLORS.length]}
                  strokeWidth={2} dot={false} connectNulls />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
