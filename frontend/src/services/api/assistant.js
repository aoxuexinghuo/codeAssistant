import { apiClient } from './client'

export function fetchModes() {
  return apiClient.get('/api/modes')
}

export function login(payload) {
  return apiClient.post('/api/auth/login', payload)
}

export function register(payload) {
  return apiClient.post('/api/auth/register', payload)
}

export function fetchProfile() {
  return apiClient.get('/api/profile')
}

export function updateProfile(payload) {
  return apiClient.put('/api/profile', payload)
}

export function resetProfile() {
  return apiClient.post('/api/profile/reset', {})
}

export function fetchProfileInsights() {
  return apiClient.get('/api/profile/insights')
}

export function fetchKnowledgeList() {
  return apiClient.get('/api/knowledge')
}

export function fetchKnowledgeDetail(fileName) {
  return apiClient.get(`/api/knowledge/${encodeURIComponent(fileName)}`)
}

export function uploadKnowledge(payload) {
  return apiClient.post('/api/knowledge', payload)
}

export function fetchStudyPlans() {
  return apiClient.get('/api/study-plans')
}

export function generateStudyPlan(resourceFiles) {
  return apiClient.post('/api/study-plans/generate', { resourceFiles })
}

export function deleteStudyPlan(id) {
  return apiClient.delete(`/api/study-plans/${id}`)
}

export function updateStudyPlanStep(id, stepIndex, completed) {
  return apiClient.put(`/api/study-plans/${id}/steps/${stepIndex}`, { completed })
}

export function fetchReply(payload) {
  return apiClient.post('/api/assistant/reply', payload)
}

export async function streamReply(payload, handlers = {}) {
  return streamEventReply('/api/assistant/reply-stream', payload, handlers)
}

export async function streamRagReply(payload, handlers = {}) {
  return streamEventReply('/api/rag/reply-stream', payload, handlers)
}

async function streamEventReply(url, payload, handlers = {}) {
  const token = localStorage.getItem('programming-assistant-token') || ''
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'X-User-Token': token } : {}),
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok || !response.body) {
    throw new Error('流式请求失败')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()

    if (done) {
      break
    }

    buffer += decoder.decode(value, { stream: true })
    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const event of events) {
      const line = event
        .split('\n')
        .find((item) => item.trim().startsWith('data:'))

      if (!line) {
        continue
      }

      const payloadText = line.trim().slice(5).trim()

      if (!payloadText) {
        continue
      }

      const data = JSON.parse(payloadText)

      if (data.type === 'chunk') {
        handlers.onChunk?.(data.content)
      } else if (data.type === 'done') {
        handlers.onDone?.(data.reply)
      } else if (data.type === 'sources') {
        handlers.onSources?.(data.sources || [])
      } else if (data.type === 'error') {
        handlers.onError?.(data)
      }
    }
  }
}

export function fetchHistory(params) {
  return apiClient.get('/api/history', params)
}

export function createHistoryEntry(payload) {
  return apiClient.post('/api/history', payload)
}

export function clearHistory() {
  return apiClient.delete('/api/history')
}

export function deleteHistoryEntry(id) {
  return apiClient.delete(`/api/history/${id}`)
}

export function fetchMistakes() {
  return apiClient.get('/api/mistakes')
}

export function createMistakeEntry(payload) {
  return apiClient.post('/api/mistakes', payload)
}

export function createMistakesFromAssistant(payload) {
  return apiClient.post('/api/mistakes/from-assistant', payload)
}

export function fetchRagReply(payload) {
  return apiClient.post('/api/rag/reply', payload)
}

export function fetchRagSearch(question) {
  return apiClient.get('/api/rag/search', { q: question })
}

export function rebuildRagIndex() {
  return apiClient.post('/api/rag/rebuild', {})
}

export function deleteMistakeEntry(id) {
  return apiClient.delete(`/api/mistakes/${id}`)
}

export function updateMistakeEntry(id, payload) {
  return apiClient.put(`/api/mistakes/${id}`, payload)
}

export function moveMistakeEntry(id, direction) {
  return apiClient.post(`/api/mistakes/${id}/move`, { direction })
}

export function reorderMistakeEntries(orderedIds) {
  return apiClient.post('/api/mistakes/reorder', { orderedIds })
}
