import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createSegment } from '../api/segments'
import AISegmentChat from '../components/AISegmentChat'

export default function CreateSegment() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const saveMutation = useMutation({
    mutationFn: createSegment,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['segments'] })
      navigate('/segments')
    },
  })

  const handleSave = (result) => {
    saveMutation.mutate({
      name: result.segment_name,
      description: result.description,
      rules: result.rules,
      ai_generated: true,
    })
  }

  return (
    <div className="max-w-3xl">
      <AISegmentChat onSave={handleSave} />
      {saveMutation.isError && (
        <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-700">
          Failed to save segment. Please try again.
        </div>
      )}
    </div>
  )
}
