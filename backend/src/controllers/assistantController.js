import { generateReply, streamReply } from '../services/llmService.js'
import { getModeByKey, buildFallbackReply } from '../services/modeService.js'
import { buildPrompts } from '../services/promptService.js'

export async function createReply(req, res) {
  const body = await req.json()
  const mode = body?.mode
  const question = body?.question || ''

  if (!mode) {
    return res.status(400).json({
      ok: false,
      message: 'mode 字段不能为空',
    })
  }

  const modeInfo = getModeByKey(mode)

  if (!modeInfo) {
    return res.status(400).json({
      ok: false,
      message: '不支持的模式',
    })
  }

  // 前端只传 mode 和 question，这里把 mode 转成真正发给模型的提示词。
  // 这样模式规则集中放在 promptService 里，controller 只负责串流程。
  const { systemPrompt, userPrompt } = buildPrompts(mode, question)

  try {
    const reply = await generateReply({ systemPrompt, userPrompt })

    return res.json({
      ok: true,
      data: {
        mode,
        question,
        reply,
      },
    })
  } catch (error) {
    const fallbackReply = buildFallbackReply(mode, question)
    const detail = error instanceof Error ? error.message : 'unknown error'

    console.error('[assistant] model call failed', {
      mode,
      model: modeInfo.key,
      question,
      detail,
    })

    return res.status(502).json({
      ok: false,
      message: '模型接口调用失败',
      detail,
      fallbackReply,
    })
  }
}

export async function createReplyStream(req, res) {
  const body = await req.json()
  const mode = body?.mode
  const question = body?.question || ''

  if (!mode) {
    return res.status(400).json({
      ok: false,
      message: 'mode 字段不能为空',
    })
  }

  const modeInfo = getModeByKey(mode)

  if (!modeInfo) {
    return res.status(400).json({
      ok: false,
      message: '不支持的模式',
    })
  }

  const { systemPrompt, userPrompt } = buildPrompts(mode, question)

  // 这里使用 SSE（Server-Sent Events）返回流式内容。
  // 核心点是：连接不立刻关闭，模型每返回一小段内容，就立刻 write 给前端。
  res
    .status(200)
    .setHeader('Content-Type', 'text/event-stream; charset=utf-8')
    .setHeader('Cache-Control', 'no-cache')
    .setHeader('Connection', 'keep-alive')

  try {
    const reply = await streamReply({
      systemPrompt,
      userPrompt,
      onChunk(chunk) {
        // 每拿到一段增量内容，就推送一个 SSE 事件给前端。
        // 前端收到后可以直接把文本追加到页面上，形成“边生成边显示”的效果。
        res.write(`data: ${JSON.stringify({ type: 'chunk', content: chunk })}\n\n`)
      },
    })

    // 流式结束后，再补一个 done 事件，把完整 reply 一次性发给前端。
    // 这样前端既能实时展示，也能在最后拿完整文本做历史记录持久化。
    res.write(`data: ${JSON.stringify({ type: 'done', reply })}\n\n`)
    res.end()
  } catch (error) {
    const fallbackReply = buildFallbackReply(mode, question)
    const detail = error instanceof Error ? error.message : 'unknown error'

    console.error('[assistant] stream model call failed', {
      mode,
      model: modeInfo.key,
      question,
      detail,
    })

    res.write(
      `data: ${JSON.stringify({
        type: 'error',
        message: '模型接口调用失败',
        detail,
        fallbackReply,
      })}\n\n`
    )
    res.end()
  }
}
