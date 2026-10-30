import { STATUS_LABEL, STATUS_ORDER } from '@/lib/progress/status.js'
import { cn } from '@/lib/util.js'
import StatusIcon from './StatusIcon.jsx'

/** Segmented control for choosing Not started / In progress / Completed. */
export default function StatusSelect({ value, onChange, size = 'md' }) {
  return (
    <div role="radiogroup" aria-label="Status" className="inline-flex rounded-lg border border-line bg-panel p-0.5">
      {STATUS_ORDER.map((status) => {
        const active = value === status
        return (
          <button
            key={status}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(status)}
            className={cn(
              'inline-flex items-center gap-1.5 rounded-md font-medium transition-colors',
              size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-[13px]',
              active ? 'bg-panel-2 text-ink shadow-sm ring-1 ring-line-strong' : 'text-faint hover:text-muted',
            )}
          >
            <StatusIcon status={status} size={size === 'sm' ? 13 : 15} />
            <span className="hidden sm:inline">{STATUS_LABEL[status]}</span>
          </button>
        )
      })}
    </div>
  )
}
