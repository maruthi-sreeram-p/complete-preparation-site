import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import StatusIcon from '@/components/ui/StatusIcon.jsx'
import { NODE_SIZE } from '@/lib/roadmap/layout.js'
import { STATUS, STATUS_LABEL, nextStatus } from '@/lib/progress/status.js'
import { cn } from '@/lib/util.js'

const handleClass = '!pointer-events-none !size-1 !min-h-0 !min-w-0 !border-0 !bg-transparent'

function TopicNode({ data }) {
  const { topic, category, status, sub, step, dimmed, onCycleStatus } = data
  const completed = status === STATUS.COMPLETED

  return (
    <div
      title={topic.summary || topic.title}
      style={{ width: NODE_SIZE.width, height: NODE_SIZE.height, borderLeftColor: category.color }}
      className={cn(
        'cursor-pointer rounded-xl border border-l-[3px] bg-panel px-3 py-2.5 hover:border-line-strong',
        completed ? 'border-ok/25 bg-ok/[0.04]' : 'border-line',
        status === STATUS.IN_PROGRESS && 'border-accent-2/50',
        !topic.hasContent && 'border-dashed',
        dimmed && 'opacity-30',
      )}
    >
      <Handle type="target" position={Position.Top} className={handleClass} />
      <Handle type="source" position={Position.Bottom} className={handleClass} />
      <div className="flex h-full items-center gap-2.5">
        <button
          type="button"
          aria-label={`${topic.title}: ${STATUS_LABEL[status]}. Click to change.`}
          onClick={(e) => {
            e.stopPropagation()
            onCycleStatus(topic.id, nextStatus(status))
          }}
          className="nodrag nopan -m-1 shrink-0 rounded-full p-1"
        >
          <StatusIcon status={status} size={20} />
        </button>
        <div className="min-w-0 flex-1">
          <div className="line-clamp-2 text-[13px] font-medium leading-snug">
            {step && <span className="mr-1 tabular-nums text-faint">{step}.</span>}
            {topic.title}
          </div>
          {sub.total > 0 && (
            <div className="mt-1 text-[11px] tabular-nums text-faint">
              {sub.done}/{sub.total} chapters
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default memo(TopicNode)

/** A stage heading sitting on the spine of the tree, with its progress. */
export const StageNode = memo(function StageNode({ data }) {
  const { category, step, done, total, width } = data
  return (
    <div style={{ width }} className="flex justify-center">
      <div className="flex items-center gap-2.5 rounded-full border border-line-strong bg-panel-2 px-4 py-1.5">
        <span className="size-2 shrink-0 rounded-full" style={{ background: category.color }} />
        <span className="text-sm font-semibold">
          Stage {step}: {category.title}
        </span>
        <span className="text-xs tabular-nums text-muted">
          {done}/{total}
        </span>
      </div>
    </div>
  )
})
