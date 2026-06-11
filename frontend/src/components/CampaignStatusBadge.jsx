import { Badge } from './ui/badge'

const STATUS_VARIANTS = {
  queued: 'default',
  draft: 'default',
  sending: 'blue',
  sent: 'blue',
  delivered: 'green',
  failed: 'red',
  opened: 'purple',
  read: 'purple',
  clicked: 'amber',
}

export default function CampaignStatusBadge({ status }) {
  const variant = STATUS_VARIANTS[status] || 'default'
  return (
    <Badge variant={variant} className="capitalize">
      {status}
    </Badge>
  )
}
