import { addHistoryEntry, clearHistory, listHistory } from '../services/historyService.js'

export function getHistory(_req, res) {
  res.json({
    ok: true,
    data: listHistory(),
  })
}

export async function createHistory(req, res) {
  const body = await req.json()
  const { mode, modeLabel, question, reply } = body || {}

  if (!mode || !question || !reply) {
    return res.status(400).json({
      ok: false,
      message: 'mode、question、reply 字段不能为空',
    })
  }

  const record = addHistoryEntry({
    mode,
    modeLabel: modeLabel || mode,
    question,
    reply,
  })

  return res.status(201).json({
    ok: true,
    data: record,
  })
}

export function removeHistory(_req, res) {
  clearHistory()

  res.json({
    ok: true,
    data: [],
  })
}
