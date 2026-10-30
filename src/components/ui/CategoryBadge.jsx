import { cn } from '@/lib/util.js'

export default function CategoryBadge({ category, className }) {
  return (
    <span className={cn('inline-flex min-w-0 items-center gap-1.5 text-xs text-muted', className)}>
      <span className="size-2 shrink-0 rounded-full" style={{ background: category.color }} />
      <span className="truncate">{category.title}</span>
    </span>
  )
}
