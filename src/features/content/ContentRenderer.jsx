import { Block } from './blockRegistry.jsx'
import { sectionMeta } from './sectionTypes.js'

/** Renders normalised topic content (see lib/content/normalize.js) as a stack of sections. */
export default function ContentRenderer({ content }) {
  return (
    <div className="space-y-12">
      {content.sections.map((section) => {
        const { Icon, label } = sectionMeta(section.type)
        return (
          <section key={section.id} id={section.id} className="scroll-mt-24">
            <h2 className="mb-5 flex items-center gap-2.5 text-lg font-semibold tracking-tight">
              <Icon size={18} className="text-accent" />
              {section.title || label}
            </h2>
            <div className="space-y-5">
              {section.blocks.map((block, i) => (
                <Block key={i} block={block} />
              ))}
            </div>
          </section>
        )
      })}
    </div>
  )
}
