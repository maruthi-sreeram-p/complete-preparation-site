/**
 * Running and checking SQL in the browser with SQLite compiled to WebAssembly (sql.js).
 *
 * The functions take the loaded `SQL` module as an argument instead of importing it, so the same code
 * runs in the app (where the module is loaded lazily, see loadSqlEngine) and in tests under Node.
 *
 * Every run starts from a fresh database built from the subject's dataset, so one query can never
 * damage the data for the next one, and "UPDATE" or "DROP" are safe to experiment with.
 */

/** Loads the SQLite engine on first use. The WebAssembly file is a separate download, only fetched here. */
let enginePromise = null
export function loadSqlEngine() {
  enginePromise ??= (async () => {
    const [{ default: initSqlJs }, { default: wasmUrl }] = await Promise.all([
      import('sql.js/dist/sql-wasm-browser.js'),
      import('sql.js/dist/sql-wasm-browser.wasm?url'),
    ])
    return initSqlJs({ locateFile: () => wasmUrl })
  })().catch((error) => {
    enginePromise = null // allow a retry after a network failure
    throw error
  })
  return enginePromise
}

export const MAX_ROWS_SHOWN = 200

/** Runs `query` on a fresh copy of the dataset. Returns { ok, columns, rows } or { ok: false, error }. */
export function runQuery(SQL, datasetSql, query) {
  const db = new SQL.Database()
  try {
    db.exec(datasetSql)
    const results = db.exec(query)
    const last = results[results.length - 1]
    if (!last) return { ok: true, columns: [], rows: [], message: 'The statement ran and returned no rows.' }
    return { ok: true, columns: last.columns, rows: last.values }
  } catch (error) {
    return { ok: false, error: String(error?.message ?? error) }
  } finally {
    db.close()
  }
}

/** Numbers compare to 4 decimals (floating point), text is trimmed, NULL stays NULL. */
function normalizeCell(value) {
  if (typeof value === 'number') return Math.round(value * 10000) / 10000
  if (typeof value === 'string') return value.trim()
  return value
}

const rowKey = (row) => JSON.stringify(row.map(normalizeCell))

/**
 * Compares the learner's result with the expected one.
 * Column names do not matter (aliases differ between correct answers); the number of columns,
 * the values and, only when `ordered` is true, the order of the rows do.
 */
export function compareResults(actual, expected, { ordered = false } = {}) {
  if (actual.columns.length !== expected.columns.length) {
    return {
      match: false,
      reason: `Expected ${expected.columns.length} column${expected.columns.length === 1 ? '' : 's'}, your query returned ${actual.columns.length}.`,
    }
  }
  if (actual.rows.length !== expected.rows.length) {
    return {
      match: false,
      reason: `Expected ${expected.rows.length} row${expected.rows.length === 1 ? '' : 's'}, your query returned ${actual.rows.length}.`,
    }
  }
  const a = actual.rows.map(rowKey)
  const e = expected.rows.map(rowKey)
  if (ordered) {
    const at = a.findIndex((key, i) => key !== e[i])
    if (at === -1) return { match: true }
    const sameSet = [...a].sort().join('|') === [...e].sort().join('|')
    return {
      match: false,
      reason: sameSet
        ? 'The right rows, in the wrong order. This question asks for a specific ORDER BY.'
        : `Row ${at + 1} differs from the expected result.`,
    }
  }
  if ([...a].sort().join('|') === [...e].sort().join('|')) return { match: true }
  return { match: false, reason: 'The row count is right but some values differ from the expected result.' }
}

/** Runs the learner's query and the model solution on the same data and compares them. */
export function checkAnswer(SQL, datasetSql, query, solution, options) {
  const actual = runQuery(SQL, datasetSql, query)
  if (!actual.ok) return { ...actual, match: false }
  const expected = runQuery(SQL, datasetSql, solution)
  if (!expected.ok) return { ok: false, match: false, error: `The model solution failed: ${expected.error}` }
  return { ...actual, ...compareResults(actual, expected, options) }
}
