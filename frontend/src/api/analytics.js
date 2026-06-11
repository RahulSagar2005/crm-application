import { api } from './client'

export async function getCampaignAnalytics(campaignId) {
  const { data } = await api.get(`/api/analytics/${campaignId}`)
  return data
}

export async function getDashboardAnalytics() {
  const { data } = await api.get('/api/analytics/dashboard')
  return data
}
