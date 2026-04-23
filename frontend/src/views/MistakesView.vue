<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  createMistakeEntry,
  deleteMistakeEntry,
  fetchMistakes,
  reorderMistakeEntries,
} from '../services/api/assistant'

const mistakes = ref([])
const loading = ref(true)
const deletingId = ref(null)
const reordering = ref(false)
const draggingId = ref(null)
const createVisible = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
let successTimer = null

const form = reactive({
  topic: 'Vue 3',
  question: '',
  note: '',
})

const typeLabels = {
  concept: '概念不清',
  logic: '逻辑错误',
  boundary: '边界遗漏',
  syntax: '语法 / API',
  expression: '表达不足',
  debugging: '排查思路',
}

const totalCount = computed(() => mistakes.value.length)

function buildCardSummary(item) {
  const parts = [item.referenceAnswer, item.mistakeReason, item.improvementSuggestion]
    .map((value) => (value || '').trim())
    .filter(Boolean)

  return parts.join(' ')
}

function buildCardNote(item) {
  const note = (item.userAnswer || '').trim()

  if (!note || note === '来自一次答疑过程的自动提炼。') {
    return ''
  }

  return note
}

function showSuccess(message) {
  successMessage.value = message

  if (successTimer) {
    clearTimeout(successTimer)
  }

  successTimer = setTimeout(() => {
    successMessage.value = ''
  }, 2400)
}

async function loadMistakes() {
  loading.value = true

  try {
    mistakes.value = await fetchMistakes()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  submitting.value = true
  errorMessage.value = ''

  try {
    const record = await createMistakeEntry({
      topic: form.topic.trim(),
      question: form.question.trim(),
      note: form.note.trim(),
    })

    mistakes.value = [...mistakes.value, record].sort((a, b) => a.sortOrder - b.sortOrder)
    createVisible.value = false
    form.question = ''
    form.note = ''
    showSuccess('已添加一条知识点卡片')
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    submitting.value = false
  }
}

async function handleDelete(id) {
  deletingId.value = id
  errorMessage.value = ''

  try {
    await deleteMistakeEntry(id)
    mistakes.value = mistakes.value.filter((item) => item.id !== id)
    showSuccess('已删除该记录')
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    deletingId.value = null
  }
}

function handleDragStart(id) {
  draggingId.value = id
}

function handleDragOver(event) {
  event.preventDefault()
}

async function handleDrop(targetId) {
  if (!draggingId.value || draggingId.value === targetId) {
    draggingId.value = null
    return
  }

  const sourceIndex = mistakes.value.findIndex((item) => item.id === draggingId.value)
  const targetIndex = mistakes.value.findIndex((item) => item.id === targetId)

  if (sourceIndex === -1 || targetIndex === -1) {
    draggingId.value = null
    return
  }

  const nextItems = [...mistakes.value]
  const [movedItem] = nextItems.splice(sourceIndex, 1)
  nextItems.splice(targetIndex, 0, movedItem)

  mistakes.value = nextItems
  draggingId.value = null
  reordering.value = true
  errorMessage.value = ''

  try {
    mistakes.value = await reorderMistakeEntries(nextItems.map((item) => item.id))
  } catch (error) {
    errorMessage.value = error.message
    await loadMistakes()
  } finally {
    reordering.value = false
  }
}

function handleDragEnd() {
  draggingId.value = null
}

function closeCreateModal() {
  createVisible.value = false
  errorMessage.value = ''
}

function typeLabel(type) {
  return typeLabels[type] || type
}

onMounted(() => {
  loadMistakes()
})
</script>

<template>
  <section class="page-stack">
    <header class="page-hero">
      <div>
        <div class="badge">Mistake Book</div>
        <h2>知识薄弱点记录</h2>
        <p class="panel-desc">系统会在答疑过程中自动沉淀薄弱点，你也可以手动补充重点记录。</p>
      </div>
      <button class="primary-link action-link" type="button" @click="createVisible = true">手动补充记录</button>
    </header>

    <p v-if="successMessage" class="success-toast" aria-live="polite">{{ successMessage }}</p>

    <section class="panel">
      <div class="section-heading">
        <h3>薄弱点列表</h3>
        <p class="panel-desc">当前共 {{ totalCount }} 条，拖动左侧手柄即可排序，右侧图标可直接删除。</p>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-if="loading" class="history-empty">
        <p>正在加载知识薄弱点...</p>
      </div>

      <div v-else-if="mistakes.length" class="card-list">
        <article
          v-for="item in mistakes"
          :key="item.id"
          class="mistake-card"
          :class="{ 'is-dragging': draggingId === item.id }"
          @dragover="handleDragOver"
          @drop="handleDrop(item.id)"
        >
          <div class="mistake-card-head">
            <div class="mistake-card-leading">
              <button
                class="icon-btn drag-handle"
                type="button"
                draggable="true"
                title="拖动排序"
                :disabled="reordering"
                @dragstart="handleDragStart(item.id)"
                @dragend="handleDragEnd"
              >
                ⋮⋮
              </button>
              <div class="mistake-badges">
                <span class="row-tag">{{ item.topic }}</span>
                <span class="topic-pill">{{ typeLabel(item.mistakeType) }}</span>
              </div>
            </div>
            <div class="mistake-actions">
              <button
                class="icon-btn danger-icon-btn"
                type="button"
                title="删除记录"
                :disabled="deletingId === item.id"
                @click="handleDelete(item.id)"
              >
                {{ deletingId === item.id ? '…' : '✕' }}
              </button>
            </div>
          </div>

          <div class="mistake-card-body">
            <strong>{{ item.question }}</strong>
            <p>{{ buildCardSummary(item) }}</p>
            <p v-if="buildCardNote(item)" class="mistake-note">{{ buildCardNote(item) }}</p>
          </div>
        </article>
      </div>

      <div v-else class="history-empty">
        <p>还没有记录。你可以先去答疑页面提问，或者手动补充一条重点知识薄弱点。</p>
      </div>
    </section>

    <transition name="history-fade">
      <div v-if="createVisible" class="history-overlay" @click.self="closeCreateModal">
        <section class="history-drawer create-mistake-modal">
          <div class="section-heading history-head">
            <div>
              <h3>手动补充记录</h3>
              <p class="panel-desc">现在只需要填写主题、标题和补充说明，系统会自动补全知识说明与建议。</p>
            </div>
            <div class="history-actions">
              <button class="ghost-btn" type="button" @click="closeCreateModal">关闭</button>
            </div>
          </div>

          <form class="auth-form" @submit.prevent="handleCreate">
            <label>
              <span>学习主题</span>
              <input v-model="form.topic" type="text" placeholder="例如：Vue 3、Java、Go" />
            </label>

            <label>
              <span>知识点标题</span>
              <textarea v-model="form.question" placeholder="例如：reactive 解构后为什么会失去响应式"></textarea>
            </label>

            <label>
              <span>补充说明</span>
              <textarea v-model="form.note" placeholder="可选。写下你目前卡住的地方，或你想补充的背景。"></textarea>
            </label>

            <div class="action-row">
              <button
                class="primary-btn"
                type="submit"
                :disabled="submitting || !form.topic.trim() || !form.question.trim()"
              >
                {{ submitting ? '正在生成知识点卡片...' : '保存记录' }}
              </button>
              <button class="ghost-btn" type="button" @click="closeCreateModal">取消</button>
            </div>
          </form>
        </section>
      </div>
    </transition>
  </section>
</template>
