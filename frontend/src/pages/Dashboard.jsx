import { useQuery } from '@tanstack/react-query'
import { Users, Megaphone, Eye, MousePointer } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { getDashboardAnalytics } from '../api/analytics'
import StatCard from '../components/StatCard'
import CampaignTable from '../components/CampaignTable'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { formatNumber } from '../lib/utils'

export default function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardAnalytics,
  })

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Customers"
          value={isLoading ? '...' : formatNumber(data?.total_customers)}
          icon={Users}
        />
        <StatCard
          title="Total Campaigns"
          value={isLoading ? '...' : formatNumber(data?.total_campaigns)}
          icon={Megaphone}
        />
        <StatCard
          title="Avg Open Rate"
          value={isLoading ? '...' : `${data?.avg_open_rate || 0}%`}
          icon={Eye}
        />
        <StatCard
          title="Avg Click Rate"
          value={isLoading ? '...' : `${data?.avg_click_rate || 0}%`}
          icon={MousePointer}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Campaigns</CardTitle>
          </CardHeader>
          <CardContent>
            <CampaignTable campaigns={data?.recent_campaigns} loading={isLoading} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Open vs Click Rate (Last 7 Campaigns)</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-64 animate-pulse rounded-lg bg-gray-100" />
            ) : data?.chart_data?.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.chart_data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} unit="%" />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="open_rate" name="Open Rate" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="click_rate" name="Click Rate" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-64 items-center justify-center text-gray-400">
                No campaign data yet
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
