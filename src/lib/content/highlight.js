let hljsPromise = null

/** highlight.js is loaded on first use so it stays out of the main bundle. */
export function loadHighlighter() {
  hljsPromise ??= import('highlight.js/lib/common').then((m) => m.default)
  return hljsPromise
}

export const escapeHtml = (text) =>
  text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

/**
 * Split highlight.js HTML into one HTML string per source line, closing and
 * re-opening <span>s at each line break so multi-line tokens (comments,
 * template strings) stay correctly coloured.
 */
export function splitHighlightedLines(html) {
  const lines = []
  const open = []
  let current = ''
  let last = 0
  const tokens = /<span[^>]*>|<\/span>|\n/g
  let match
  while ((match = tokens.exec(html))) {
    current += html.slice(last, match.index)
    const token = match[0]
    if (token === '\n') {
      lines.push(current + '</span>'.repeat(open.length))
      current = open.join('')
    } else if (token === '</span>') {
      open.pop()
      current += token
    } else {
      open.push(token)
      current += token
    }
    last = tokens.lastIndex
  }
  lines.push(current + html.slice(last))
  return lines
}

/** Plain, escaped lines: shown immediately and used when a language is unknown. */
export const plainLines = (code) => code.split('\n').map(escapeHtml)

export async function highlightLines(code, language) {
  const hljs = await loadHighlighter()
  if (!language || !hljs.getLanguage(language)) return plainLines(code)
  return splitHighlightedLines(hljs.highlight(code, { language, ignoreIllegals: true }).value)
}
