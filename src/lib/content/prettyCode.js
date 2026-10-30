/**
 * The PDFs print short listings inside sentences ("What does this print? class A { ... } new B();").
 * These helpers turn such one-line code into a properly laid out code block.
 */

const INDENT = '    '

/** True for inline code that is really a listing: several statements or nested braces. */
export function isListing(code) {
  if (code.length < 30) return false
  const count = (ch) => code.split(ch).length - 1
  return count(';') >= 2 || count('{') >= 2
}

export function guessLanguage(code) {
  if (/^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|WITH)\b/i.test(code)) return 'sql'
  if (/\b(class|interface|public|void|int|long|String|new|return|System\.)\b/.test(code)) return 'java'
  return undefined
}

/** Lays out one-line brace-and-semicolon code over several indented lines. Strings are left alone. */
export function formatListing(code) {
  const lines = []
  let depth = 0
  let parens = 0
  let current = ''

  const flush = () => {
    const text = current.trim()
    if (text) lines.push(INDENT.repeat(Math.max(depth, 0)) + text)
    current = ''
  }

  for (let i = 0; i < code.length; i++) {
    const ch = code[i]

    if (ch === '"' || ch === "'") {
      let end = i + 1
      while (end < code.length && code[end] !== ch) end += code[end] === '\\' ? 2 : 1
      current += code.slice(i, end + 1)
      i = end
    } else if (ch === '(') {
      parens++
      current += ch
    } else if (ch === ')') {
      parens--
      current += ch
    } else if (ch === ';' && parens === 0) {
      current += ch
      flush()
    } else if (ch === '{') {
      const close = matchingBrace(code, i)
      const body = close === -1 ? ';' : code.slice(i + 1, close)
      if (!body.includes(';') && !body.includes('{')) {
        // an empty body or an initialiser stays on one line
        current += code.slice(i, close + 1)
        i = close
        if (!/^\s*[;,)]/.test(code.slice(i + 1))) flush()
      } else {
        current += ch
        flush()
        depth++
      }
    } else if (ch === '}') {
      flush()
      depth--
      current = '}'
      const rest = code.slice(i + 1)
      if (!/^\s*(else\b|catch\b|finally\b|[;,)])/.test(rest)) flush()
    } else {
      current += ch
    }
  }
  flush()
  return lines.join('\n')
}

function matchingBrace(code, open) {
  let depth = 0
  for (let i = open; i < code.length; i++) {
    if (code[i] === '{') depth++
    else if (code[i] === '}' && --depth === 0) return i
  }
  return -1
}

const SPANS = /`[^`\n]+`(?: `[^`\n]+`)*/g
const LIST_ITEM = /^(\s*)(?:[-*]|\d+\.)\s+/

/** Rewrites Markdown so that inline code holding a whole listing becomes a fenced code block. */
export function expandInlineListings(markdown) {
  if (!markdown.includes('`')) return markdown
  let inFence = false
  return markdown
    .split('\n')
    .map((line) => {
      if (/^\s*```/.test(line)) inFence = !inFence
      if (inFence || !line.includes('`')) return line

      const marker = LIST_ITEM.exec(line)
      const pad = ' '.repeat(marker ? marker[0].length : 0)
      let out = ''
      let last = 0
      for (const match of line.matchAll(SPANS)) {
        const code = match[0].replace(/` `/g, ' ').slice(1, -1)
        if (!isListing(code)) continue
        const fence = [`\`\`\`${guessLanguage(code) ?? ''}`, ...formatListing(code).split('\n'), '```']
          .map((l) => pad + l)
          .join('\n')
        const before = line.slice(last, match.index).trimEnd()
        out += `${before}\n\n${fence}\n\n`
        last = match.index + match[0].length
      }
      if (last === 0) return line
      const after = line.slice(last).trim()
      return (out + (after ? pad + after : '')).trimEnd()
    })
    .join('\n')
}
