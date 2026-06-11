import { api } from './client'

export async function getSegments() {
  const { data } = await api.get('/api/segments')
  return data
}

export async function createSegment(segment) {
  const { data } = await api.post('/api/segments', segment)
  return data
}

export async function aiSuggestSegment(query) {
  const { data } = await api.post('/api/segments/ai-suggest', { query })
  return data
}

export async function getSegmentCustomers(id) {
  const { data } = await api.get(`/api/segments/${id}/customers`)
  return data
}

export async function deleteSegment(id) {
  await api.delete(`/api/segments/${id}`)
}
