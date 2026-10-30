import {
  BookOpen,
  Code,
  FlaskConical,
  Layers,
  Lightbulb,
  Link2,
  ListChecks,
  Network,
  StickyNote,
  Workflow,
  FileText,
} from 'lucide-react'

/** Section `type` → icon and default title. Types are hints; any section renders either way. */
export const SECTION_TYPES = {
  introduction: { label: 'Introduction', Icon: BookOpen },
  concept: { label: 'Concept explanation', Icon: Lightbulb },
  theory: { label: 'Detailed theory', Icon: Layers },
  visual: { label: 'Visual explanation', Icon: Workflow },
  architecture: { label: 'Architecture and workflow', Icon: Network },
  code: { label: 'Code examples', Icon: Code },
  example: { label: 'Practical examples', Icon: FlaskConical },
  notes: { label: 'Important notes', Icon: StickyNote },
  related: { label: 'Related concepts', Icon: Link2 },
  practice: { label: 'Practice questions', Icon: ListChecks },
  other: { label: 'Section', Icon: FileText },
}

export const sectionMeta = (type) => SECTION_TYPES[type] ?? SECTION_TYPES.other
