import { useEffect, useState } from 'react'
import { loadTopicContent } from '@/lib/content/registry.js'
import { normalizeTopicContent } from '@/lib/content/normalize.js'

/** Loads and normalises a topic's content file. status: loading | ready | missing | error */
export function useTopicContent(roadmapId, topic) {
  const [result, setResult] = useState({ status: 'loading' })

  useEffect(() => {
    let alive = true
    setResult({ status: 'loading' })
    loadTopicContent(roadmapId, topic.contentId)
      .then((raw) => {
        if (!alive) return
        setResult(raw ? { status: 'ready', content: normalizeTopicContent(raw) } : { status: 'missing' })
      })
      .catch((error) => alive && setResult({ status: 'error', error }))
    return () => {
      alive = false
    }
  }, [roadmapId, topic.contentId])

  return result
}
