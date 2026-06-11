import { useMutation } from '@tanstack/react-query'
import { aiSuggestSegment } from '../api/segments'

export function useAISegment() {
  return useMutation({
    mutationFn: (query) => aiSuggestSegment(query),
  })
}
