import { useEffect, useState } from 'react'
import { Expand, X } from 'lucide-react'
import { renderMermaid } from '@/lib/content/mermaid.js'
import Markdown from './Markdown.jsx'

/**
 * A diagram plus an explanation of each component.
 * block: { title?, format: 'mermaid', code, caption?, components?: [{ name, description }] }
 *    or: { title?, format: 'svg', svg, width?, alt?, caption? }   (figures carried over from the source PDF)
 */
export default function DiagramBlock({ title, format = 'mermaid', code, svg, width, alt, caption, components }) {
  const [state, setState] = useState({ status: 'loading' })
  const [expanded, setExpanded] = useState(false)

  useEffect(() => {
    if (format === 'svg') {
      setState(svg ? { status: 'ready', svg } : { status: 'error', message: 'This figure has no drawing.' })
      return
    }
    if (format !== 'mermaid') {
      setState({ status: 'error', message: `Unsupported diagram format "${format}".` })
      return
    }
    let alive = true
    setState({ status: 'loading' })
    renderMermaid(code ?? '')
      .then((svg) => alive && setState({ status: 'ready', svg }))
      .catch((err) => alive && setState({ status: 'error', message: String(err?.message ?? err) }))
    return () => {
      alive = false
    }
  }, [format, code, svg])

  useEffect(() => {
    if (!expanded) return
    const onKey = (e) => e.key === 'Escape' && setExpanded(false)
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [expanded])

  return (
    <figure className="overflow-hidden rounded-xl border border-line bg-panel">
      {(title || state.status === 'ready') && (
        <figcaption className="flex items-center justify-between border-b border-line bg-panel-2 px-3 py-1.5 text-xs text-muted">
          <span className="truncate">{title || 'Diagram'}</span>
          {state.status === 'ready' && (
            <button
              type="button"
              onClick={() => setExpanded(true)}
              aria-label="Expand diagram"
              className="rounded p-1 text-faint transition-colors hover:text-ink"
            >
              <Expand size={14} />
            </button>
          )}
        </figcaption>
      )}

      <div className="overflow-x-auto p-4">
        {state.status === 'loading' && <div className="py-10 text-center text-sm text-faint">Rendering diagram…</div>}
        {state.status === 'ready' && (
          <div
            role="img"
            aria-label={alt || caption || title || 'Diagram'}
            className="mx-auto max-w-full [&_svg]:h-auto [&_svg]:w-full"
            style={format === 'svg' ? { width: '100%', maxWidth: Math.round((width || 500) * 2) } : { width: 'fit-content' }}
            dangerouslySetInnerHTML={{ __html: state.svg }}
          />
        )}
        {state.status === 'error' && (
          <div className="rounded-lg border border-danger/30 bg-danger/5 p-3 text-sm">
            <div className="font-medium text-danger">This diagram could not be rendered.</div>
            <div className="mt-1 text-xs text-muted">{state.message}</div>
            <pre className="mt-2 overflow-x-auto font-mono text-xs text-muted">{code}</pre>
          </div>
        )}
      </div>

      {caption && <p className="border-t border-line px-4 py-2.5 text-xs text-muted">{caption}</p>}

      {Array.isArray(components) && components.length > 0 && (
        <dl className="grid border-t border-line sm:grid-cols-2">
          {components.map((c, i) => (
            <div key={i} className="border-b border-line p-3 last:border-b-0 sm:odd:border-r sm:[&:nth-last-child(2):nth-child(odd)]:border-b-0">
              <dt className="text-sm font-medium">{c.name}</dt>
              <dd className="mt-0.5 text-[13px] text-muted">
                <Markdown inline>{c.description}</Markdown>
              </dd>
            </div>
          ))}
        </dl>
      )}

      {expanded && state.status === 'ready' && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={title || 'Diagram'}
          className="fixed inset-0 z-50 flex flex-col bg-canvas/95 backdrop-blur"
          onClick={() => setExpanded(false)}
        >
          <div className="flex items-center justify-between px-4 py-3 text-sm text-muted">
            <span>{title}</span>
            <button type="button" aria-label="Close" className="rounded p-1 hover:text-ink" onClick={() => setExpanded(false)}>
              <X size={18} />
            </button>
          </div>
          <div className="grid flex-1 place-items-center overflow-auto p-6" onClick={(e) => e.stopPropagation()}>
            <div className="w-full max-w-6xl [&_svg]:h-auto [&_svg]:w-full [&_svg]:max-w-none" dangerouslySetInnerHTML={{ __html: state.svg }} />
          </div>
        </div>
      )}
    </figure>
  )
}
