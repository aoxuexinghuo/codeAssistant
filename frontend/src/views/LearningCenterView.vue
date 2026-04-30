<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { fetchKnowledgeList, generateStudyPlan } from '../services/api/assistant'
import { loadPageState, savePageState } from '../services/pageState'

const savedState = loadPageState('learning-center', {
  activeTopic: '',
  selectedFiles: [],
})
const items = ref([])
const loading = ref(true)
const generatingPlan = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const activeTopic = ref(savedState.activeTopic)
const selectedFiles = ref(savedState.selectedFiles)

const topics = computed(() => [...new Set(items.value.map((item) => item.topic).filter(Boolean))])
const filteredItems = computed(() =>
  activeTopic.value ? items.value.filter((item) => item.topic === activeTopic.value) : items.value
)

function initialOf(topic) {
  if (!topic) {
    return 'K'
  }

  if (topic === 'C 语言') {
    return 'C'
  }

  if (topic === 'Vue 3') {
    return 'V3'
  }

  return topic.slice(0, 2)
}

async function loadKnowledge() {
  loading.value = true
  errorMessage.value = ''

  try {
    items.value = await fetchKnowledgeList()
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

function toggleSelected(file) {
  if (selectedFiles.value.includes(file)) {
    selectedFiles.value = selectedFiles.value.filter((item) => item !== file)
    return
  }

  selectedFiles.value = [...selectedFiles.value, file]
}

async function handleGeneratePlan() {
  generatingPlan.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await generateStudyPlan(selectedFiles.value)
    selectedFiles.value = []
    successMessage.value = '学习计划已生成，可在首页查看。'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    generatingPlan.value = false
  }
}

onMounted(() => {
  loadKnowledge()
})

watch([activeTopic, selectedFiles], () => {
  savePageState('learning-center', {
    activeTopic: activeTopic.value,
    selectedFiles: selectedFiles.value,
  })
})
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero">
      <div>
        <div class="badge">Knowledge</div>
        <h2>知识库</h2>
        <p class="panel-desc">浏览本地 Markdown 知识库，答疑时也会检索同一批资料。</p>
      </div>
      <RouterLink to="/learning/upload" class="primary-link">上传个人资料</RouterLink>
    </header>

    <section class="panel knowledge-toolbar">
      <button class="topic-filter" :class="{ active: !activeTopic }" type="button" @click="activeTopic = ''">
        全部
      </button>
      <button
        v-for="topic in topics"
        :key="topic"
        class="topic-filter"
        :class="{ active: activeTopic === topic }"
        type="button"
        @click="activeTopic = topic"
      >
        {{ topic }}
      </button>
    </section>

    <section v-if="selectedFiles.length" class="selection-action-bar">
      <span>已选择 {{ selectedFiles.length }} 项资料</span>
      <button class="ghost-btn" type="button" @click="selectedFiles = []">清空</button>
      <button class="primary-btn" type="button" :disabled="generatingPlan" @click="handleGeneratePlan">
        {{ generatingPlan ? '生成中...' : '生成学习计划' }}
      </button>
    </section>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success-toast">{{ successMessage }}</p>

    <div v-if="loading" class="history-empty">
      <p>正在加载资料...</p>
    </div>

    <section v-else-if="filteredItems.length" class="topic-grid">
      <RouterLink
        v-for="item in filteredItems"
        :key="item.file"
        :to="`/learning/${encodeURIComponent(item.file)}`"
        class="topic-card interactive-card"
        :class="{ selected: selectedFiles.includes(item.file) }"
      >
        <button
          class="select-resource-btn"
          type="button"
          :aria-label="selectedFiles.includes(item.file) ? '取消选择资料' : '选择资料'"
          @click.prevent="toggleSelected(item.file)"
        >
          {{ selectedFiles.includes(item.file) ? '✓' : '+' }}
        </button>
        <div class="topic-initial">{{ initialOf(item.topic) }}</div>
        <div class="topic-content">
          <div class="topic-card-head">
            <strong>{{ item.title }}</strong>
            <span class="row-tag">{{ item.topic }}</span>
          </div>
          <span v-if="item.scope === 'user'" class="topic-pill">个人资料</span>
          <p>{{ item.summary }}</p>
          <span class="topic-action">阅读资料 →</span>
        </div>
      </RouterLink>
    </section>

    <div v-else class="history-empty">
      <p>暂无知识库资料。</p>
    </div>
  </section>
</template>
