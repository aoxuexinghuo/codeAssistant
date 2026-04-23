const sessionHistory = []
let nextId = 1

export function listHistory() {
  // 前端历史列表默认想看到最新记录，所以这里直接按“最新在前”返回。
  return [...sessionHistory].reverse()
}

export function addHistoryEntry(entry) {
  // 当前历史记录只存在内存里，没有落数据库。
  // 所以后端服务一重启，历史就会清空。这是当前版本的刻意简化。
  const record = {
    id: nextId++,
    mode: entry.mode,
    modeLabel: entry.modeLabel,
    question: entry.question,
    reply: entry.reply,
    createdAt: new Date().toISOString(),
  }

  sessionHistory.push(record)

  return record
}

export function clearHistory() {
  sessionHistory.length = 0
}
