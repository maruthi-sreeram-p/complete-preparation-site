import { Link, NavLink, matchPath, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Waypoints } from 'lucide-react'
import { APP_NAME } from '@/config.js'
import { getRoadmap, listRoadmaps } from '@/lib/content/registry.js'
import { computeStats } from '@/lib/progress/state.js'
import { useProgressStore } from '@/features/progress/ProgressProvider.jsx'
import { cn, paths } from '@/lib/util.js'

const navClass = ({ isActive }) =>
  cn(
    'inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-sm transition-colors',
    isActive ? 'bg-panel-2 text-ink' : 'text-muted hover:text-ink',
  )

export default function Header() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { state } = useProgressStore()
  const roadmaps = listRoadmaps()

  const roadmapId = matchPath('/r/:roadmapId/*', pathname)?.params.roadmapId
  const roadmap = roadmapId ? getRoadmap(roadmapId) : null
  const percent = roadmap ? computeStats(roadmap, state.roadmaps[roadmap.id]).percent : null

  return (
    <header className="sticky top-0 z-30 h-14 border-b border-line bg-canvas">
      <div className="flex h-full w-full items-center gap-3 px-4 lg:px-6">
        <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="grid size-7 place-items-center rounded-lg bg-linear-to-br from-accent to-accent-2">
            <Waypoints size={16} className="text-canvas" />
          </span>
          <span className="hidden sm:inline">{APP_NAME}</span>
        </Link>

        {roadmap && (
          <>
            {roadmaps.length > 1 && (
              <select
                value={roadmap.id}
                onChange={(e) => navigate(paths.dashboard(e.target.value))}
                aria-label="Roadmap"
                className="max-w-40 truncate rounded-lg border border-line bg-panel px-2 py-1.5 text-sm text-muted"
              >
                {roadmaps.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title}
                  </option>
                ))}
              </select>
            )}
            <nav className="ml-1 flex items-center gap-1" aria-label="Main">
              <NavLink to={paths.roadmap(roadmap.id)} className={navClass}>
                <Waypoints size={15} /> Roadmap
              </NavLink>
              <NavLink to={paths.dashboard(roadmap.id)} end className={navClass}>
                <LayoutDashboard size={15} /> Dashboard
              </NavLink>
            </nav>
            <Link
              to={paths.dashboard(roadmap.id)}
              className="ml-auto flex items-center gap-2 text-xs text-muted hover:text-ink"
              title="Overall completion"
            >
              <span className="hidden sm:inline">Overall</span>
              <span className="w-16 overflow-hidden rounded-full bg-line">
                <span
                  className="block h-1.5 rounded-full bg-linear-to-r from-accent to-accent-2"
                  style={{ width: `${percent}%` }}
                />
              </span>
              <span className="w-8 tabular-nums">{percent}%</span>
            </Link>
          </>
        )}
      </div>
    </header>
  )
}
