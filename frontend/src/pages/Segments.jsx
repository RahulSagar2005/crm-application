import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Users, Trash2 } from 'lucide-react'
import { getSegments, getSegmentCustomers, deleteSegment } from '../api/segments'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import CustomerTable from '../components/CustomerTable'
import { formatDate, formatNumber } from '../lib/utils'

export default function Segments() {
  const [selectedId, setSelectedId] = useState(null)

  const { data: segments = [], isLoading, refetch } = useQuery({
    queryKey: ['segments'],
    queryFn: getSegments,
  })

  const { data: segmentCustomers = [], isLoading: loadingCustomers } = useQuery({
    queryKey: ['segment-customers', selectedId],
    queryFn: () => getSegmentCustomers(selectedId),
    enabled: !!selectedId,
  })

  const handleDelete = async (id) => {
    if (!confirm('Delete this segment?')) return
    await deleteSegment(id)
    if (selectedId === id) setSelectedId(null)
    refetch()
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-40 animate-pulse rounded-xl bg-gray-100" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-end">
        <Link to="/segments/create">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Create with AI
          </Button>
        </Link>
      </div>

      {segments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-gray-400">
          <Users className="h-12 w-12 mb-3" />
          <p className="text-lg font-medium">No segments yet</p>
          <p className="text-sm mt-1">Use AI to create your first customer segment</p>
          <Link to="/segments/create" className="mt-4">
            <Button>Create with AI</Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {segments.map((seg) => (
            <Card
              key={seg.id}
              className={`cursor-pointer transition-all hover:shadow-md ${
                selectedId === seg.id ? 'ring-2 ring-primary' : ''
              }`}
              onClick={() => setSelectedId(seg.id)}
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{seg.name}</h3>
                    {seg.ai_generated && (
                      <span className="text-xs text-primary font-medium">AI Generated</span>
                    )}
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDelete(seg.id) }}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
                <p className="text-sm text-gray-500 mt-2 line-clamp-2">{seg.description}</p>
                <div className="mt-4 flex items-center justify-between text-sm">
                  <span className="flex items-center gap-1 text-gray-600">
                    <Users className="h-4 w-4" />
                    {formatNumber(seg.customer_count)} customers
                  </span>
                  <span className="text-gray-400">{formatDate(seg.created_at)}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selectedId && (
        <Card>
          <CardHeader>
            <CardTitle>Segment Customers</CardTitle>
          </CardHeader>
          <CardContent>
            <CustomerTable customers={segmentCustomers} loading={loadingCustomers} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
