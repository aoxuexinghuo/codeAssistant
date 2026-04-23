export const env = {
  port: Number(process.env.PORT || 3000),
  llmApiKey: process.env.LLM_API_KEY || process.env.DASHSCOPE_API_KEY || '',
  llmBaseUrl: process.env.LLM_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  llmModel: process.env.LLM_MODEL || 'qvq-max-2025-03-25',
  llmTemperature: Number(process.env.LLM_TEMPERATURE || 0.7),
  llmMaxTokens: Number(process.env.LLM_MAX_TOKENS || 1200),
}
