import { api } from './client'

export async function getCampaigns() {
  const { data } = await api.get('/api/campaigns')
  return data
}

export async function getCampaign(id) {
  const { data } = await api.get(`/api/campaigns/${id}`)
  return data
}

export async function createCampaign(campaign) {
  const { data } = await api.post('/api/campaigns', campaign)
  return data
}

export async function launchCampaign(id) {
  const { data } = await api.post(`/api/campaigns/${id}/launch`)
  return data
}

export async function aiCampaignMessage(id) {
  const { data } = await api.post(`/api/campaigns/${id}/ai-message`)
  return data
}
