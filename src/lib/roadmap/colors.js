/** Named accents a roadmap category may use. Hex values are accepted too. */
export const CATEGORY_PALETTE = {
  violet: '#8b7cf6',
  blue: '#5b8def',
  cyan: '#3fb8d9',
  teal: '#34c3a0',
  fuchsia: '#c26fe0',
  amber: '#e0a84a',
  rose: '#e0709a',
  green: '#6fbf73',
  slate: '#8a93a8',
}

const PALETTE_ORDER = Object.keys(CATEGORY_PALETTE)

/** Resolve a category colour (palette name, hex, or nothing) to a hex string. */
export function resolveCategoryColor(color, index) {
  if (typeof color === 'string') {
    if (CATEGORY_PALETTE[color]) return CATEGORY_PALETTE[color]
    if (/^#[0-9a-f]{3,8}$/i.test(color)) return color
  }
  return CATEGORY_PALETTE[PALETTE_ORDER[index % PALETTE_ORDER.length]]
}
