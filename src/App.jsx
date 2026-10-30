import { Navigate, Route, Routes } from 'react-router-dom'
import AppShell from '@/components/layout/AppShell.jsx'
import NotFound from '@/components/layout/NotFound.jsx'
import RoadmapScope from '@/features/roadmap/RoadmapScope.jsx'
import DashboardPage from '@/features/dashboard/DashboardPage.jsx'
import RoadmapPage from '@/features/roadmap/RoadmapPage.jsx'
import TopicPage from '@/features/topic/TopicPage.jsx'
import { listRoadmaps } from '@/lib/content/registry.js'
import { useProgressStore } from '@/features/progress/ProgressProvider.jsx'
import { paths } from '@/lib/util.js'

function RootRedirect() {
  const { state } = useProgressStore()
  const roadmaps = listRoadmaps()
  if (roadmaps.length === 0) {
    return (
      <div className="mx-auto max-w-lg px-4 py-24 text-center">
        <h1 className="text-xl font-semibold">No roadmap found</h1>
        <p className="mt-2 text-sm text-muted">
          Add <code className="rounded bg-panel-2 px-1.5 py-0.5 font-mono text-xs">content/roadmaps/&lt;id&gt;/roadmap.json</code>{' '}
          to get started. See <code className="rounded bg-panel-2 px-1.5 py-0.5 font-mono text-xs">content/README.md</code>.
        </p>
      </div>
    )
  }
  const target = roadmaps.find((r) => r.id === state.activeRoadmapId) ?? roadmaps[0]
  return <Navigate to={paths.dashboard(target.id)} replace />
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<RootRedirect />} />
        <Route path="r/:roadmapId" element={<RoadmapScope />}>
          <Route index element={<DashboardPage />} />
          <Route path="roadmap" element={<RoadmapPage />} />
          <Route path="topics/:topicId" element={<TopicPage />} />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
