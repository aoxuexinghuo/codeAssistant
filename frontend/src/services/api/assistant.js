import { apiClient } from './client'

export function fetchModes() {
  return apiClient.get('/api/modes')
}

export function fetchKnowledgeList() {
  return apiClient.get('/api/knowledge')
}

export function fetchKnowledgeDetail(fileName) {
  return apiClient.get(`/api/knowledge/${encodeURIComponent(fileName)}`)
}

export function fetchReply(payload) {
  return apiClient.post('/api/assistant/reply', payload)
}

export async function streamReply(payload, handlers = {}) {
  const response = await fetch('/api/assistant/reply-stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
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
