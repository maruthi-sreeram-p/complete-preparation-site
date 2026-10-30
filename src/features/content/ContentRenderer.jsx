import { memo } from 'react'
import { Block } from './blockRegistry.jsx'
import { sectionMeta } from './sectionTypes.js'

/**
 * One section of normalised topic content (see lib/content/normalize.js).
 * Memoised: ticking a status elsewhere on the page must not re-render long content.
 */
export const Section = memo(function Section({ section }) {
  const { Icon, label } = sectionMeta(section.type)
  return (
    <section id={section.id} className="scroll-mt-24">
      <h2 className="mb-5 flex items-center gap-2.5 text-lg font-semibold tracking-tight">
        <Icon size={18} className="text-accent" />
        {section.title || label}
      </h2>
      <div className="space-y-5">
        {section.blocks.map((block, i) => (
          <div key={i} className="lazy-block">
            <Block block={block} />
          </div>
        ))}
      </div>
    </section>
  )
})
