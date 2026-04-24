<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  createMistakeEntry,
  deleteMistakeEntry,
  fetchMistakes,
  reorderMistakeEntries,
  updateMistakeEntry,
} from '../services/api/assistant'

const mistakes = ref([])
const loading = ref(true)
const deletingId = ref(null)
const reordering = ref(false)
const draggingId = ref(null)
const createVisible = ref(false)
const editVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const updating = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
let successTimer = null

const form = reactive({
  topic: 'Vue 3',
  question: '',
  note: '',
})

const editForm = reactive({
  topic: '',
  question: '',
  referenceAnswer: '',
  userAnswer: '',
  mistakeType: 'concept',
})

const typeLabels = {
  concept: '概念',
  logic: '逻辑',
  boundary: '边界',
  syntax: '语法',
  expression: '表达',
  debugging: '排查',
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
    showSuccess('已添加知识卡片')
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
    showSuccess('已删除记录')
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    deletingId.value = null
  }
}

function openEditModal(item) {
  editingId.value = item.id
  editForm.topic = item.topic || ''
  editForm.question = item.question || ''
  editForm.referenceAnswer = item.referenceAnswer || ''
  editForm.userAnswer = buildCardNote(item)
  editForm.mistakeType = item.mistakeType || 'concept'
  editVisible.value = true
  errorMessage.value = ''
}

function closeEditModal() {
  editVisible.value = false
  editingId.value = null
  errorMessage.value = ''
}

async function handleUpdate() {
  if (!editingId.value) {
    return
  }

  updating.value = true
  errorMessage.value = ''

  try {
    const record = await updateMistakeEntry(editingId.value, {
      topic: editForm.topic.trim(),
      question: editForm.question.trim(),
      referenceAnswer: editForm.referenceAnswer.trim(),
      userAnswer: editForm.userAnswer.trim(),
      mistakeType: editForm.mistakeType,
    })

    mistakes.value = mistakes.value.map((item) => (item.id === record.id ? record : item))
    closeEditModal()
    showSuccess('已更新知识卡片')
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    updating.value = false
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
    <header class="page-hero compact-hero">
      <div>
        <div class="badge">Review</div>
        <h2>薄弱点</h2>
        <p class="panel-desc">自动沉淀和手动补充的知识卡片。</p>
      </div>
      <button class="primary-link action-link" type="button" @click="createVisible = true">新增</button>
    </header>

    <p v-if="successMessage" class="success-toast" aria-live="polite">{{ successMessage }}</p>

    <section class="panel">
      <div class="section-heading">
        <h3>{{ totalCount }} 条记录</h3>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-if="loading" class="history-empty">
        <p>正在加载...</p>
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
              <button class="icon-btn" type="button" title="编辑记录" @click="openEditModal(item)">
                ✎
              </button>
              <button
                class="icon-btn danger-icon-btn"
                type="button"
                title="删除记录"
                :disabled="deletingId === item.id"
                @click="handleDelete(item.id)"
              >
                {{ deletingId === item.id ? '…' : '×' }}
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
        <p>还没有记录。</p>
      </div>
    </section>

    <transition name="history-fade">
      <div v-if="createVisible" class="history-overlay" @click.self="closeCreateModal">
        <section class="history-drawer create-mistake-modal">
          <div class="section-heading history-head">
            <div>
              <h3>新增知识卡片</h3>
              <p class="panel-desc">填写主题和标题，补充说明可选。</p>
            </div>
            <button class="ghost-btn" type="button" @click="closeCreateModal">关闭</button>
          </div>

          <form class="auth-form" @submit.prevent="handleCreate">
            <label>
              <span>学习主题</span>
              <input v-model="form.topic" type="text" placeholder="例如：Vue 3、Java、Go" />
            </label>

            <label>
              <span>知识点标题</span>
              <textarea v-model="form.question" placeholder="例如：watch 和 watchEffect 怎么区分"></textarea>
            </label>

            <label>
              <span>补充说明</span>
              <textarea v-model="form.note" placeholder="可选。写下当前卡住的地方。"></textarea>
            </label>

            <div class="action-row">
              <button
                class="primary-btn"
                type="submit"
                :disabled="submitting || !form.topic.trim() || !form.question.trim()"
              >
                {{ submitting ? '生成中...' : '保存' }}
              </button>
              <button class="ghost-btn" type="button" @click="closeCreateModal">取消</button>
            </div>
          </form>
        </section>
      </div>
    </transition>

    <transition name="history-fade">
      <div v-if="editVisible" class="history-overlay" @click.self="closeEditModal">
        <section class="history-drawer create-mistake-modal">
          <div class="section-heading history-head">
            <div>
              <h3>编辑知识卡片</h3>
              <p class="panel-desc">修改卡片展示内容，不会重新调用模型。</p>
            </div>
            <button class="ghost-btn" type="button" @click="closeEditModal">关闭</button>
          </div>

          <form class="auth-form" @submit.prevent="handleUpdate">
            <label>
              <span>学习主题</span>
              <input v-model="editForm.topic" type="text" placeholder="例如：Vue 3、Java、Go" />
            </label>

            <label>
              <span>知识点标题</span>
              <textarea v-model="editForm.question" placeholder="例如：watch 和 watchEffect 怎么区分"></textarea>
            </label>

            <label>
              <span>卡片内容</span>
              <textarea v-model="editForm.referenceAnswer" placeholder="写下这个知识点的核心说明"></textarea>
            </label>

            <label>
              <span>个人备注</span>
              <textarea v-model="editForm.userAnswer" placeholder="可选。写下你自己容易混淆的地方。"></textarea>
            </label>

            <label>
              <span>类型</span>
              <select v-model="editForm.mistakeType">
                <option v-for="(label, value) in typeLabels" :key="value" :value="value">
                  {{ label }}
                </option>
              </select>
            </label>

            <div class="action-row">
              <button
                class="primary-btn"
                type="submit"
                :disabled="
                  updating ||
                  !editForm.topic.trim() ||
                  !editForm.question.trim() ||
                  !editForm.referenceAnswer.trim()
                "
              >
                {{ updating ? '保存中...' : '保存修改' }}
              </button>
              <button class="ghost-btn" type="button" @click="closeEditModal">取消</button>
            </div>
          </form>
        </section>
      </div>
    </transition>
  </section>
</template>
