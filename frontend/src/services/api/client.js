async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const rawText = await response.text()
  let data = null

  if (rawText) {
    try {
      data = JSON.parse(rawText)
    } catch {
      throw new Error(`????????? JSON???? ${response.status}`)
    }
  }

  if (!data) {
    throw new Error(`??????????? ${response.status}`)
  }

  if (!response.ok || !data.ok) {
    const error = new Error(data.message || `???????? ${response.status}`)
    error.detail = data.detail || ''
    error.status = response.status
    throw error
  }

  return data.data
}

export const apiClient = {
  get(url, params) {
    const query = params
      ? new URLSearchParams(
          Object.entries(params).reduce((accumulator, [key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
              accumulator[key] = String(value)
            }
            return accumulator
          }, {})
        ).toString()
      : ''

    return request(query ? `${url}?${query}` : url)
  },
  post(url, body) {
    return request(url, {
      method: 'POST',
      body: JSON.stringify(body),
    })
  },
  delete(url) {
    return request(url, {
      method: 'DELETE',
    })
  },
}
