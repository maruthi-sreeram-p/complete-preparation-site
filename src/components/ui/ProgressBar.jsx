import { cn } from '@/lib/util.js'

export default function ProgressBar({ value, color, className }) {
  const pct = Math.max(0, Math.min(100, value))
  return (
    <div
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={pct}
      className={cn('h-1.5 w-full overflow-hidden rounded-full bg-line', className)}
    >
      <div
        className="h-full rounded-full transition-[width] duration-300"
        style={{ width: `${pct}%`, background: color ?? 'linear-gradient(90deg, var(--color-accent), var(--color-accent-2))' }}
      />
    </div>
  )
}
