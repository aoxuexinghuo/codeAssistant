<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadKnowledge } from '../services/api/assistant'

const router = useRouter()
const uploading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const uploadForm = ref({
  title: '',
  topic: '自定义资料',
  level: 'beginner',
  tags: '',
  content: '',
})

async function handleUpload() {
  uploading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await uploadKnowledge({
      ...uploadForm.value,
      tags: uploadForm.value.tags
        .split(',')
        .map((tag) => tag.trim())
        .filter(Boolean),
    })
    successMessage.value = '资料已上传，会进入你的个人知识库。'
    setTimeout(() => {
      router.push('/learning')
    }, 650)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    uploading.value = false
  }
}

function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (!file) {
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    uploadForm.value.content = String(reader.result || '')
    if (!uploadForm.value.title) {
      uploadForm.value.title = file.name.replace(/\.(md|markdown)$/i, '')
    }
  }
  reader.readAsText(file, 'utf-8')
}
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero upload-hero">
      <div>
        <div class="badge">Upload</div>
        <h2>上传个人资料</h2>
        <p class="panel-desc">把自己的 Markdown 笔记加入个人知识库，答疑时也会参与检索。</p>
      </div>
      <RouterLink to="/learning" class="ghost-btn">返回知识库</RouterLink>
    </header>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success-toast">{{ successMessage }}</p>

    <section class="panel upload-knowledge-panel upload-page-panel">
      <div class="section-heading">
        <h3>资料信息</h3>
        <p class="panel-desc">资料只会保存在当前登录用户的个人知识库中。</p>
      </div>
      <form class="upload-knowledge-form" @submit.prevent="handleUpload">
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
        <label>
          选择 Markdown 文件
          <input type="file" accept=".md,.markdown,text/markdown,text/plain" @change="handleFileSelect" />
        </label>
        <label>
          Markdown 内容
          <textarea
            v-model="uploadForm.content"
            rows="12"
            placeholder="# 标题&#10;&#10;在这里粘贴你的 Markdown 资料。"
            required
          />
        </label>
        <div class="profile-actions">
          <RouterLink to="/learning" class="ghost-btn">取消</RouterLink>
          <button class="primary-btn" type="submit" :disabled="uploading">
            {{ uploading ? '上传中...' : '上传资料' }}
          </button>
        </div>
      </form>
    </section>
  </section>
</template>
