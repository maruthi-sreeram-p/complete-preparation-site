import { beforeAll, describe, expect, it } from 'vitest'
import initSqlJs from 'sql.js'
import { checkAnswer, compareResults, runQuery } from './sql.js'

const DATA = `
CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT, score REAL);
INSERT INTO t VALUES (1,'a',1.5),(2,'b',2.5),(3,'c',NULL);`

let SQL
beforeAll(async () => {
  SQL = await initSqlJs()
})

describe('runQuery', () => {
  it('returns columns and rows of the last statement', () => {
    const r = runQuery(SQL, DATA, 'SELECT name FROM t ORDER BY id')
    expect(r).toEqual({ ok: true, columns: ['name'], rows: [['a'], ['b'], ['c']] })
  })

  it('reports SQL errors instead of throwing', () => {
    const r = runQuery(SQL, DATA, 'SELEC 1')
    expect(r.ok).toBe(false)
    expect(r.error).toMatch(/syntax error/i)
  })

  it('starts every run from fresh data', () => {
    runQuery(SQL, DATA, 'DELETE FROM t')
    expect(runQuery(SQL, DATA, 'SELECT COUNT(*) FROM t').rows).toEqual([[3]])
  })

  it('supports window functions and CTEs', () => {
    const r = runQuery(SQL, DATA, 'WITH x AS (SELECT id, ROW_NUMBER() OVER (ORDER BY id DESC) AS rn FROM t) SELECT id FROM x WHERE rn = 1')
    expect(r.rows).toEqual([[3]])
  })
})

describe('compareResults', () => {
  const base = { columns: ['a', 'b'], rows: [[1, 'x'], [2, 'y']] }

  it('ignores column names and, by default, row order', () => {
    expect(compareResults({ columns: ['p', 'q'], rows: [[2, 'y'], [1, 'x']] }, base).match).toBe(true)
  })

  it('treats 0.1 + 0.2 and 0.3 as equal', () => {
    expect(compareResults({ columns: ['v'], rows: [[0.1 + 0.2]] }, { columns: ['v'], rows: [[0.3]] }).match).toBe(true)
  })

  it('distinguishes NULL from an empty string and from zero', () => {
    expect(compareResults({ columns: ['v'], rows: [[null]] }, { columns: ['v'], rows: [['']] }).match).toBe(false)
    expect(compareResults({ columns: ['v'], rows: [[null]] }, { columns: ['v'], rows: [[0]] }).match).toBe(false)
  })

  it('explains column and row count mismatches', () => {
    expect(compareResults({ columns: ['a'], rows: [] }, base).reason).toMatch(/2 columns/)
    expect(compareResults({ columns: ['a', 'b'], rows: [[1, 'x']] }, base).reason).toMatch(/2 rows/)
  })

  it('checks the order when asked and says so', () => {
    const reversed = { columns: ['a', 'b'], rows: [[2, 'y'], [1, 'x']] }
    const r = compareResults(reversed, base, { ordered: true })
    expect(r.match).toBe(false)
    expect(r.reason).toMatch(/wrong order/)
  })
})

describe('checkAnswer', () => {
  it('accepts a different but equivalent query', () => {
    const r = checkAnswer(SQL, DATA, 'SELECT name FROM t WHERE score IS NOT NULL', "SELECT name FROM t WHERE name <> 'c'")
    expect(r.match).toBe(true)
  })

  it('surfaces the learner error', () => {
    const r = checkAnswer(SQL, DATA, 'SELECT nope FROM t', 'SELECT 1')
    expect(r.ok).toBe(false)
    expect(r.error).toMatch(/no such column/i)
  })

  it('blames the solution, not the learner, when the reference fails', () => {
    const r = checkAnswer(SQL, DATA, 'SELECT 1', 'SELECT nope FROM t')
    expect(r.error).toMatch(/model solution failed/)
  })
})
