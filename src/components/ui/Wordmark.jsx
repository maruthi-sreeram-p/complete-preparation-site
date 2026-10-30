import { APP_NAME, APP_NAME_PARTS } from '@/config.js'
import { cn } from '@/lib/util.js'

/** The JavaTrail name: heavy display type with "Trail" in the accent gradient. */
export default function Wordmark({ className }) {
  return (
    <span aria-label={APP_NAME} className={cn('font-display font-bold tracking-tight', className)}>
      {APP_NAME_PARTS[0]}
      <span className="bg-linear-to-r from-accent to-accent-2 bg-clip-text text-transparent">{APP_NAME_PARTS[1]}</span>
    </span>
  )
}
