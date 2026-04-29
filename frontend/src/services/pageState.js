const PREFIX = 'programming-assistant-page-state:'

export function loadPageState(key, fallback = {}) {
  try {
    const rawValue = sessionStorage.getItem(`${PREFIX}${key}`)
    return rawValue ? { ...fallback, ...JSON.parse(rawValue) } : fallback
  } catch {
    return fallback
  }
}

export function savePageState(key, value) {
  try {
    sessionStorage.setItem(`${PREFIX}${key}`, JSON.stringify(value))
  } catch {
    // 状态保存失败不应影响主流程。
  }
}

export function clearPageStates() {
  Object.keys(sessionStorage)
    .filter((key) => key.startsWith(PREFIX))
    .forEach((key) => sessionStorage.removeItem(key))
}
