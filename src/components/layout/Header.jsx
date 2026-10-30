import { Link, NavLink, matchPath, useLocation, useNavigate } from 'react-router-dom'
import { House, LayoutDashboard, Waypoints } from 'lucide-react'
import { APP_NAME, APP_NAME_PARTS } from '@/config.js'
import { getRoadmap, listRoadmaps } from '@/lib/content/registry.js'
import { computeStats } from '@/lib/progress/state.js'
import { useProgressStore } from '@/features/progress/ProgressProvider.jsx'
import { ThemeToggle } from '@/features/theme/ThemeProvider.jsx'
import { cn, paths } from '@/lib/util.js'

const navClass = (active) =>
  cn(
    'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1.5 text-sm font-medium transition-colors sm:px-3.5',
    active
      ? 'bg-linear-to-r from-accent to-accent-2 text-white shadow-sm'
      : 'text-muted hover:bg-panel-2 hover:text-ink',
  )

export default function Header() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { state } = useProgressStore()
  const roadmaps = listRoadmaps()

  const roadmapId = matchPath('/r/:roadmapId/*', pathname)?.params.roadmapId
  const roadmap = roadmapId
    ? getRoadmap(roadmapId)
    : (roadmaps.find((r) => r.id === state.activeRoadmapId) ?? roadmaps[0] ?? null)
  const percent = roadmap ? computeStats(roadmap, state.roadmaps[roadmap.id]).percent : null
  // a topic page is a step of the roadmap, so Roadmap stays highlighted there
  const onTopic = Boolean(matchPath('/r/:roadmapId/topics/:topicId', pathname))

  return (
    <header className="sticky top-0 z-30 h-14 border-b border-line bg-canvas">
      {/* equal outer columns keep the nav in the true centre of the screen */}
      <div className="grid h-full w-full grid-cols-[1fr_auto_1fr] items-center gap-3 px-4 lg:px-6">
        <div className="flex min-w-0 items-center gap-3">
          <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
            <span className="logo-mark size-7 shrink-0" aria-hidden="true" />
            <span className="hidden text-lg font-bold sm:inline" aria-label={APP_NAME}>
              {APP_NAME_PARTS[0]}
              <span className="bg-linear-to-r from-accent to-accent-2 bg-clip-text text-transparent">
                {APP_NAME_PARTS[1]}
              </span>
            </span>
          </Link>
          {roadmap && roadmaps.length > 1 && (
            <select
              value={roadmap.id}
              onChange={(e) => navigate(paths.dashboard(e.target.value))}
              aria-label="Roadmap"
              className="hidden max-w-40 truncate rounded-lg border border-line bg-panel px-2 py-1.5 text-sm text-muted lg:block"
            >
              {roadmaps.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title}
                </option>
              ))}
            </select>
          )}
        </div>

        {roadmap ? (
          <nav className="flex items-center gap-1 rounded-full border border-line bg-panel p-1" aria-label="Main">
            <NavLink to="/" end className={({ isActive }) => navClass(isActive)}>
              <House size={15} /> <span className="hidden sm:inline">Home</span>
            </NavLink>
            <NavLink to={paths.roadmap(roadmap.id)} className={({ isActive }) => navClass(isActive || onTopic)}>
              <Waypoints size={15} /> <span className="hidden sm:inline">Roadmap</span>
            </NavLink>
            <NavLink to={paths.dashboard(roadmap.id)} end className={({ isActive }) => navClass(isActive)}>
              <LayoutDashboard size={15} /> <span className="hidden sm:inline">Dashboard</span>
            </NavLink>
          </nav>
        ) : (
          <span />
        )}

        <div className="flex items-center justify-end gap-3">
          {roadmap && (
            <Link
              to={paths.dashboard(roadmap.id)}
              className="hidden items-center gap-2 text-xs text-muted hover:text-ink md:flex"
              title="Overall completion"
            >
              <span className="w-16 overflow-hidden rounded-full bg-line">
                <span
                  className="block h-1.5 rounded-full bg-linear-to-r from-accent to-accent-2"
                  style={{ width: `${percent}%` }}
                />
              </span>
              <span className="tabular-nums">{percent}%</span>
            </Link>
          )}
          <ThemeToggle className="rounded-full" />
        </div>
      </div>
    </header>
  )
}
