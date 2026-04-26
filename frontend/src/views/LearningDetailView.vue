<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownRenderer from '../components/common/MarkdownRenderer.vue'
import { fetchKnowledgeDetail } from '../services/api/assistant'

const route = useRoute()
const resource = ref(null)
const loading = ref(true)
const errorMessage = ref('')

async function loadResource() {
  loading.value = true
  errorMessage.value = ''

  try {
    resource.value = await fetchKnowledgeDetail(route.params.slug)
  } catch (error) {
    resource.value = null
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

watch(() => route.params.slug, loadResource)

onMounted(() => {
  loadResource()
})
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero" v-if="resource">
      <div>
        <div class="badge">Knowledge</div>
        <h2>{{ resource.title }}</h2>
        <p class="panel-desc">{{ resource.summary }}</p>
      </div>
      <span class="topic-pill">{{ resource.topic }}</span>
    </header>

    <header class="page-hero compact-hero" v-else>
      <div>
        <div class="badge">Knowledge</div>
        <h2>{{ loading ? '正在加载资料' : '资料不存在' }}</h2>
        <p class="panel-desc">{{ loading ? '请稍候。' : errorMessage || '未找到对应资料。' }}</p>
      </div>
      <RouterLink to="/learning" class="primary-link">返回学习中心</RouterLink>
    </header>

    <article v-if="resource" class="panel knowledge-detail-card">
      <MarkdownRenderer :content="resource.content" />
    </article>
  </section>
</template>
