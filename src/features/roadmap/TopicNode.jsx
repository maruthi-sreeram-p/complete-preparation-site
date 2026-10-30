import { memo } from 'react'
import { Handle, Position } from '@xyflow/react'
import StatusIcon from '@/components/ui/StatusIcon.jsx'
import { NODE_SIZE } from '@/lib/roadmap/layout.js'
import { STATUS, STATUS_LABEL, nextStatus } from '@/lib/progress/status.js'
import { cn } from '@/lib/util.js'

const handleClass = '!pointer-events-none !size-1 !min-h-0 !min-w-0 !border-0 !bg-transparent'

function TopicNode({ data }) {
  const { topic, category, status, sub, dimmed, onCycleStatus } = data
  const completed = status === STATUS.COMPLETED

  return (
    <div
      title={topic.summary || topic.title}
      style={{ width: NODE_SIZE.width, height: NODE_SIZE.height, borderLeftColor: category.color }}
      className={cn(
        'cursor-pointer rounded-xl border border-l-[3px] bg-panel px-3 py-2.5 transition-[opacity,border-color,box-shadow] duration-150',
        'hover:border-line-strong hover:shadow-lg hover:shadow-black/30',
        completed ? 'border-ok/25 bg-ok/[0.04]' : 'border-line',
        status === STATUS.IN_PROGRESS && 'border-accent-2/50',
        !topic.hasContent && 'border-dashed',
        dimmed && 'opacity-30',
      )}
    >
      <Handle type="target" position={Position.Top} className={handleClass} />
      <div className="flex h-full items-center gap-2.5">
        <button
          type="button"
          aria-label={`${topic.title}: ${STATUS_LABEL[status]}. Click to change.`}
          onClick={(e) => {
            e.stopPropagation()
            onCycleStatus(topic.id, nextStatus(status))
          }}
          className="nodrag nopan -m-1 shrink-0 rounded-full p-1 transition-transform hover:scale-110"
        >
          <StatusIcon status={status} size={20} />
        </button>
        <div className="min-w-0 flex-1">
          <div className="line-clamp-2 text-[13px] font-medium leading-snug">{topic.title}</div>
          <div className="mt-1 flex items-center gap-1.5 text-[11px] text-faint">
            <span className="size-1.5 shrink-0 rounded-full" style={{ background: category.color }} />
            <span className="truncate">{category.title}</span>
          </div>
        </div>
        {sub.total > 0 && (
          <span className="shrink-0 self-start text-[11px] tabular-nums text-faint">
            {sub.done}/{sub.total}
          </span>
        )}
      </div>
      <Handle type="source" position={Position.Bottom} className={handleClass} />
    </div>
  )
}

export default memo(TopicNode)
