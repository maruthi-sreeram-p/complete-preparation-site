import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { APP_NAME, LEGAL_LAST_UPDATED } from '@/config.js'
import { LEGAL_LINKS } from './legalLinks.js'

/** Shared frame for the legal pages: title, date line, readable prose column, links to the other pages. */
export default function LegalPage({ title, intro, children, showDate = true }) {
  useEffect(() => {
    document.title = `${title} · ${APP_NAME}`
    return () => {
      document.title = APP_NAME
    }
  }, [title])

  return (
    <article className="mx-auto w-full max-w-3xl px-4 py-10 sm:py-14">
      <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">{title}</h1>
      {showDate && <p className="mt-2 text-sm text-muted">Last updated: {LEGAL_LAST_UPDATED}</p>}
      {intro && <p className="mt-4 text-base text-muted">{intro}</p>}
      <div className="doc mt-6 rounded-xl border border-line bg-panel p-5 sm:p-8">{children}</div>
      <nav aria-label="Legal pages" className="mt-6 flex flex-wrap gap-x-4 gap-y-2 text-sm">
        {LEGAL_LINKS.filter((l) => l.title !== title).map((l) => (
          <Link key={l.to} to={l.to} className="text-muted underline underline-offset-4 hover:text-ink">
            {l.title}
          </Link>
        ))}
      </nav>
    </article>
  )
}
