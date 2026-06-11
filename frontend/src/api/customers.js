import { api } from './client'

export async function getCustomers() {
  const { data } = await api.get('/api/customers')
  return data
}

export async function getCustomer(id) {
  const { data } = await api.get(`/api/customers/${id}`)
  return data
}

export async function createCustomer(customer) {
  const { data } = await api.post('/api/customers', customer)
  return data
}

export async function uploadCustomersCSV(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/api/customers/upload-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    },
  })
  return data
}
