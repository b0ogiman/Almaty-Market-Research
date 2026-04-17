import { BuildingStorefrontIcon, StarIcon, ArrowTrendingUpIcon, MapPinIcon } from "@heroicons/react/24/outline";

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

interface CardProps {
  label: string;
  value: string;
  sub?: string;
  icon: React.ReactNode;
  color: string;
  loading: boolean;
}

function StatCard({ label, value, sub, icon, color, loading }: CardProps) {
  return (
    <div className="card p-5 transition-all hover:border-slate-700/80">
      <div className="flex items-start justify-between">
        <p className="section-title">{label}</p>
        <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${color}`}>
          {icon}
        </div>
      </div>
      <p className="mt-4 text-3xl font-bold tracking-tight">
        {loading ? <span className="inline-block h-8 w-20 animate-pulse rounded-lg bg-slate-800" /> : value}
      </p>
      {sub && (
        <p className="mt-1 text-xs text-slate-500">
          {loading ? <span className="inline-block h-3 w-16 animate-pulse rounded bg-slate-800" /> : sub}
        </p>
      )}
    </div>
  );
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
};

function AnalysisSummaryCards({ loading, summary }: Props) {
  const sector = summary?.topSector ? (SECTOR_RU[summary.topSector] ?? summary.topSector) : "—";

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Заведений в базе"
        value={loading ? "…" : String(summary?.totalListings ?? 0)}
        sub="из 2GIS по Алматы"
        icon={<BuildingStorefrontIcon className="h-4 w-4" />}
        color="bg-primary-600/15 text-primary-400"
        loading={loading}
      />
      <StatCard
        label="Средний рейтинг"
        value={loading ? "…" : `★ ${(summary?.avgRating ?? 0).toFixed(1)}`}
        sub="по всем категориям"
        icon={<StarIcon className="h-4 w-4" />}
        color="bg-yellow-500/15 text-yellow-400"
        loading={loading}
      />
      <StatCard
        label="Тональность"
        value={loading ? "…" : `${Math.round((summary?.avgSentiment ?? 0.5) * 100)}%`}
        sub="положительных отзывов"
        icon={<ArrowTrendingUpIcon className="h-4 w-4" />}
        color="bg-accent-500/15 text-accent-400"
        loading={loading}
      />
      <div className="card p-5 transition-all hover:border-slate-700/80">
        <div className="flex items-start justify-between">
          <p className="section-title">Лучшая возможность</p>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-500/15 text-orange-400">
            <MapPinIcon className="h-4 w-4" />
          </div>
        </div>
        <p className="mt-4 text-xl font-bold tracking-tight">
          {loading ? <span className="inline-block h-7 w-28 animate-pulse rounded-lg bg-slate-800" /> : (summary?.topDistrict ?? "—")}
        </p>
        <p className="mt-1 text-xs text-slate-500">
          {loading ? <span className="inline-block h-3 w-20 animate-pulse rounded bg-slate-800" /> : sector}
        </p>
      </div>
    </div>
  );
}

export default AnalysisSummaryCards;
