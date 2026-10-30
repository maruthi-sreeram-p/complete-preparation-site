import { describe, expect, it } from 'vitest'
import { ancestorsOf, buildRoadmap, descendantsOf } from './model.js'
import { computeLayout, NODE_SIZE } from './layout.js'

const raw = (topics, categories = [{ id: 'c', title: 'C' }]) => ({ title: 'T', categories, topics })
const t = (id, requires = [], extra = {}) => ({ id, title: id, category: 'c', requires, ...extra })
const build = (r) => buildRoadmap(r, { id: 'r' })

describe('buildRoadmap', () => {
  it('orders the learning sequence by dependencies, then by file order', () => {
    const r = build(raw([t('c', ['a', 'b']), t('b', ['a']), t('a'), t('d')]))
    expect(r.sequence).toEqual(['a', 'b', 'c', 'd'])
    expect(r.issues).toEqual([])
  })

  it('drops unknown, self and duplicate dependencies with warnings', () => {
    const r = build(raw([t('a', ['a', 'zzz']), t('b', ['a', 'a'])]))
    expect(r.topicsById.a.requires).toEqual([])
    expect(r.topicsById.b.requires).toEqual(['a'])
    expect(r.issues.filter((i) => i.level === 'warning')).toHaveLength(2)
  })

  it('breaks dependency cycles and reports an error', () => {
    const r = build(raw([t('a', ['c']), t('b', ['a']), t('c', ['b'])]))
    expect(r.sequence).toHaveLength(3)
    expect(r.issues.some((i) => i.level === 'error' && /cycle/i.test(i.message))).toBe(true)
  })

  it('ignores duplicate ids and falls back to an Uncategorized category', () => {
    const r = build(raw([t('a'), t('a'), { id: 'b', title: 'B', category: 'nope' }]))
    expect(r.topics.map((x) => x.id)).toEqual(['a', 'b'])
    expect(r.topicsById.b.categoryId).toBe('uncategorized')
    expect(r.categoryById.uncategorized).toBeDefined()
  })

  it('computes ancestors, descendants and unlocks', () => {
    const r = build(raw([t('a'), t('b', ['a']), t('c', ['b']), t('d', ['a'])]))
    expect([...ancestorsOf(r, 'c')].sort()).toEqual(['a', 'b'])
    expect([...descendantsOf(r, 'a')].sort()).toEqual(['b', 'c', 'd'])
    expect(r.unlocks.a).toEqual(['b', 'd'])
  })

  it('marks which topics have content', () => {
    const r = buildRoadmap(raw([t('a'), t('b', [], { contentId: 'custom' })]), {
      id: 'r',
      contentIds: new Set(['a', 'custom']),
    })
    expect(r.topicsById.a.hasContent).toBe(true)
    expect(r.topicsById.b.hasContent).toBe(true)
  })

  it('survives garbage input', () => {
    expect(() => build(null)).not.toThrow()
    expect(build({}).topics).toEqual([])
  })
})

describe('computeLayout', () => {
  it('places prerequisites above dependents and never overlaps nodes', () => {
    const topics = [t('a'), t('b'), t('c'), t('d', ['a', 'b']), t('e', ['c']), t('f', ['d', 'e']), t('g', ['a'])]
    const r = build(raw(topics))
    const { positions } = computeLayout(r)
    for (const edge of r.edges) expect(positions[edge.source].y).toBeLessThan(positions[edge.target].y)

    const byRow = {}
    for (const [id, p] of Object.entries(positions)) (byRow[p.y] ??= []).push({ id, x: p.x })
    for (const row of Object.values(byRow)) {
      row.sort((p, q) => p.x - q.x)
      for (let i = 1; i < row.length; i++) expect(row[i].x - row[i - 1].x).toBeGreaterThanOrEqual(NODE_SIZE.width)
    }
  })

  it('wraps very wide layers into several rows', () => {
    const r = build(raw(Array.from({ length: 14 }, (_, i) => t(`n${i}`))))
    const rows = new Set(Object.values(computeLayout(r).positions).map((p) => p.y))
    expect(rows.size).toBeGreaterThan(1)
  })

  it('tree layout centres each level on one spine and puts a heading at each new stage', () => {
    const cats = [{ id: 'c', title: 'C' }, { id: 'd', title: 'D' }]
    const list = [t('a'), t('b', ['a']), t('e', ['a']), t('f', ['b', 'e'])]
    list.push({ id: 'm', title: 'm', category: 'd', requires: ['f'] })
    const r = buildRoadmap({ layout: 'tree', categories: cats, topics: list }, { id: 'r' })
    const { positions, stages } = computeLayout(r)
    expect(r.sequence).toEqual(['a', 'b', 'e', 'f', 'm'])
    expect(stages.map((s) => s.categoryId)).toEqual(['c', 'd'])
    expect(positions.b.y).toBe(positions.e.y)
    expect(positions.b.y).toBeGreaterThan(positions.a.y)
    expect(positions.a.x + NODE_SIZE.width / 2).toBe(0)
    expect((positions.b.x + positions.e.x + NODE_SIZE.width) / 2).toBe(0)
    expect(stages[1].y).toBeGreaterThan(positions.f.y)
    expect(positions.m.y).toBeGreaterThan(stages[1].y)
  })

  it('respects explicit positions', () => {
    const r = build(raw([t('a', [], { position: { x: 5, y: 7 } })]))
    expect(computeLayout(r).positions.a).toEqual({ x: 5, y: 7 })
  })
})
