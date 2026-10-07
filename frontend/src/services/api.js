import axios from 'axios'
import { API_BASE_URL } from '../config/config'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    Accept: 'application/json',
  },
})

export async function uploadResearchPaper(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post(
    '/papers/upload',
    formData,
  )

  return response.data
}

export async function analyzeResearchPaper(paperId) {
  const response = await apiClient.post(
    `/papers/${paperId}/analyze`,
  )

  return response.data
}
export async function getPaperResults(paperId) {
  const response = await apiClient.get(`/papers/${paperId}`)
  return response.data
}
