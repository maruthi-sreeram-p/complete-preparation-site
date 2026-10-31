import { readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll, describe, expect, it } from 'vitest'
import initSqlJs from 'sql.js'
import { runQuery } from './sql.js'

/**
 * Checks the shipped practice content: every subject is well formed, ids are unique (answers are saved under
 * them), every coding question links to a real https page, and every SQL reference solution runs on its dataset
 * and returns what the question describes.
 */
const DIR = join(process.cwd(), 'content', 'practice')
const subjects = readdirSync(DIR)
  .filter((f) => f.endsWith('.json'))
  .map((f) => JSON.parse(readFileSync(join(DIR, f), 'utf8')))

const LEVELS = ['Easy', 'Medium', 'Hard']

describe('practice subjects', () => {
  it('has the expected subjects', () => {
    const ids = subjects.map((s) => s.id)
    for (const id of ['databases', 'core-java', 'spring-boot', 'kafka', 'system-design', 'dsa-arrays-hashing', 'dsa-math-geometry']) {
      expect(ids).toContain(id)
    }
    expect(subjects.filter((s) => s.id.startsWith('dsa-'))).toHaveLength(18)
  })

  it('uses unique subject and question ids', () => {
    const subjectIds = subjects.map((s) => s.id)
    expect(new Set(subjectIds).size).toBe(subjectIds.length)
    const questionIds = subjects.flatMap((s) => s.questions.map((q) => q.id))
    expect(new Set(questionIds).size).toBe(questionIds.length)
  })

  it.each(subjects.map((s) => [s.id, s]))('%s: every question is complete', (_id, subject) => {
    expect(subject.title && subject.group && subject.description).toBeTruthy()
    for (const p of subject.platforms ?? []) expect(p.url).toMatch(/^https:\/\//)
    expect(subject.questions.length).toBeGreaterThan(0)
    for (const q of subject.questions) {
      expect(q.id && q.title, `question in ${subject.id}`).toBeTruthy()
      if (q.level) expect(LEVELS).toContain(q.level)
      if (q.type === 'written') expect(q.answer, q.id).toBeTruthy()
      if (q.type === 'sql') {
        expect(subject.dataset?.sql, `${q.id} needs a dataset`).toBeTruthy()
        expect(q.solution, q.id).toBeTruthy()
      }
      if (q.type === 'coding') {
        expect(q.links?.length, q.id).toBeGreaterThan(0)
        for (const l of q.links) expect(l.url, q.id).toMatch(/^https:\/\/leetcode\.com\/problems\/[a-z0-9-]+\/$/)
      }
    }
  })
})

describe('SQL reference solutions', () => {
  let SQL
  beforeAll(async () => {
    SQL = await initSqlJs()
  })

  const db = subjects.find((s) => s.id === 'databases')
  const sqlQuestions = db.questions.filter((q) => q.type === 'sql')
  const byId = (id) => sqlQuestions.find((q) => q.id === id)
  const rows = (id) => {
    const r = runQuery(SQL, db.dataset.sql, byId(id).solution)
    expect(r.ok, `${id}: ${r.error}`).toBe(true)
    return r.rows
  }

  it('all run and return at least one row', () => {
    expect(sqlQuestions.length).toBeGreaterThanOrEqual(15)
    for (const q of sqlQuestions) {
      const r = runQuery(SQL, db.dataset.sql, q.solution)
      expect(r.ok, `${q.id}: ${r.error}`).toBe(true)
      expect(r.rows.length, q.id).toBeGreaterThan(0)
    }
  })

  // The expected results were worked out by hand from the data when the questions were written.
  it('return the results the questions describe', () => {
    expect(rows('db-sql-india')).toEqual([['Asha Rao', 'Bengaluru'], ['Chitra Iyer', 'Chennai'], ['Farhan Ali', 'Hyderabad'], ['Isha Nair', 'Kochi']])
    expect(rows('db-sql-top3').map((r) => r[0])).toEqual(['Standing Desk', 'Ergonomic Chair', 'Noise-Cancelling Headphones'])
    expect(rows('db-sql-null-city')).toEqual([['Emma Stone']])
    expect(rows('db-sql-per-country')).toEqual([['India', 4], ['UK', 2], ['USA', 2]])
    expect(rows('db-sql-status-count')).toEqual([['delivered', 9], ['cancelled', 2], ['shipped', 2], ['pending', 1]])
    expect(rows('db-sql-order-totals')).toHaveLength(12)
    expect(rows('db-sql-order-totals')[0]).toEqual([13, 368])
    expect(rows('db-sql-never-ordered')).toEqual([['Emma Stone'], ['Hiro Tanaka'], ['Jack Brown']])
    expect(rows('db-sql-category-revenue')).toEqual([['Electronics', 799.5], ['Furniture', 392]])
    expect(rows('db-sql-top-spender')).toEqual([['Grace Lee', 502]])
    expect(rows('db-sql-self-join')).toEqual([['Priya Nair'], ['Vikram Das']])
    expect(rows('db-sql-above-avg')).toEqual([
      ['Meera Joshi', 'Engineering', 250000], ['Vikram Das', 'Engineering', 190000], ['Tara Bose', 'HR', 110000], ['Kabir Singh', 'Sales', 150000],
    ])
    expect(rows('db-sql-second-highest')).toEqual([[190000]])
    expect(rows('db-sql-top2-per-dept').map((r) => r[0])).toEqual(['Meera Joshi', 'Vikram Das', 'Tara Bose', 'Anita Pillai', 'Kabir Singh', 'Divya Reddy', 'Nikhil Shah'])
    expect(rows('db-sql-running-total')).toEqual([['2024-07', 347, 347], ['2024-08', 477, 824], ['2024-09', 312.5, 1136.5], ['2024-10', 368, 1504.5]])
    expect(rows('db-sql-mom-change')).toEqual([['2024-07', 347, null], ['2024-08', 477, 130], ['2024-09', 312.5, -164.5], ['2024-10', 368, 55.5]])
    expect(rows('db-sql-all-categories')).toEqual([['Chitra Iyer']])
  })
})
