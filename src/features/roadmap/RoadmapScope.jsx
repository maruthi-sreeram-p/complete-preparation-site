import { createContext, useContext, useEffect, useMemo } from 'react'
import { Outlet, useParams } from 'react-router-dom'
import { getRoadmap } from '@/lib/content/registry.js'
import { useProgressStore } from '@/features/progress/ProgressProvider.jsx'
import {
  computeStats,
  markStudied,
  pickContinueTarget,
  recentTopics,
  resetRoadmapProgress,
  setActiveRoadmap,
  setSubtopicStatus,
  setTopicStatus,
  statusOfSubtopic,
  statusOfTopic,
  subtopicProgress,
} from '@/lib/progress/state.js'
import NotFound from '@/components/layout/NotFound.jsx'

const RoadmapContext = createContext(null)

/**
 * Route layout for /r/:roadmapId. Resolves the roadmap and exposes it together
 * with its progress selectors and actions to every page below.
 */
export default function RoadmapScope() {
  const { roadmapId } = useParams()
  const roadmap = getRoadmap(roadmapId)
  const { state, update } = useProgressStore()
  const rp = roadmap ? state.roadmaps[roadmap.id] : undefined

  useEffect(() => {
    if (roadmap) update((s) => setActiveRoadmap(s, roadmap.id))
  }, [roadmap, update])

  const value = useMemo(() => {
    if (!roadmap) return null
    return {
      roadmap,
      statusOf: (topicId) => statusOfTopic(rp, topicId),
      subStatusOf: (topicId, subId) => statusOfSubtopic(rp, topicId, subId),
      subProgress: (topicId) => subtopicProgress(roadmap.topicsById[topicId], rp),
      lastStudiedAt: (topicId) => rp?.lastStudied[topicId],
      stats: computeStats(roadmap, rp),
      recent: recentTopics(roadmap, rp),
      continueTarget: pickContinueTarget(roadmap, rp),
      setTopicStatus: (topicId, status) => update((s) => setTopicStatus(s, roadmap, topicId, status)),
      setSubtopicStatus: (topicId, subId, status) =>
        update((s) => setSubtopicStatus(s, roadmap, topicId, subId, status)),
      markStudied: (topicId) => update((s) => markStudied(s, roadmap.id, topicId)),
      resetProgress: () => update((s) => resetRoadmapProgress(s, roadmap.id)),
    }
  }, [roadmap, rp, update])

  if (!value) return <NotFound message={`There is no roadmap called "${roadmapId}".`} />

  return (
    <RoadmapContext.Provider value={value}>
      <Outlet />
    </RoadmapContext.Provider>
  )
}

export function useRoadmapScope() {
  const ctx = useContext(RoadmapContext)
  if (!ctx) throw new Error('useRoadmapScope must be used inside <RoadmapScope>')
  return ctx
}
