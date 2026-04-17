import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Cell,
} from "recharts";
import type { AnalysisSummary } from "./AnalysisSummaryCards";
import type { DistrictChartRow } from "../store/dashboardStore";

interface Props {
  loading: boolean;
  summary: AnalysisSummary | null;
  districtChartData: DistrictChartRow[];
}

const SCORE_COLORS = ["#8b5cf6", "#7c3aed", "#6d28d9", "#5b21b6", "#4c1d95", "#3b0764", "#a78bfa", "#c4b5fd"];

function EmptyState({ text }: { text: string }) {
  return (
    <div className="flex h-full items-center justify-center text-xs text-slate-600">{text}</div>
  );
}

function DemandCompetitionCharts({ loading, districtChartData }: Props) {
  const hasData = districtChartData.length > 0;

  return (
    <div className="space-y-4">
      <div className="card p-5">
        <div className="mb-4">
          <h3 className="font-semibold text-slate-100">Спрос и конкуренция по районам</h3>
          <p className="text-xs text-slate-500 mt-0.5">На основе проведённых анализов</p>
        </div>
        <div className="h-60">
          {loading ? (
            <div className="h-full animate-pulse rounded-xl bg-slate-800/40" />
          ) : !hasData ? (
            <EmptyState text="Запустите анализ по нескольким районам, чтобы увидеть данные" />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={districtChartData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis
                  dataKey="district"
                  stroke="#475569"
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={[0, 1]}
                  stroke="#475569"
                  tick={{ fontSize: 11, fill: "#64748b" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${Math.round(v * 100)}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#1e293b",
                    borderRadius: "12px",
                    fontSize: 12,
                    boxShadow: "0 4px 24px rgba(0,0,0,0.4)",
                  }}
                  formatter={(v: number, name: string) => [
                    `${Math.round(v * 100)}%`,
                    name === "demand" ? "Спрос" : "Конкуренция",
                  ]}
                />
                <Legend
                  formatter={(v) => (v === "demand" ? "Спрос" : "Конкуренция")}
                  wrapperStyle={{ fontSize: 11, paddingTop: 8 }}
                />
                <Bar dataKey="demand" name="demand" fill="#10b981" radius={[6, 6, 0, 0]} />
                <Bar dataKey="competition" name="competition" fill="#f97316" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card p-5">
        <div className="mb-4">
          <h3 className="font-semibold text-slate-100">Итоговый балл по районам</h3>
          <p className="text-xs text-slate-500 mt-0.5">Чем выше — тем выгоднее входить</p>
        </div>
        <div className="h-44">
          {loading ? (
            <div className="h-full animate-pulse rounded-xl bg-slate-800/40" />
          ) : !hasData ? (
            <EmptyState text="Нет данных" />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={districtChartData}
                layout="vertical"
                margin={{ top: 0, right: 16, left: 8, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis
                  type="number"
                  domain={[0, 1]}
                  stroke="#475569"
                  tick={{ fontSize: 11, fill: "#64748b" }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${Math.round(v * 100)}`}
                />
                <YAxis
                  type="category"
                  dataKey="district"
                  stroke="#475569"
                  tick={{ fontSize: 11, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                  width={72}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#1e293b",
                    borderRadius: "12px",
                    fontSize: 12,
                    boxShadow: "0 4px 24px rgba(0,0,0,0.4)",
                  }}
                  formatter={(v: number) => [`${Math.round(v * 100)}`, "Балл"]}
                />
                <Bar dataKey="score" name="score" radius={[0, 6, 6, 0]}>
                  {districtChartData.map((_, i) => (
                    <Cell key={i} fill={SCORE_COLORS[i % SCORE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}

export default DemandCompetitionCharts;
