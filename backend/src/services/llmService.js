import { ChatOpenAI } from '@langchain/openai'
import { HumanMessage, SystemMessage } from '@langchain/core/messages'
import { env } from '../config/env.js'

function assertLlmConfig() {
  if (!env.llmApiKey) {
    throw new Error('缺少 LLM_API_KEY 或 DASHSCOPE_API_KEY 环境变量')
  }

  if (!env.llmBaseUrl) {
    throw new Error('缺少 LLM_BASE_URL 环境变量')
  }

  if (!env.llmModel) {
    throw new Error('缺少 LLM_MODEL 环境变量')
  }
}

function createChatModel() {
  assertLlmConfig()

  // 这里只把 LangChain 限定在“模型调用层”：
  // controller 仍然只管收参和返回，prompt 仍然由 promptService 维护。
  // 这样后续即使继续接 RAG，也只需要在 service 层往下扩展。
  return new ChatOpenAI({
    apiKey: env.llmApiKey,
    model: env.llmModel,
    temperature: env.llmTemperature,
    maxTokens: env.llmMaxTokens,
    maxRetries: 0,
    configuration: {
      baseURL: env.llmBaseUrl,
    },
  })
}

function buildMessages({ systemPrompt, userPrompt }) {
  return [new SystemMessage(systemPrompt), new HumanMessage(userPrompt)]
}

function normalizeChunkText(content) {
  // LangChain 在不同模型下返回的 content 可能是字符串，
  // 也可能是由多个内容块组成的数组。这里统一提取成纯文本，
  // 这样上层 controller 和前端都不用关心底层差异。
  if (typeof content === 'string') {
    return content
  }

  if (!Array.isArray(content)) {
    return ''
  }

  return content
    .map((item) => {
      if (typeof item === 'string') {
        return item
      }

      if (typeof item?.text === 'string') {
        return item.text
      }

      return ''
    })
    .join('')
}

function formatModelError(error) {
  const reason = error instanceof Error ? error.message : 'unknown error'

  return `LangChain 模型调用失败: baseURL=${env.llmBaseUrl} model=${env.llmModel} reason=${reason}`
}

async function collectStreamReply({ systemPrompt, userPrompt, onChunk }) {
  const model = createChatModel()
  const stream = await model.stream(buildMessages({ systemPrompt, userPrompt }))
  let fullReply = ''

  for await (const chunk of stream) {
    const text = normalizeChunkText(chunk.content)

    if (!text) {
      continue
    }

    fullReply += text

    if (typeof onChunk === 'function') {
      onChunk(text)
    }
  }

  if (!fullReply.trim()) {
    throw new Error('模型流式输出为空')
  }

  return fullReply.trim()
}

export async function generateReply({ systemPrompt, userPrompt }) {
  try {
    // 即使是“普通回复”接口，这里也统一走流式聚合。
    // 原因是你当前使用的部分模型只支持流式 HTTP 调用，
    // 这样可以保证非流式接口和流式接口共用同一套稳定路径。
    return await collectStreamReply({ systemPrompt, userPrompt })
  } catch (error) {
    throw new Error(formatModelError(error))
  }
}

export async function streamReply({ systemPrompt, userPrompt, onChunk }) {
  try {
    return await collectStreamReply({ systemPrompt, userPrompt, onChunk })
  } catch (error) {
    throw new Error(formatModelError(error))
  }
}
