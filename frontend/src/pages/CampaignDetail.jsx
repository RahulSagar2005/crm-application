import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Send, CheckCircle, XCircle, Eye, MousePointer } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { getCampaignAnalytics } from '../api/analytics'
import StatCard from '../components/StatCard'
import CampaignStatusBadge from '../components/CampaignStatusBadge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table'
import { formatDateTime } from '../lib/utils'

export default function CampaignDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const { data, isLoading } = useQuery({
    queryKey: ['campaign-analytics', id],
    queryFn: () => getCampaignAnalytics(id),
    refetchInterval: (query) =>
      query.state.data?.status === 'sending' ? 5000 : false,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200" />
        <div className="grid grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-100" />
          ))}
        </div>
      </div>
    )
  }

  if (!data) return <p className="text-gray-500">Campaign not found</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/campaigns')}>
          <ArrowLeft className="h-4 w-4 mr-1" /> Back
        </Button>
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900">{data.campaign_name}</h2>
            <CampaignStatusBadge status={data.status} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <StatCard title="Sent" value={data.sent} icon={Send} />
        <StatCard title="Delivered" value={data.delivered} icon={CheckCircle} />
        <StatCard title="Failed" value={data.failed} icon={XCircle} />
        <StatCard title="Opened" value={data.opened} icon={Eye} />
        <StatCard title="Clicked" value={data.clicked} icon={MousePointer} />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-sm text-gray-500">Open Rate</p>
            <p className="text-4xl font-bold text-primary mt-1">{data.open_rate}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-sm text-gray-500">Click Rate</p>
            <p className="text-4xl font-bold text-amber-500 mt-1">{data.click_rate}%</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Delivery Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          {data.timeline?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={data.timeline}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="delivered" stackId="1" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
                <Area type="monotone" dataKey="opened" stackId="1" stroke="#a855f7" fill="#a855f7" fillOpacity={0.3} />
                <Area type="monotone" dataKey="clicked" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.3} />
                <Area type="monotone" dataKey="failed" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.3} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-48 items-center justify-center text-gray-400">
              {data.status === 'sending' ? 'Waiting for delivery events...' : 'No timeline data'}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Individual Communications</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Customer</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Sent At</TableHead>
                <TableHead>Updated At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.communications?.length > 0 ? (
                data.communications.map((c) => (
                  <TableRow key={c.id}>
                    <TableCell className="font-medium">{c.customer_name}</TableCell>
                    <TableCell><CampaignStatusBadge status={c.status} /></TableCell>
                    <TableCell>{formatDateTime(c.sent_at)}</TableCell>
                    <TableCell>{formatDateTime(c.updated_at)}</TableCell>
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-gray-400 py-8">
                    No communications yet
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
