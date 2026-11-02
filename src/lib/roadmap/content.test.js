import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { buildRoadmap } from './model.js'

/** Builds every shipped roadmap with the app's own model: bad data would show up as issues in the UI. */
const ROOT = join(process.cwd(), 'content', 'roadmaps')
const ids = readdirSync(ROOT).filter((d) => existsSync(join(ROOT, d, 'roadmap.json')))

const load = (id) => {
  const raw = JSON.parse(readFileSync(join(ROOT, id, 'roadmap.json'), 'utf8'))
  const topicsDir = join(ROOT, id, 'topics')
  const contentIds = new Set(existsSync(topicsDir) ? readdirSync(topicsDir).map((f) => f.replace(/\.json$/, '')) : [])
  // a topic can show a page of another tree: contentId "<roadmapId>/<topicId>"
  for (const t of raw.topics ?? []) {
    if (t.contentId?.includes('/') && existsSync(join(ROOT, ...t.contentId.split('/').slice(0, 1), 'topics', `${t.contentId.split('/')[1]}.json`))) {
      contentIds.add(t.contentId)
    }
  }
  return { raw, roadmap: buildRoadmap(raw, { id, contentIds }) }
}

describe.each(ids)('roadmap %s', (id) => {
  it('has no data issues and every topic has a page', () => {
    const { roadmap } = load(id)
    expect(roadmap.issues, JSON.stringify(roadmap.issues)).toEqual([])
    const withoutPage = roadmap.topics.filter((t) => !t.hasContent && id !== 'aptitude').map((t) => t.id)
    expect(withoutPage).toEqual([])
  })
})

describe('DSA by topic', () => {
  const { roadmap } = load('dsa-topics')

  it('has the 18 NeetCode topics and its dependency edges', () => {
    expect(roadmap.topics).toHaveLength(18)
    expect(roadmap.edges).toHaveLength(22)
    expect(roadmap.sequence[0]).toBe('arrays-hashing')
    expect(roadmap.sequence.at(-1)).toBe('math-geometry')
  })

  it('follows the order NeetCode suggests', () => {
    const at = (id) => roadmap.sequence.indexOf(id)
    expect(roadmap.topicsById.trees.requires.sort()).toEqual(['binary-search', 'linked-list', 'sliding-window'])
    for (const [after, before] of [['trees', 'binary-search'], ['backtracking', 'trees'], ['graphs', 'backtracking'], ['dp-2d', 'dp-1d'], ['math-geometry', 'bit-manipulation']]) {
      expect(at(after), `${after} after ${before}`).toBeGreaterThan(at(before))
    }
  })

  it('has a practice subject for every topic, with the same problems', () => {
    const practice = join(process.cwd(), 'content', 'practice')
    for (const t of roadmap.topics) {
      const subject = JSON.parse(readFileSync(join(practice, `dsa-${t.id}.json`), 'utf8'))
      const page = JSON.parse(readFileSync(join(ROOT, 'dsa-topics', 'topics', `${t.id}.json`), 'utf8'))
      const table = JSON.stringify(page)
      for (const q of subject.questions) expect(table, `${t.id}: ${q.title}`).toContain(q.links[0].url)
    }
  })
})

describe('GATE CSE tree', () => {
  const { roadmap } = load('gate-cs')
  const topicFile = (id) => JSON.parse(readFileSync(join(ROOT, 'gate-cs', 'topics', `${id}.json`), 'utf8'))
  const questionsOf = (id) => topicFile(id).sections.flatMap((s) => s.blocks).filter((b) => b.type === 'mcq').flatMap((b) => b.items)
  const subjects = roadmap.topics.filter((t) => t.id !== 'gate-start')

  it('covers the 13 subject areas of the CS syllabus plus the start page', () => {
    expect(roadmap.topics).toHaveLength(14)
    expect(roadmap.sequence[0]).toBe('gate-start')
  })

  it('gives every subject at least 50 well-formed questions', () => {
    for (const t of subjects) {
      const items = questionsOf(t.id)
      expect(items.length, `${t.id}: number of questions`).toBeGreaterThanOrEqual(50)
      for (const [i, q] of items.entries()) {
        const where = `${t.id} question ${i + 1}`
        expect(q.o, `${where}: options`).toHaveLength(4)
        expect(new Set(q.o).size, `${where}: distinct options`).toBe(4)
        expect(Number.isInteger(q.a) && q.a >= 0 && q.a < 4, `${where}: answer index`).toBe(true)
        expect(q.w?.length, `${where}: explanation`).toBeGreaterThan(10)
      }
    }
  })

  it('does not always put the right answer in the same place', () => {
    for (const t of subjects) {
      const counts = [0, 1, 2, 3].map((k) => questionsOf(t.id).filter((q) => q.a === k).length)
      expect(Math.max(...counts) - Math.min(...counts), `${t.id}: answers per position ${counts}`).toBeLessThanOrEqual(2)
    }
  })

  it('has unique question-set ids so saved answers cannot collide', () => {
    const ids = subjects.map((t) => topicFile(t.id).sections.flatMap((s) => s.blocks).find((b) => b.type === 'mcq').id)
    expect(new Set(ids).size).toBe(ids.length)
  })
})

describe('Cybersecurity tree', () => {
  const { roadmap } = load('cybersecurity')
  const topicFile = (id) => JSON.parse(readFileSync(join(ROOT, 'cybersecurity', 'topics', `${id}.json`), 'utf8'))
  const questionsOf = (id) => topicFile(id).sections.flatMap((s) => s.blocks).filter((b) => b.type === 'mcq').flatMap((b) => b.items)

  it('has the 10 parts, starting from the foundations', () => {
    expect(roadmap.topics).toHaveLength(10)
    expect(roadmap.sequence[0]).toBe('cyber-start')
    expect(roadmap.sequence.at(-1)).toBe('cyber-career')
  })

  it('gives every part at least 50 well-formed questions', () => {
    for (const t of roadmap.topics) {
      const items = questionsOf(t.id)
      expect(items.length, `${t.id}: number of questions`).toBeGreaterThanOrEqual(50)
      for (const [i, q] of items.entries()) {
        const where = `${t.id} question ${i + 1}`
        expect(q.o, `${where}: options`).toHaveLength(4)
        expect(new Set(q.o).size, `${where}: distinct options`).toBe(4)
        expect(Number.isInteger(q.a) && q.a >= 0 && q.a < 4, `${where}: answer index`).toBe(true)
        expect(q.w?.length, `${where}: explanation`).toBeGreaterThan(10)
      }
    }
  })

  it('does not always put the right answer in the same place', () => {
    for (const t of roadmap.topics) {
      const counts = [0, 1, 2, 3].map((k) => questionsOf(t.id).filter((q) => q.a === k).length)
      expect(Math.max(...counts) - Math.min(...counts), `${t.id}: answers per position ${counts}`).toBeLessThanOrEqual(2)
    }
  })

  it('has unique question-set ids so saved answers cannot collide', () => {
    const ids = roadmap.topics.map((t) => topicFile(t.id).sections.flatMap((s) => s.blocks).find((b) => b.type === 'mcq').id)
    expect(new Set(ids).size).toBe(ids.length)
  })
})

describe('Core Subjects tree', () => {
  const { roadmap } = load('core-subjects')
  const java = load('interview-prep').roadmap
  const topicFile = (id) => JSON.parse(readFileSync(join(ROOT, 'core-subjects', 'topics', `${id}.json`), 'utf8'))
  const written = roadmap.topics.filter((t) => !t.contentId.includes('/'))
  const questionsOf = (id) => topicFile(id).sections.flatMap((s) => s.blocks).filter((b) => b.type === 'mcq').flatMap((b) => b.items)

  it('has the five subjects in the order they were asked for', () => {
    expect(roadmap.topics).toHaveLength(24)
    const stages = roadmap.sequence.map((id) => roadmap.topicsById[id].categoryId)
    expect([...new Set(stages)]).toEqual(['os', 'dbms', 'cn', 'coa', 'oop'])
  })

  it('shows the Java Full Stack guides for Operating Systems, Databases and Networks without copying them', () => {
    const reused = roadmap.topics.filter((t) => t.contentId.includes('/'))
    expect(reused).toHaveLength(14)
    for (const t of reused) {
      const [owner, source] = t.contentId.split('/')
      expect(owner).toBe('interview-prep')
      const original = java.topicsById[source]
      expect(original, `${t.id} -> ${t.contentId}`).toBeTruthy()
      expect(t.subtopics.map((s) => s.id)).toEqual(original.subtopics.map((s) => s.id))
      expect(existsSync(join(ROOT, 'core-subjects', 'topics', `${t.id}.json`)), `${t.id} must not be a copy`).toBe(false)
    }
  })

  it('writes Computer Organisation (6 parts) and OOP (4 parts) with well-formed questions', () => {
    expect(written.map((t) => t.categoryId).sort()).toEqual([...Array(6).fill('coa'), ...Array(4).fill('oop')].sort())
    for (const t of written) {
      const items = questionsOf(t.id)
      expect(items.length, `${t.id}: number of questions`).toBeGreaterThanOrEqual(15)
      for (const [i, q] of items.entries()) {
        const where = `${t.id} question ${i + 1}`
        expect(q.o, `${where}: options`).toHaveLength(4)
        expect(new Set(q.o).size, `${where}: distinct options`).toBe(4)
        expect(Number.isInteger(q.a) && q.a >= 0 && q.a < 4, `${where}: answer index`).toBe(true)
        expect(q.w?.length, `${where}: explanation`).toBeGreaterThan(10)
      }
    }
  })

  it('has unique question-set ids, so saved answers cannot collide with other trees', () => {
    const ids = written.map((t) => topicFile(t.id).sections.flatMap((s) => s.blocks).find((b) => b.type === 'mcq').id)
    expect(new Set(ids).size).toBe(ids.length)
    expect(ids.every((id) => id.startsWith('core-'))).toBe(true)
  })
})
