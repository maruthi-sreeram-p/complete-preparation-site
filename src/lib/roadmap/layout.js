export const NODE_SIZE = { width: 248, height: 76 }

const DEFAULTS = { gapX: 44, gapY: 84, maxPerRow: 6 }

/**
 * Layered top-to-bottom layout for the dependency graph.
 *
 * 1. A topic's layer is one more than its deepest prerequisite.
 * 2. Over-wide layers are split into several rows.
 * 3. Within each row, topics are placed near the average x of their neighbours
 *    (parents on the way down, children on the way up), then spread out so they
 *    never overlap.
 *
 * A topic with an explicit `position` in roadmap.json keeps it.
 * Returns top-left positions, which is what React Flow expects.
 */
export function computeLayout(roadmap, options = {}) {
  const { gapX, gapY, maxPerRow } = { ...DEFAULTS, ...options }
  const { width, height } = NODE_SIZE
  const step = width + gapX
  const { topicsById, sequence, unlocks } = roadmap

  const layerOf = {}
  for (const id of sequence) {
    const reqs = topicsById[id].requires
    layerOf[id] = reqs.length ? Math.max(...reqs.map((r) => layerOf[r])) + 1 : 0
  }

  const layers = []
  for (const id of sequence) (layers[layerOf[id]] ??= []).push(id)

  const rows = []
  for (const layer of layers) {
    if (!layer) continue
    const rowCount = Math.ceil(layer.length / maxPerRow)
    const size = Math.ceil(layer.length / rowCount)
    for (let i = 0; i < layer.length; i += size) rows.push(layer.slice(i, i + size))
  }

  const order = {}
  sequence.forEach((id, i) => (order[id] = i))
  const cx = {} // x of node centres

  const place = (ids, desired) => {
    const sorted = [...ids].sort((a, b) => desired[a] - desired[b] || order[a] - order[b])
    const xs = []
    let prev = -Infinity
    for (const id of sorted) {
      const x = Math.max(desired[id], prev + step)
      xs.push(x)
      prev = x
    }
    const shift = sorted.reduce((sum, id, i) => sum + desired[id] - xs[i], 0) / (sorted.length || 1)
    sorted.forEach((id, i) => (cx[id] = xs[i] + shift))
  }

  const mean = (values, fallback) =>
    values.length ? values.reduce((a, b) => a + b, 0) / values.length : fallback

  // initial pass, top to bottom
  rows.forEach((row, rowIndex) => {
    const desired = {}
    row.forEach((id, i) => {
      const parents = topicsById[id].requires
      desired[id] = rowIndex === 0 || !parents.length
        ? (i - (row.length - 1) / 2) * step
        : mean(parents.map((p) => cx[p]), 0)
    })
    place(row, desired)
  })

  // refine: bottom-up, then top-down again
  for (const direction of ['up', 'down']) {
    const sequenceOfRows = direction === 'up' ? [...rows].reverse() : rows
    for (const row of sequenceOfRows) {
      const desired = {}
      for (const id of row) {
        const neighbours = direction === 'up' ? unlocks[id] : topicsById[id].requires
        desired[id] = mean(neighbours.map((n) => cx[n]), cx[id])
      }
      place(row, desired)
    }
  }

  const rowOf = {}
  rows.forEach((row, i) => row.forEach((id) => (rowOf[id] = i)))

  const positions = {}
  for (const id of sequence) {
    const explicit = topicsById[id].position
    positions[id] = explicit ?? {
      x: Math.round(cx[id] - width / 2),
      y: rowOf[id] * (height + gapY),
    }
  }
  return { positions }
}
