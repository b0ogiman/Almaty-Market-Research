import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Legend,
  CartesianGrid
} from "recharts";
import type { AnalysisSummary } from "./AnalysisSummaryCards";

interface Props {
  loading: boolean;
  summary: AnalysisSummary | null;
}

const sampleTrend = Array.from({ length: 6 }).map((_, idx) => ({
  label: `T${idx + 1}`,
  demand: 0.4 + idx * 0.06,
  competition: 0.7 - idx * 0.05
}));

const sampleDistricts = [
  { district: "Bostandyk", demand: 0.8, competition: 0.5 },
  { district: "Almaly", demand: 0.7, competition: 0.6 },
  { district: "Medey", demand: 0.6, competition: 0.4 }
];

function DemandCompetitionCharts({ loading }: Props) {
  const trendData = loading ? sampleTrend : sampleTrend;
  const districtData = loading ? sampleDistricts : sampleDistricts;

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <h3 className="text-sm font-medium text-slate-100">
          Demand vs competition trend
        </h3>
        <p className="text-xs text-slate-400">
          Illustrative moving average of demand and competition over time.
        </p>
        <div className="mt-3 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="label" stroke="#64748b" />
              <YAxis domain={[0, 1]} stroke="#64748b" />
              <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b" }} />
              <Legend />
              <Line
                type="monotone"
                dataKey="demand"
                name="Demand"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="competition"
                name="Competition"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <h3 className="text-sm font-medium text-slate-100">
          District demand vs competition
        </h3>
        <div className="mt-3 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={districtData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="district" stroke="#64748b" />
              <YAxis domain={[0, 1]} stroke="#64748b" />
              <Tooltip contentStyle={{ backgroundColor: "#020617", borderColor: "#1e293b" }} />
              <Legend />
              <Bar dataKey="demand" name="Demand" fill="#22c55e" radius={[4, 4, 0, 0]} />
              <Bar dataKey="competition" name="Competition" fill="#f97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default DemandCompetitionCharts;

