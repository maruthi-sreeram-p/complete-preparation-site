import { Circle, CircleCheck, CircleDot } from 'lucide-react'
import { STATUS, STATUS_LABEL } from '@/lib/progress/status.js'
import { cn } from '@/lib/util.js'

const ICONS = {
  [STATUS.NOT_STARTED]: { Icon: Circle, className: 'text-faint' },
  [STATUS.IN_PROGRESS]: { Icon: CircleDot, className: 'text-accent-2' },
  [STATUS.COMPLETED]: { Icon: CircleCheck, className: 'text-ok' },
}

export default function StatusIcon({ status, size = 18, className }) {
  const { Icon, className: color } = ICONS[status] ?? ICONS[STATUS.NOT_STARTED]
  return <Icon size={size} className={cn(color, className)} aria-label={STATUS_LABEL[status]} role="img" />
}
