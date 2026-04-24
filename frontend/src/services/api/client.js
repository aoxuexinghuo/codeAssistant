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
      throw new Error(`接口返回的不是合法 JSON，状态码 ${response.status}`)
    }
  }

  if (!data) {
    throw new Error(`接口返回空响应，状态码 ${response.status}`)
  }

  if (!response.ok || !data.ok) {
    const error = new Error(data.message || `请求失败，状态码 ${response.status}`)
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
  put(url, body) {
    return request(url, {
      method: 'PUT',
      body: JSON.stringify(body),
    })
  },
  delete(url) {
    return request(url, {
      method: 'DELETE',
    })
  },
}
