import { describe, expect, it } from 'vitest'
import { buildRoadmap } from '../roadmap/model.js'
import { STATUS } from './status.js'
import {
  computeStats,
  emptyProgress,
  markStudied,
  pickContinueTarget,
  recentTopics,
  sanitizeProgress,
  setSubtopicStatus,
  setTopicStatus,
  statusOfTopic,
} from './state.js'

const roadmap = buildRoadmap(
  {
    categories: [{ id: 'c1', title: 'One' }, { id: 'c2', title: 'Two' }],
    topics: [
      { id: 'a', title: 'A', category: 'c1', subtopics: [{ id: 'x', title: 'X' }, { id: 'y', title: 'Y' }] },
      { id: 'b', title: 'B', category: 'c1', requires: ['a'] },
      { id: 'c', title: 'C', category: 'c2', requires: ['b'] },
    ],
  },
  { id: 'r' },
)
const rp = (state) => state.roadmaps.r

describe('topic and subtopic status', () => {
  it('completing a topic completes its subtopics; resetting clears them', () => {
    let s = setTopicStatus(emptyProgress(), roadmap, 'a', STATUS.COMPLETED, 1)
    expect(Object.keys(rp(s).subtopics)).toEqual(['a/x', 'a/y'])
    s = setTopicStatus(s, roadmap, 'a', STATUS.NOT_STARTED, 2)
    expect(rp(s).topics).toEqual({})
    expect(rp(s).subtopics).toEqual({})
  })

  it('subtopic progress moves the parent topic along', () => {
    let s = setSubtopicStatus(emptyProgress(), roadmap, 'a', 'x', STATUS.COMPLETED, 1)
    expect(statusOfTopic(rp(s), 'a')).toBe(STATUS.IN_PROGRESS)
    s = setSubtopicStatus(s, roadmap, 'a', 'y', STATUS.COMPLETED, 2)
    expect(statusOfTopic(rp(s), 'a')).toBe(STATUS.COMPLETED)
    s = setSubtopicStatus(s, roadmap, 'a', 'y', STATUS.NOT_STARTED, 3)
    expect(statusOfTopic(rp(s), 'a')).toBe(STATUS.IN_PROGRESS)
  })

  it('does not mutate previous state and ignores unknown ids', () => {
    const before = emptyProgress()
    const after = setTopicStatus(before, roadmap, 'a', STATUS.IN_PROGRESS, 1)
    expect(before.roadmaps).toEqual({})
    expect(after).not.toBe(before)
    expect(setTopicStatus(before, roadmap, 'nope', STATUS.COMPLETED)).toBe(before)
    expect(setSubtopicStatus(before, roadmap, 'a', 'nope', STATUS.COMPLETED)).toBe(before)
  })
})

describe('stats and continue learning', () => {
  it('computes overall and per-category numbers', () => {
    let s = setTopicStatus(emptyProgress(), roadmap, 'a', STATUS.COMPLETED, 1)
    s = setTopicStatus(s, roadmap, 'b', STATUS.IN_PROGRESS, 2)
    const stats = computeStats(roadmap, rp(s))
    expect(stats).toMatchObject({ total: 3, completed: 1, inProgress: 1, notStarted: 1, percent: 33 })
    expect(stats.subtopics).toEqual({ done: 2, total: 2 })
    expect(stats.byCategory.map((c) => [c.category.id, c.completed, c.total])).toEqual([['c1', 1, 2], ['c2', 0, 1]])
  })

  it('starts at the first ready topic, then resumes the latest unfinished one', () => {
    expect(pickContinueTarget(roadmap, undefined)).toMatchObject({ topic: { id: 'a' }, reason: 'next' })

    let s = setTopicStatus(emptyProgress(), roadmap, 'a', STATUS.COMPLETED, 1)
    expect(pickContinueTarget(roadmap, rp(s))).toMatchObject({ topic: { id: 'b' }, reason: 'next' })

    s = markStudied(s, 'r', 'c', 10)
    expect(pickContinueTarget(roadmap, rp(s))).toMatchObject({ topic: { id: 'c' }, reason: 'resume' })
  })

  it('returns null when everything is complete, and lists recent topics newest first', () => {
    let s = emptyProgress()
    for (const [i, id] of ['a', 'b', 'c'].entries()) s = setTopicStatus(s, roadmap, id, STATUS.COMPLETED, i + 1)
    expect(pickContinueTarget(roadmap, rp(s))).toBeNull()
    expect(recentTopics(roadmap, rp(s)).map((t) => t.id)).toEqual(['c', 'b', 'a'])
  })
})

describe('sanitizeProgress', () => {
  it('rejects unknown versions and corrupt entries', () => {
    expect(sanitizeProgress({ version: 99 })).toEqual(emptyProgress())
    expect(sanitizeProgress('garbage')).toEqual(emptyProgress())
    const cleaned = sanitizeProgress({
      version: 1,
      activeRoadmapId: 5,
      roadmaps: { r: { topics: { a: { status: 'bogus' }, b: { status: 'completed', updatedAt: 3 } } } },
    })
    expect(cleaned.activeRoadmapId).toBeNull()
    expect(cleaned.roadmaps.r.topics).toEqual({ b: { status: 'completed', updatedAt: 3 } })
  })
})
