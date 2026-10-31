/**
 * Practice state: which questions are done, the answers the learner wrote, and the extra
 * questions or links they added themselves. Everything here is a pure function of the state,
 * like lib/progress/state.js, so it can be tested without a browser and the storage can change.
 *
 * Shape:
 *   { v: 1,
 *     done:    { [questionId]: timestamp },
 *     answers: { [questionId]: string },          // free text or a SQL query
 *     custom:  { [subjectId]: [CustomItem] } }
 *
 * CustomItem: { id, title, platform, url, addedAt }
 */
export const PRACTICE_VERSION = 1

export const PLATFORMS = ['LeetCode', 'GeeksforGeeks', 'HackerRank', 'Codeforces', 'CodeChef', 'Other']

export const emptyPractice = () => ({ v: PRACTICE_VERSION, done: {}, answers: {}, custom: {} })

const isObject = (v) => v !== null && typeof v === 'object' && !Array.isArray(v)

/** Accepts whatever was stored and returns a valid state; never throws. */
export function sanitizePractice(raw) {
  if (!isObject(raw)) return emptyPractice()
  const out = emptyPractice()
  if (isObject(raw.done)) {
    for (const [id, at] of Object.entries(raw.done)) if (Number.isFinite(at)) out.done[id] = at
  }
  if (isObject(raw.answers)) {
    for (const [id, text] of Object.entries(raw.answers)) if (typeof text === 'string' && text !== '') out.answers[id] = text
  }
  if (isObject(raw.custom)) {
    for (const [subjectId, items] of Object.entries(raw.custom)) {
      if (!Array.isArray(items)) continue
      const clean = items.filter((i) => isObject(i) && typeof i.id === 'string' && typeof i.title === 'string' && typeof i.url === 'string')
      if (clean.length) out.custom[subjectId] = clean.map((i) => ({
        id: i.id,
        title: i.title,
        platform: PLATFORMS.includes(i.platform) ? i.platform : 'Other',
        url: i.url,
        addedAt: Number.isFinite(i.addedAt) ? i.addedAt : 0,
      }))
    }
  }
  return out
}

export const isDone = (state, questionId) => questionId in state.done

export function setDone(state, questionId, done, now = Date.now()) {
  const next = { ...state.done }
  if (done) next[questionId] = now
  else delete next[questionId]
  return { ...state, done: next }
}

/** An empty answer removes the entry so the stored state does not grow with blank boxes. */
export function setAnswer(state, questionId, text) {
  const next = { ...state.answers }
  if (text === '') delete next[questionId]
  else next[questionId] = text
  return { ...state, answers: next }
}

/**
 * Where "LeetCode problem 128" should go when the learner types a number instead of a URL.
 * Only a plain number is expanded; anything else is returned as typed.
 */
export function resolveLink(platform, input) {
  const text = String(input ?? '').trim()
  if (!text) return null
  if (/^https?:\/\//i.test(text)) return text
  if (/^\d+$/.test(text) && platform === 'LeetCode') return `https://leetcode.com/problemset/?search=${text}`
  // These two sites have no search address we can rely on, so a name becomes a web search limited to the site.
  const site = { GeeksforGeeks: 'geeksforgeeks.org', HackerRank: 'hackerrank.com' }[platform]
  if (site) return `https://www.google.com/search?q=${encodeURIComponent(`site:${site} ${text}`)}`
  if (platform === 'LeetCode') return `https://leetcode.com/problemset/?search=${encodeURIComponent(text)}`
  return null
}

/** @returns the new state, or the same state when the input does not make a usable item */
export function addCustom(state, subjectId, { title, platform, link }, id, now = Date.now()) {
  const url = resolveLink(platform, link)
  const typed = String(link ?? '').trim()
  const name = String(title ?? '').trim() || (/^\d+$/.test(typed) ? `${platform} #${typed}` : typed)
  if (!url || !name) return state
  const item = { id, title: name, platform: PLATFORMS.includes(platform) ? platform : 'Other', url, addedAt: now }
  return { ...state, custom: { ...state.custom, [subjectId]: [...(state.custom[subjectId] ?? []), item] } }
}

export function removeCustom(state, subjectId, itemId) {
  const items = (state.custom[subjectId] ?? []).filter((i) => i.id !== itemId)
  const custom = { ...state.custom }
  if (items.length) custom[subjectId] = items
  else delete custom[subjectId]
  const { [itemId]: _gone, ...done } = state.done
  return { ...state, custom, done }
}

/** Counts include the learner's own items, so adding a problem raises the total. */
export function subjectStats(subject, state) {
  const ids = [...subject.questions.map((q) => q.id), ...(state.custom[subject.id] ?? []).map((i) => i.id)]
  const done = ids.filter((id) => id in state.done).length
  return { total: ids.length, done, percent: ids.length ? Math.round((done / ids.length) * 100) : 0 }
}

export function overallStats(subjects, state) {
  let total = 0
  let done = 0
  for (const s of subjects) {
    const st = subjectStats(s, state)
    total += st.total
    done += st.done
  }
  return { total, done, percent: total ? Math.round((done / total) * 100) : 0 }
}
