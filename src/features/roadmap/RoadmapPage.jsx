import RoadmapCanvas from './RoadmapCanvas.jsx'
import { useRoadmapScope } from './RoadmapScope.jsx'
import DataIssues from '@/components/ui/DataIssues.jsx'

export default function RoadmapPage() {
  const { roadmap } = useRoadmapScope()
  return (
    <div className="relative h-[calc(100dvh-3.5rem)]">
      {roadmap.issues.length > 0 && (
        <div className="absolute inset-x-3 top-16 z-10 mx-auto max-w-2xl">
          <DataIssues issues={roadmap.issues} />
        </div>
      )}
      {roadmap.topics.length === 0 ? (
        <div className="grid h-full place-items-center text-sm text-muted">This roadmap has no topics yet.</div>
      ) : (
        <RoadmapCanvas key={roadmap.id} />
      )}
    </div>
  )
}
