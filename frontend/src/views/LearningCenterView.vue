<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deleteKnowledge, fetchKnowledgeList, generateStudyPlan, uploadKnowledge } from '../services/api/assistant'
import { loadPageState, savePageState } from '../services/pageState'

const route = useRoute()
const router = useRouter()
const savedState = loadPageState('learning-center', {
  activeTopic: '',
  selectedFiles: [],
})
const items = ref([])
const loading = ref(true)
const generatingPlan = ref(false)
const deletingFile = ref('')
const uploading = ref(false)
const uploadVisible = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const activeTopic = ref(savedState.activeTopic)
const selectedFiles = ref(savedState.selectedFiles)
const uploadForm = reactive({
  title: '',
  topic: '自定义资料',
  level: 'beginner',
  tags: '',
  content: '',
})

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

function resetUploadForm() {
  uploadForm.title = ''
  uploadForm.topic = '自定义资料'
  uploadForm.level = 'beginner'
  uploadForm.tags = ''
  uploadForm.content = ''
}

function openUploadModal() {
  uploadVisible.value = true
  errorMessage.value = ''
  successMessage.value = ''
}

function closeUploadModal() {
  uploadVisible.value = false

  if (route.query.upload) {
    router.replace({ name: 'learning' })
  }
}

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    uploadForm.content = String(reader.result || '')
    if (!uploadForm.title) {
      uploadForm.title = file.name.replace(/\.(md|markdown)$/i, '')
    }
  }
  reader.readAsText(file, 'utf-8')
}

async function handleUpload() {
  uploading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const item = await uploadKnowledge({
      ...uploadForm,
      tags: uploadForm.tags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
    })
    items.value = [...items.value, item].sort((a, b) =>
      `${a.topic || ''}${a.title || ''}`.localeCompare(`${b.topic || ''}${b.title || ''}`, 'zh-Hans-CN')
    )
    resetUploadForm()
    closeUploadModal()
    successMessage.value = '资料已上传，会进入你的个人知识库。'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    uploading.value = false
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

async function handleDeleteKnowledge(item) {
  if (item.scope !== 'user' || deletingFile.value) {
    return
  }

  const confirmed = window.confirm(`确定删除“${item.title}”吗？删除后该资料将不再参与知识库检索。`)
  if (!confirmed) {
    return
  }

  deletingFile.value = item.file
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await deleteKnowledge(item.file)
    items.value = items.value.filter((record) => record.file !== item.file)
    selectedFiles.value = selectedFiles.value.filter((file) => file !== item.file)
    successMessage.value = '个人资料已删除。'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    deletingFile.value = ''
  }
}

onMounted(() => {
  loadKnowledge()

  if (route.query.upload === '1') {
    openUploadModal()
  }
})

watch([activeTopic, selectedFiles], () => {
  savePageState('learning-center', {
    activeTopic: activeTopic.value,
    selectedFiles: selectedFiles.value,
  })
})

watch(
  () => route.query.upload,
  (value) => {
    if (value === '1') {
      openUploadModal()
    }
  }
)
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero">
      <div>
        <h2>知识库</h2>
        <p class="panel-desc">浏览本地 Markdown 知识库，答疑时也会检索同一批资料。</p>
      </div>
      <button class="primary-link action-link" type="button" @click="openUploadModal">上传个人资料</button>
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
        <button
          v-if="item.scope === 'user'"
          class="delete-resource-btn"
          type="button"
          :disabled="deletingFile === item.file"
          :title="deletingFile === item.file ? '正在删除' : '删除个人资料'"
          @click.prevent="handleDeleteKnowledge(item)"
        >
          {{ deletingFile === item.file ? '…' : '×' }}
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

    <Transition name="history-fade">
      <div v-if="uploadVisible" class="history-overlay" @click.self="closeUploadModal">
        <section class="history-drawer knowledge-upload-modal">
          <header class="upload-modal-hero">
            <div>
              <span>个人知识库</span>
              <h3>上传个人资料</h3>
              <p>把自己的 Markdown 笔记加入知识库，后续答疑和检索会优先结合你的资料。</p>
            </div>
            <button class="ghost-btn" type="button" @click="closeUploadModal">关闭</button>
          </header>

          <form class="upload-knowledge-form modal-upload-form" @submit.prevent="handleUpload">
            <div class="profile-form-grid">
              <label>
                标题
                <input v-model="uploadForm.title" placeholder="例如：C语言文件操作" required />
              </label>
              <label>
                主题
                <input v-model="uploadForm.topic" placeholder="例如：C语言" />
              </label>
              <label>
                难度
                <select v-model="uploadForm.level">
                  <option value="beginner">beginner</option>
                  <option value="intermediate">intermediate</option>
                  <option value="advanced">advanced</option>
                </select>
              </label>
              <label>
                标签
                <input v-model="uploadForm.tags" placeholder="用英文逗号分隔，例如 file, fopen" />
              </label>
            </div>

            <label class="upload-file-field">
              选择 Markdown 文件
              <input type="file" accept=".md,.markdown,text/markdown,text/plain" @change="handleFileSelect" />
            </label>

            <label>
              Markdown 内容
              <textarea
                v-model="uploadForm.content"
                rows="10"
                placeholder="# 标题&#10;&#10;在这里粘贴你的 Markdown 资料。"
                required
              />
            </label>

            <div class="profile-actions">
              <button class="ghost-btn" type="button" @click="closeUploadModal">取消</button>
              <button class="primary-btn" type="submit" :disabled="uploading">
                {{ uploading ? '上传中...' : '上传资料' }}
              </button>
            </div>
          </form>
        </section>
      </div>
    </Transition>
  </section>
</template>
