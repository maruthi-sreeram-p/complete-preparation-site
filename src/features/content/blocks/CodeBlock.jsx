import { useEffect, useMemo, useState } from 'react'
import { Check, ChevronLeft, ChevronRight, Copy } from 'lucide-react'
import { highlightLines, plainLines } from '@/lib/content/highlight.js'
import { parseLineSpec } from '@/lib/content/normalize.js'
import { cn } from '@/lib/util.js'
import Markdown from './Markdown.jsx'

/**
 * Syntax-highlighted code with optional line emphasis (`highlight`) and an
 * optional step-by-step `walkthrough` ([{ lines, title, text }]).
 */
export default function CodeBlock({ code, language, title, highlight, walkthrough }) {
  const source = code ?? ''
  const [lines, setLines] = useState(() => plainLines(source))
  const [step, setStep] = useState(0)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    let alive = true
    setLines(plainLines(source))
    highlightLines(source, language).then((result) => alive && setLines(result))
    return () => {
      alive = false
    }
  }, [source, language])

  const steps = Array.isArray(walkthrough) ? walkthrough : []
  const activeStep = steps[Math.min(step, steps.length - 1)]
  const emphasised = useMemo(
    () => (activeStep ? parseLineSpec(activeStep.lines) : parseLineSpec(highlight)),
    [activeStep, highlight],
  )
  const hasEmphasis = emphasised.size > 0

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(source)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* clipboard unavailable */
    }
  }

  return (
    <figure className="overflow-hidden rounded-xl border border-line bg-panel">
      <figcaption className="flex items-center justify-between border-b border-line bg-panel-2 px-3 py-1.5 text-xs text-muted">
        <span className="truncate">{title || language || 'code'}</span>
        <span className="flex items-center gap-2">
          {title && language && <span className="font-mono text-faint">{language}</span>}
          <button
            type="button"
            onClick={copy}
            aria-label="Copy code"
            className="rounded p-1 text-faint transition-colors hover:text-ink"
          >
            {copied ? <Check size={14} className="text-ok" /> : <Copy size={14} />}
          </button>
        </span>
      </figcaption>

      <pre className="overflow-x-auto py-3 font-mono text-[13px] leading-6">
        <code>
          {lines.map((html, i) => {
            const n = i + 1
            const on = emphasised.has(n)
            return (
              <div
                key={n}
                className={cn(
                  'flex border-l-2 pr-4 transition-colors',
                  on ? 'border-accent bg-accent/10' : 'border-transparent',
                  hasEmphasis && !on && 'opacity-45',
                )}
              >
                <span className="w-10 shrink-0 select-none pr-3 text-right text-faint">{n}</span>
                <span className="whitespace-pre" dangerouslySetInnerHTML={{ __html: html || ' ' }} />
              </div>
            )
          })}
        </code>
      </pre>

      {activeStep && (
        <div className="border-t border-line bg-panel-2/60 p-4">
          <div className="mb-2 flex items-center justify-between gap-3">
            <div className="text-xs font-medium text-accent">
              Step {Math.min(step, steps.length - 1) + 1} of {steps.length}
              {activeStep.title && <span className="ml-2 text-ink">{activeStep.title}</span>}
            </div>
            <div className="flex gap-1">
              <StepButton label="Previous step" disabled={step === 0} onClick={() => setStep(step - 1)}>
                <ChevronLeft size={15} />
              </StepButton>
              <StepButton label="Next step" disabled={step >= steps.length - 1} onClick={() => setStep(step + 1)}>
                <ChevronRight size={15} />
              </StepButton>
            </div>
          </div>
          <Markdown>{activeStep.text}</Markdown>
        </div>
      )}
    </figure>
  )
}

function StepButton({ label, disabled, onClick, children }) {
  return (
    <button
      type="button"
      aria-label={label}
      disabled={disabled}
      onClick={onClick}
      className="rounded-md border border-line p-1 text-muted transition-colors enabled:hover:border-line-strong enabled:hover:text-ink disabled:opacity-30"
    >
      {children}
    </button>
  )
}
