<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { loadPageState, savePageState } from '../services/pageState'
import {
  createMistakeEntry,
  deleteMistakeEntry,
  fetchMistakes,
  generateMistakeReviewQuestion,
  reorderMistakeEntries,
  updateMistakeEntry,
  updateMistakeReview,
} from '../services/api/assistant'

const savedState = loadPageState('mistakes', {
  searchKeyword: '',
  topicFilter: '',
  typeFilter: '',
})
const mistakes = ref([])
const loading = ref(true)
const deletingId = ref(null)
const reordering = ref(false)
const draggingId = ref(null)
const createVisible = ref(false)
const editVisible = ref(false)
const reviewVisible = ref(false)
const editingId = ref(null)
const reviewingId = ref(null)
const submitting = ref(false)
const updating = ref(false)
const reviewing = ref(false)
const generatingQuestion = ref(false)
const reviewQuestion = ref(null)
const reviewQuestionCache = ref({})
const errorMessage = ref('')
const successMessage = ref('')
const searchKeyword = ref(savedState.searchKeyword)
const topicFilter = ref(savedState.topicFilter)
const typeFilter = ref(savedState.typeFilter)
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

const reviewForm = reactive({
  status: 'reviewing',
  answer: '',
})

const typeLabels = {
  concept: '概念',
  logic: '逻辑',
  boundary: '边界',
  syntax: '语法',
  expression: '表达',
  debugging: '排查',
}

const reviewStatusLabels = {
  pending: '待复盘',
  reviewing: '复盘中',
  mastered: '已掌握',
}

const totalCount = computed(() => mistakes.value.length)
const topicOptions = computed(() => [...new Set(mistakes.value.map((item) => item.topic).filter(Boolean))])
const filteredMistakes = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  return mistakes.value.filter((item) => {
    const text = [
      item.topic,
      item.question,
      item.referenceAnswer,
      item.mistakeReason,
      item.improvementSuggestion,
      item.userAnswer,
    ]
      .join(' ')
      .toLowerCase()
    const keywordMatched = !keyword || text.includes(keyword)
    const topicMatched = !topicFilter.value || item.topic === topicFilter.value
    const typeMatched = !typeFilter.value || item.mistakeType === typeFilter.value

    return keywordMatched && topicMatched && typeMatched
  })
})

function sortMistakes(items) {
  return [...items].sort((a, b) => {
    const masteredA = a.reviewStatus === 'mastered' ? 1 : 0
    const masteredB = b.reviewStatus === 'mastered' ? 1 : 0

    if (masteredA !== masteredB) {
      return masteredA - masteredB
    }

    return (a.sortOrder || 0) - (b.sortOrder || 0)
  })
}

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
    mistakes.value = sortMistakes(await fetchMistakes())
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

    mistakes.value = sortMistakes([...mistakes.value, record])
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

async function openReviewModal(item) {
  reviewingId.value = item.id
  reviewForm.status = item.reviewStatus === 'mastered' ? 'mastered' : 'reviewing'
  reviewForm.answer = item.reviewNote || ''
  reviewQuestion.value = reviewQuestionCache.value[item.id] || null
  reviewVisible.value = true
  errorMessage.value = ''

  if (!reviewQuestion.value) {
    await loadReviewQuestion(item.id)
  }
}

function closeReviewModal() {
  reviewVisible.value = false
  reviewingId.value = null
  reviewQuestion.value = null
  errorMessage.value = ''
}

async function loadReviewQuestion(id = reviewingId.value, force = false) {
  if (!id) {
    return
  }

  if (!force && reviewQuestionCache.value[id]) {
    reviewQuestion.value = reviewQuestionCache.value[id]
    return
  }

  generatingQuestion.value = true
  errorMessage.value = ''

  try {
    reviewQuestion.value = await generateMistakeReviewQuestion(id)
    reviewQuestionCache.value = {
      ...reviewQuestionCache.value,
      [id]: reviewQuestion.value,
    }
  } catch (error) {
    errorMessage.value = error.message
    reviewQuestion.value = {
      question: '请用自己的话说明这个知识点的关键结论。',
      hint: '先说概念，再说易错点，最后补一个最小例子。',
      expectedAnswer: '',
      checkpoints: ['能说清核心概念', '能指出一个易错点', '能给出一个最小例子'],
    }
    reviewQuestionCache.value = {
      ...reviewQuestionCache.value,
      [id]: reviewQuestion.value,
    }
  } finally {
    generatingQuestion.value = false
  }
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

    mistakes.value = sortMistakes(mistakes.value.map((item) => (item.id === record.id ? record : item)))
    closeEditModal()
    showSuccess('已更新知识卡片')
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    updating.value = false
  }
}

async function handleReviewUpdate(nextStatus = reviewForm.status) {
  if (!reviewingId.value) {
    return
  }

  reviewing.value = true
  errorMessage.value = ''

  try {
    const result = await updateMistakeReview(reviewingId.value, {
      status: nextStatus,
      reviewNote: reviewForm.answer.trim(),
    })
    const record = result.record || result
    mistakes.value = sortMistakes(mistakes.value.map((item) => (item.id === record.id ? record : item)))
    closeReviewModal()
    showSuccess(result.awardedPoints ? `已标记掌握，获得 ${result.awardedPoints} 积分` : '复盘记录已保存')
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    reviewing.value = false
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

function reviewStatusLabel(status) {
  return reviewStatusLabels[status] || '待复盘'
}

onMounted(() => {
  loadMistakes()
})

watch([searchKeyword, topicFilter, typeFilter], () => {
  savePageState('mistakes', {
    searchKeyword: searchKeyword.value,
    topicFilter: topicFilter.value,
    typeFilter: typeFilter.value,
  })
})
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero mistake-hero">
      <div>
        <h2>薄弱点卡片</h2>
        <p class="panel-desc">把答疑中暴露出的知识点整理成可复盘的卡片。</p>
      </div>
      <button class="primary-link action-link" type="button" @click="createVisible = true">新增</button>
    </header>

    <p v-if="successMessage" class="success-toast" aria-live="polite">{{ successMessage }}</p>

    <section class="panel">
      <div class="mistake-board-head">
        <div>
          <h3>{{ filteredMistakes.length }} / {{ totalCount }} 条记录</h3>
          <p class="panel-desc">支持搜索、筛选和拖拽排序。</p>
        </div>
        <div class="mistake-filters">
          <input v-model="searchKeyword" type="text" placeholder="搜索知识点" />
          <select v-model="topicFilter">
            <option value="">全部主题</option>
            <option v-for="topic in topicOptions" :key="topic" :value="topic">{{ topic }}</option>
          </select>
          <select v-model="typeFilter">
            <option value="">全部类型</option>
            <option v-for="(label, value) in typeLabels" :key="value" :value="value">{{ label }}</option>
          </select>
        </div>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-if="loading" class="history-empty">
        <p>正在加载...</p>
      </div>

      <div v-else-if="filteredMistakes.length" class="mistake-grid">
        <article
          v-for="item in filteredMistakes"
          :key="item.id"
          class="mistake-card"
          :class="{ 'is-dragging': draggingId === item.id, 'is-mastered': item.reviewStatus === 'mastered' }"
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
                <span class="review-status-pill" :class="`is-${item.reviewStatus || 'pending'}`">
                  {{ reviewStatusLabel(item.reviewStatus) }}
                </span>
              </div>
            </div>
            <div class="mistake-actions">
              <button class="icon-btn review-icon-btn" type="button" title="AI 复盘" @click="openReviewModal(item)">
                练
              </button>
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
            <p v-if="item.reviewNote" class="mistake-review-note">复盘：{{ item.reviewNote }}</p>
          </div>
        </article>
      </div>

      <div v-else class="history-empty">
        <p>{{ mistakes.length ? '没有匹配的知识卡片。' : '还没有记录。' }}</p>
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
      <div v-if="reviewVisible" class="history-overlay" @click.self="closeReviewModal">
        <section class="history-drawer review-modal">
          <div class="review-modal-hero">
            <div>
              <span>AI 复盘</span>
              <h3>回答一个小问题，确认是否真的掌握</h3>
              <p>系统会根据这张薄弱点卡片生成一道短问题。完成作答后标记掌握，可获得 2 积分。</p>
            </div>
            <button class="ghost-btn" type="button" @click="closeReviewModal">关闭</button>
          </div>

          <div class="review-question-card">
            <div class="review-question-head">
              <span>{{ generatingQuestion ? '生成中' : '复盘题' }}</span>
              <button class="ghost-btn compact-btn" type="button" :disabled="generatingQuestion" @click="loadReviewQuestion(reviewingId, true)">
                换一题
              </button>
            </div>

            <div v-if="generatingQuestion" class="review-skeleton">
              <i></i>
              <i></i>
              <i></i>
            </div>

            <template v-else>
              <strong>{{ reviewQuestion?.question }}</strong>
              <p>{{ reviewQuestion?.hint }}</p>
              <div v-if="reviewQuestion?.checkpoints?.length" class="review-checkpoints">
                <span v-for="point in reviewQuestion.checkpoints" :key="point">{{ point }}</span>
              </div>
            </template>
          </div>

          <form class="review-answer-panel" @submit.prevent="handleReviewUpdate()">
            <label>
              <span>我的回答</span>
              <textarea
                v-model="reviewForm.answer"
                rows="5"
                placeholder="不用写很长。用自己的话答出关键点、易错点或一个最小例子即可。"
              ></textarea>
            </label>

            <details v-if="reviewQuestion?.expectedAnswer" class="review-reference">
              <summary>查看参考答案</summary>
              <p>{{ reviewQuestion.expectedAnswer }}</p>
            </details>

            <div class="review-action-row">
              <button class="primary-btn" type="button" :disabled="reviewing" @click="handleReviewUpdate('mastered')">
                {{ reviewing ? '保存中...' : '标记掌握 +2 积分' }}
              </button>
              <button class="ghost-btn" type="button" :disabled="reviewing" @click="handleReviewUpdate('reviewing')">
                {{ reviewing ? '保存中...' : '保存当前复盘' }}
              </button>
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
