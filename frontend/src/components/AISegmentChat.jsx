import { useState } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import { useAISegment } from '../hooks/useAISegment'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import CustomerTable from './CustomerTable'
import { cn } from '../lib/utils'

const EXAMPLES = ['Inactive 30 days', 'High spenders', 'Mumbai customers']

export default function AISegmentChat({ onSave }) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const aiSegment = useAISegment()

  const handleSubmit = async (q) => {
    const searchQuery = q || query
    if (!searchQuery.trim()) return
    setResult(null)
    try {
      const data = await aiSegment.mutateAsync(searchQuery)
      setResult(data)
    } catch {
      // error handled by mutation state
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Segment Builder
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Describe your audience..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            />
            <Button onClick={() => handleSubmit()} disabled={aiSegment.isPending}>
              {aiSegment.isPending ? (
                <span className="flex items-center gap-1">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Thinking
                  <span className="animate-pulse">...</span>
                </span>
              ) : (
                'Analyze'
              )}
            </Button>
          </div>

          <div className="flex flex-wrap gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => { setQuery(ex); handleSubmit(ex) }}
                className="rounded-full border border-gray-200 px-3 py-1 text-xs text-gray-600 hover:border-primary hover:text-primary transition-colors"
              >
                {ex}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {aiSegment.isError && (
        <div className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
          Failed to generate segment. Please try again.
        </div>
      )}

      {result && (
        <Card className="border-primary/20">
          <CardContent className="p-6 space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">{result.segment_name}</h3>
              <p className="text-sm text-gray-500 mt-1">{result.description}</p>
            </div>

            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">AI Reasoning</p>
              <p className="text-sm text-gray-700 mt-1">{result.reasoning}</p>
            </div>

            <div className="flex items-center gap-4">
              <div className="rounded-lg bg-primary/10 px-4 py-2">
                <p className="text-2xl font-bold text-primary">{result.preview_count}</p>
                <p className="text-xs text-gray-500">matching customers</p>
              </div>
            </div>

            {result.sample_customers?.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Sample Customers</p>
                <CustomerTable customers={result.sample_customers} loading={false} />
              </div>
            )}

            <Button
              onClick={() => onSave?.(result)}
              className={cn('w-full')}
              disabled={result.preview_count === 0}
            >
              Save Segment
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
