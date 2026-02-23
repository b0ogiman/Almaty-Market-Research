import { Routes, Route, NavLink } from "react-router-dom";
import { ChartBarIcon, SparklesIcon } from "@heroicons/react/24/outline";
import DashboardPage from "./pages/DashboardPage";
import AnalysisPage from "./pages/AnalysisPage";

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-6 w-6 text-primary-500" />
            <div>
              <h1 className="text-lg font-semibold">
                Almaty Market Research
              </h1>
              <p className="text-xs text-slate-400">
                AI-powered local opportunity discovery
              </p>
            </div>
          </div>
          <nav className="flex gap-4 text-sm">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 ${
                  isActive
                    ? "bg-primary-600 text-white"
                    : "text-slate-300 hover:bg-slate-800"
                }`
              }
              end
            >
              Dashboard
            </NavLink>
            <NavLink
              to="/analysis"
              className={({ isActive }) =>
                `rounded-md px-3 py-1.5 ${
                  isActive
                    ? "bg-primary-600 text-white"
                    : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              Market Analysis
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
        </Routes>
      </main>
      <footer className="border-t border-slate-800 bg-slate-900/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 text-xs text-slate-500">
          <span>© {new Date().getFullYear()} Almaty Market Research</span>
          <span className="inline-flex items-center gap-1">
            <ChartBarIcon className="h-4 w-4" />
            FastAPI · React · PostgreSQL · Redis
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;

