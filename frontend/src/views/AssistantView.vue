<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AssistantHeader from '../components/assistant/AssistantHeader.vue'
import HistoryDrawer from '../components/assistant/HistoryDrawer.vue'
import QuestionAnswerPanel from '../components/assistant/QuestionAnswerPanel.vue'
import { clearPageStates, loadPageState, savePageState } from '../services/pageState'
import {
  clearHistory,
  createHistoryEntry,
  createMistakesFromAssistant,
  deleteHistoryEntry,
  fetchHistory,
  fetchModes,
  fetchProfile,
  fetchRagSearch,
  streamRagReply,
  streamReply,
} from '../services/api/assistant'

const router = useRouter()
const savedState = loadPageState('assistant', {
  activeMode: '',
  question: '',
  answer: '等待你的提问。',
  autoExtractEnabled: true,
  ragEnabled: false,
  historyKeyword: '',
  historyModeFilter: '',
})
const modes = ref([])
const historyItems = ref([])
const activeMode = ref(savedState.activeMode)
const question = ref(savedState.question)
const answer = ref(savedState.answer)
const loading = ref(false)
const modeLoading = ref(true)
const historyLoading = ref(true)
const clearingHistory = ref(false)
const deletingHistoryId = ref(null)
const historyVisible = ref(false)
const profile = ref(null)
const profileLoading = ref(false)
const historyKeyword = ref(savedState.historyKeyword)
const historyModeFilter = ref(savedState.historyModeFilter)
const errorMessage = ref('')
const autoExtractEnabled = ref(savedState.autoExtractEnabled)
const ragEnabled = ref(savedState.ragEnabled)
const ragSources = ref([])
const ragHits = ref([])
const extractionMessage = ref('')
const extractionState = ref('')
let extractionTimer = null

const modeOptions = computed(() => modes.value)
const currentMode = computed(
  () =>
    modeOptions.value.find((mode) => mode.key === activeMode.value) || {
      key: '',
      label: '加载中',
      description: '正在获取模式配置',
      placeholder: '请稍候',
      tone: '',
    }
)

function showExtractionMessage(message, state) {
  extractionMessage.value = message
  extractionState.value = state

  if (extractionTimer) {
    clearTimeout(extractionTimer)
  }

  extractionTimer = setTimeout(() => {
    extractionMessage.value = ''
    extractionState.value = ''
  }, 2800)
}

async function loadModes() {
  modeLoading.value = true
  errorMessage.value = ''

  try {
    const data = await fetchModes()
    modes.value = data
    activeMode.value = data.some((mode) => mode.key === activeMode.value) ? activeMode.value : data[0]?.key || ''
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    modeLoading.value = false
  }
}

async function loadHistory() {
  historyLoading.value = true

  try {
    historyItems.value = await fetchHistory({
      q: historyKeyword.value.trim(),
      mode: historyModeFilter.value,
      limit: 80,
    })
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    historyLoading.value = false
  }
}

async function loadProfile() {
  profileLoading.value = true

  try {
    const profileData = await fetchProfile()
    profile.value = profileData
    autoExtractEnabled.value = profileData.weakPreference !== '手动记录'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    profileLoading.value = false
  }
}

async function submitQuestion() {
  if (!activeMode.value) {
    return
  }

  loading.value = true
  errorMessage.value = ''
  extractionMessage.value = ''
  extractionState.value = ''
  ragSources.value = []
  ragHits.value = []
  answer.value = ''

  try {
    let finalReply = ''

    if (ragEnabled.value) {
      const searchQuestion = question.value.trim()
      await streamRagReply(
        {
          question: searchQuestion,
        },
        {
          onSources(sources) {
            ragSources.value = sources
          },
          onChunk(chunk) {
            answer.value += chunk
          },
          onDone(reply) {
            finalReply = reply
            answer.value = reply
          },
          onError(data) {
            errorMessage.value = data.detail || data.message || '知识库增强回答失败'
          },
        }
      )

      try {
        ragHits.value = await fetchRagSearch(searchQuestion)
      } catch (error) {
        console.warn('[rag-search] failed', {
          message: error?.message,
          detail: error?.detail,
          status: error?.status,
        })
      }
    } else {
      await streamReply(
        {
          mode: activeMode.value,
          question: question.value.trim(),
        },
        {
          onChunk(chunk) {
            answer.value += chunk
          },
          onDone(reply) {
            finalReply = reply
            answer.value = reply
          },
          onError(data) {
            errorMessage.value = data.detail || data.message || '流式输出失败'

            if (data.fallbackReply) {
              answer.value = data.fallbackReply
              finalReply = data.fallbackReply
            }
          },
        }
      )
    }

    if (!finalReply.trim()) {
      finalReply = answer.value
    }

    if (!finalReply.trim()) {
      throw new Error('模型没有返回有效内容')
    }

    const currentLabel = currentMode.value.label || activeMode.value
    const record = await createHistoryEntry({
      mode: activeMode.value,
      modeLabel: currentLabel,
      question: question.value.trim(),
      reply: finalReply,
    })

    const keyword = historyKeyword.value.trim()
    const modeMatched = !historyModeFilter.value || historyModeFilter.value === record.mode
    const keywordMatched = !keyword || record.question.includes(keyword) || record.reply.includes(keyword)

    if (modeMatched && keywordMatched) {
      historyItems.value = [record, ...historyItems.value]
    }

    if (autoExtractEnabled.value) {
      try {
        const records = await createMistakesFromAssistant({
          question: question.value.trim(),
          reply: finalReply,
        })
        const count = Array.isArray(records) ? records.length : 0

        if (count > 0) {
          showExtractionMessage(`已自动沉淀 ${count} 条薄弱点`, 'success')
        } else {
          showExtractionMessage('本轮未识别到明显薄弱点', 'neutral')
        }
      } catch (error) {
        console.error('[mistake-extraction] failed', {
          message: error?.message,
          detail: error?.detail,
          status: error?.status,
        })
        showExtractionMessage('薄弱点沉淀失败', 'error')
      }
    }
  } catch (error) {
    if (!errorMessage.value) {
      errorMessage.value = error.message
    }
  } finally {
    loading.value = false
  }
}

async function handleClearHistory() {
  clearingHistory.value = true
  errorMessage.value = ''

  try {
    await clearHistory()
    historyItems.value = []
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    clearingHistory.value = false
  }
}

async function handleDeleteHistory(id) {
  deletingHistoryId.value = id
  errorMessage.value = ''

  try {
    await deleteHistoryEntry(id)
    historyItems.value = historyItems.value.filter((item) => item.id !== id)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    deletingHistoryId.value = null
  }
}

function reuseQuestion(savedQuestion) {
  question.value = savedQuestion
  historyVisible.value = false
}

function logout() {
  clearPageStates()
  localStorage.removeItem('programming-assistant-token')
  localStorage.removeItem('programming-assistant-user')
  router.push('/auth/login')
}

watch(historyModeFilter, () => {
  if (historyVisible.value) {
    loadHistory()
  }
})

watch(
  [activeMode, question, answer, autoExtractEnabled, ragEnabled, historyKeyword, historyModeFilter],
  () => {
    savePageState('assistant', {
      activeMode: activeMode.value,
      question: question.value,
      answer: answer.value,
      autoExtractEnabled: autoExtractEnabled.value,
      ragEnabled: ragEnabled.value,
      historyKeyword: historyKeyword.value,
      historyModeFilter: historyModeFilter.value,
    })
  },
  { deep: true }
)

onMounted(() => {
  loadModes()
  loadHistory()
  loadProfile()
})
</script>

<template>
  <main class="assistant-page">
    <AssistantHeader
      :history-count="historyItems.length || 0"
      @logout="logout"
      @toggle-history="historyVisible = !historyVisible"
    />
    <HistoryDrawer
      :items="historyItems"
      :visible="historyVisible"
      :clearing="clearingHistory"
      :deleting-id="deletingHistoryId"
      :loading="historyLoading"
      :search-keyword="historyKeyword"
      :selected-mode="historyModeFilter"
      :mode-options="modeOptions"
      @reuse-question="reuseQuestion"
      @clear="handleClearHistory"
      @delete-history="handleDeleteHistory"
      @search="loadHistory"
      @update:search-keyword="historyKeyword = $event"
      @update:selected-mode="historyModeFilter = $event"
      @close="historyVisible = false"
    />

    <section class="assistant-main solo-layout">
      <QuestionAnswerPanel
        :modes="modeOptions"
        :active-mode="activeMode"
        :current-mode="currentMode"
        :question="question"
        :answer="answer"
        :loading="loading"
        :mode-loading="modeLoading"
        :error-message="errorMessage"
        :auto-extract-enabled="autoExtractEnabled"
        :rag-enabled="ragEnabled"
        :rag-sources="ragSources"
        :rag-hits="ragHits"
        :extraction-message="extractionMessage"
        :extraction-state="extractionState"
        @update:question="question = $event"
        @update:auto-extract-enabled="autoExtractEnabled = $event"
        @update:rag-enabled="ragEnabled = $event"
        @select-mode="activeMode = $event"
        @submit="submitQuestion"
      />
    </section>
  </main>
</template>
