import { SparklesIcon, ArrowTrendingUpIcon, GlobeAltIcon } from "@heroicons/react/24/outline";

export interface AnalysisSummary {
  totalListings: number;
  avgRating: number;
  avgSentiment: number;
  topDistrict?: string;
  topSector?: string;
}

interface Props {
  loading: boolean;
  summary: AnalysisSummary | null;
}

function formatPct(value: number) {
  return `${(value * 100).toFixed(0)}%`;
}

function AnalysisSummaryCards({ loading, summary }: Props) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Listings analyzed
          </p>
          <GlobeAltIcon className="h-5 w-5 text-primary-500" />
        </div>
        <p className="mt-3 text-2xl font-semibold">
          {loading ? "…" : summary?.totalListings ?? 0}
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Avg. rating
          </p>
          <SparklesIcon className="h-5 w-5 text-yellow-400" />
        </div>
        <p className="mt-3 text-2xl font-semibold">
          {loading ? "…" : (summary?.avgRating ?? 0).toFixed(1)}
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Sentiment
          </p>
          <ArrowTrendingUpIcon className="h-5 w-5 text-emerald-400" />
        </div>
        <p className="mt-3 text-2xl font-semibold">
          {loading ? "…" : formatPct(summary?.avgSentiment ?? 0.5)}
        </p>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
          Top area
        </p>
        <p className="mt-3 text-sm font-medium">
          {loading
            ? "Loading…"
            : summary?.topDistrict || "Not enough data yet"}
        </p>
        <p className="mt-1 text-xs text-slate-400">
          Sector: {summary?.topSector || "Various"}
        </p>
      </div>
    </div>
  );
}

export default AnalysisSummaryCards;

