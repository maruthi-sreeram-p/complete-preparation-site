import { Link } from 'react-router-dom'
import { SITE_OWNER_NAME } from '@/config.js'
import { LEGAL_LINKS } from '@/features/legal/legalLinks.js'

export default function Footer() {
  return (
    <footer className="border-t border-line bg-canvas">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-6 text-sm text-muted sm:flex-row sm:items-center sm:justify-between lg:px-6">
        <p>© 2026 {SITE_OWNER_NAME}. All rights reserved.</p>
        <nav aria-label="Legal" className="flex flex-wrap gap-x-5 gap-y-2">
          {LEGAL_LINKS.map((l) => (
            <Link key={l.to} to={l.to} className="underline-offset-4 hover:text-ink hover:underline">
              {l.title}
            </Link>
          ))}
        </nav>
      </div>
    </footer>
  )
}
