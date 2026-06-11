import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { getCampaigns } from '../api/campaigns'
import CampaignTable from '../components/CampaignTable'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'

export default function Campaigns() {
  const { data: campaigns = [], isLoading } = useQuery({
    queryKey: ['campaigns'],
    queryFn: getCampaigns,
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Link to="/campaigns/create">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Campaign
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Campaigns</CardTitle>
        </CardHeader>
        <CardContent>
          <CampaignTable campaigns={campaigns} loading={isLoading} />
        </CardContent>
      </Card>
    </div>
  )
}
