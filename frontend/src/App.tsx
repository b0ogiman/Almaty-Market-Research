import { Routes, Route, NavLink } from "react-router-dom";
import { ChartBarIcon, MagnifyingGlassIcon, HomeIcon } from "@heroicons/react/24/outline";
import { SparklesIcon } from "@heroicons/react/24/solid";
import DashboardPage from "./pages/DashboardPage";
import AnalysisPage from "./pages/AnalysisPage";

function App() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-50 border-b border-slate-800/60 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-600/20 ring-1 ring-primary-500/30">
              <SparklesIcon className="h-5 w-5 text-primary-400" />
            </div>
            <div>
              <h1 className="bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-base font-bold text-transparent">
                Рынок Алматы
              </h1>
              <p className="text-[11px] text-slate-500">AI-аналитика бизнес-возможностей</p>
            </div>
          </div>

          <nav className="flex items-center gap-1">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-primary-600/20 text-primary-300 ring-1 ring-primary-500/30"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`
              }
            >
              <HomeIcon className="h-4 w-4" />
              Дашборд
            </NavLink>
            <NavLink
              to="/analysis"
              className={({ isActive }) =>
                `flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-primary-600/20 text-primary-300 ring-1 ring-primary-500/30"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`
              }
            >
              <MagnifyingGlassIcon className="h-4 w-4" />
              Анализ рынка
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
        </Routes>
      </main>

      <footer className="mt-12 border-t border-slate-800/60 bg-slate-950/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 text-xs text-slate-600">
          <span>© {new Date().getFullYear()} Рынок Алматы</span>
          <span className="flex items-center gap-1.5">
            <ChartBarIcon className="h-3.5 w-3.5" />
            FastAPI · React · PostgreSQL · 2GIS
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
