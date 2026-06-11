import { Link } from 'react-router-dom'
import { formatDate } from '../lib/utils'
import CampaignStatusBadge from './CampaignStatusBadge'
import { Badge } from './ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'

const CHANNEL_VARIANTS = {
  whatsapp: 'green',
  sms: 'blue',
  email: 'default',
}

function SkeletonRow() {
  return (
    <TableRow>
      {[...Array(7)].map((_, i) => (
        <TableCell key={i}>
          <div className="h-4 animate-pulse rounded bg-gray-200" />
        </TableCell>
      ))}
    </TableRow>
  )
}

export default function CampaignTable({ campaigns, loading }) {
  if (loading) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Segment</TableHead>
            <TableHead>Channel</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Sent</TableHead>
            <TableHead>Open Rate</TableHead>
            <TableHead>Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...Array(5)].map((_, i) => <SkeletonRow key={i} />)}
        </TableBody>
      </Table>
    )
  }

  if (!campaigns?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-gray-400">
        <p className="text-lg font-medium">No campaigns yet</p>
        <p className="text-sm mt-1">Create your first campaign to reach customers</p>
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Segment</TableHead>
          <TableHead>Channel</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Sent</TableHead>
          <TableHead>Open Rate</TableHead>
          <TableHead>Date</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {campaigns.map((c) => (
          <TableRow key={c.id}>
            <TableCell>
              <Link to={`/campaigns/${c.id}`} className="font-medium text-primary hover:underline">
                {c.name}
              </Link>
            </TableCell>
            <TableCell>{c.segment_name || '—'}</TableCell>
            <TableCell>
              <Badge variant={CHANNEL_VARIANTS[c.channel] || 'default'} className="capitalize">
                {c.channel}
              </Badge>
            </TableCell>
            <TableCell><CampaignStatusBadge status={c.status} /></TableCell>
            <TableCell>{c.stats?.sent || 0}</TableCell>
            <TableCell>{c.stats?.open_rate || 0}%</TableCell>
            <TableCell>{formatDate(c.launched_at || c.created_at)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
