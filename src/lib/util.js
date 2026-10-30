export const cn = (...parts) => parts.filter(Boolean).join(' ')

const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

export function formatRelative(timestamp, now = Date.now()) {
  const seconds = Math.round((timestamp - now) / 1000)
  const abs = Math.abs(seconds)
  if (abs < 60) return 'just now'
  if (abs < 3600) return rtf.format(Math.round(seconds / 60), 'minute')
  if (abs < 86400) return rtf.format(Math.round(seconds / 3600), 'hour')
  return rtf.format(Math.round(seconds / 86400), 'day')
}

export const paths = {
  dashboard: (roadmapId) => `/r/${roadmapId}`,
  roadmap: (roadmapId) => `/r/${roadmapId}/roadmap`,
  topic: (roadmapId, topicId) => `/r/${roadmapId}/topics/${topicId}`,
}
