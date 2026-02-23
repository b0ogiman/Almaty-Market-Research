import { SparklesIcon } from "@heroicons/react/24/outline";

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

function OpportunityList({ loading, opportunities }: Props) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-100">
          Top opportunities
        </h3>
        <SparklesIcon className="h-5 w-5 text-primary-500" />
      </div>
      <p className="mt-1 text-xs text-slate-400">
        Ranked by demand, competition, and sentiment.
      </p>
      <div className="mt-3 space-y-2">
        {loading && (
          <div className="text-xs text-slate-500">Loading opportunities…</div>
        )}
        {!loading && opportunities.length === 0 && (
          <div className="text-xs text-slate-500">
            No opportunities yet. Run a market analysis first.
          </div>
        )}
        {opportunities.map((o) => (
          <div
            key={o.id}
            className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-xs"
          >
            <div className="flex items-center justify-between">
              <span className="font-medium text-slate-100 truncate">
                {o.name}
              </span>
              <span className="rounded-full bg-primary-500/10 px-2 py-0.5 text-[10px] font-semibold text-primary-400">
                {(o.score * 100).toFixed(0)}
              </span>
            </div>
            <div className="mt-1 flex justify-between text-[11px] text-slate-400">
              <span>{o.district}</span>
              <span>{o.sector}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default OpportunityList;

