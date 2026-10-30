import { TriangleAlert } from 'lucide-react'

/** Shows problems found while validating roadmap.json, so bad data is visible rather than silent. */
export default function DataIssues({ issues }) {
  if (!issues?.length) return null
  return (
    <div className="rounded-xl border border-warn/30 bg-warn/5 p-4 text-sm">
      <div className="mb-2 flex items-center gap-2 font-medium text-warn">
        <TriangleAlert size={16} /> {issues.length} issue{issues.length > 1 ? 's' : ''} in roadmap.json
      </div>
      <ul className="list-disc space-y-1 pl-5 text-muted">
        {issues.map((issue, i) => (
          <li key={i}>
            <span className="text-faint">{issue.level}:</span> {issue.message}
          </li>
        ))}
      </ul>
    </div>
  )
}
