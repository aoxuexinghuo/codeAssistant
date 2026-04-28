<script setup>
import { computed, onMounted, ref } from 'vue'
import { fetchKnowledgeList } from '../services/api/assistant'

const items = ref([])
const loading = ref(true)
const errorMessage = ref('')
const activeTopic = ref('')

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

onMounted(() => {
  loadKnowledge()
})
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero">
      <div>
        <div class="badge">Knowledge</div>
        <h2>学习中心</h2>
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

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <div v-if="loading" class="history-empty">
      <p>正在加载资料...</p>
    </div>

    <section v-else-if="filteredItems.length" class="topic-grid">
      <RouterLink
        v-for="item in filteredItems"
        :key="item.file"
        :to="`/learning/${encodeURIComponent(item.file)}`"
        class="topic-card interactive-card"
      >
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
