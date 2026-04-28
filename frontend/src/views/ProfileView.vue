<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { fetchProfile, fetchProfileInsights, resetProfile, updateProfile } from '../services/api/assistant'

const profile = ref(null)
const insights = ref(null)
const loading = ref(true)
const saving = ref(false)
const message = ref('')
const errorMessage = ref('')

const form = reactive({
  nickname: '',
  level: '初级',
  focus: 'C语言',
  goal: '课程学习',
  answerStyle: '简洁直接',
  weakPreference: '自动记录',
})

const levelOptions = ['零基础', '初级', '中级', '面试准备']
const focusOptions = ['C语言', 'Java', 'Python', 'Go', 'Rust', 'Vue 3', '算法']
const goalOptions = ['课程学习', '期末考试', '毕设开发', '面试准备', '项目实践']
const styleOptions = ['简洁直接', '多举例', '逐步引导', '少给完整代码']
const weakOptions = ['自动记录', '只在明显薄弱时记录', '手动记录']

const topicDistribution = computed(() => insights.value?.topicDistribution || [])
const abilityScores = computed(() => insights.value?.abilityScores || [])
const recentWeakPoints = computed(() => insights.value?.recentWeakPoints || [])
const strategyTips = computed(() => insights.value?.strategyTips || [])

const maxTopicValue = computed(() => Math.max(...topicDistribution.value.map((item) => item.value), 1))
const topTopic = computed(() => topicDistribution.value[0]?.name || form.focus)
const learningPulse = computed(() => {
  const questions = insights.value?.questionCount || 0
  const mistakes = insights.value?.mistakeCount || 0
  return Math.min(96, 38 + questions * 3 + mistakes * 2)
})

function syncForm(nextProfile) {
  form.nickname = nextProfile?.nickname || ''
  form.level = nextProfile?.level || '初级'
  form.focus = nextProfile?.focus || 'C语言'
  form.goal = nextProfile?.goal || '课程学习'
  form.answerStyle = nextProfile?.answerStyle || '简洁直接'
  form.weakPreference = nextProfile?.weakPreference || '自动记录'
}

async function loadProfilePage() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [profileData, insightsData] = await Promise.all([fetchProfile(), fetchProfileInsights()])
    profile.value = profileData
    insights.value = insightsData
    syncForm(profileData)
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  message.value = ''
  errorMessage.value = ''

  try {
    profile.value = await updateProfile({ ...form })
    insights.value = await fetchProfileInsights()
    syncForm(profile.value)
    message.value = '学习档案已更新'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}

async function handleReset() {
  saving.value = true
  message.value = ''
  errorMessage.value = ''

  try {
    profile.value = await resetProfile()
    insights.value = await fetchProfileInsights()
    syncForm(profile.value)
    message.value = '已恢复默认画像'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    saving.value = false
  }
}

function ringStyle(value) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0))
  return {
    background: `conic-gradient(#256f61 ${safeValue * 3.6}deg, #e3eee9 0deg)`,
  }
}

function bubbleStyle(item, index) {
  const size = 76 + (item.value / maxTopicValue.value) * 76
  const positions = [
    ['8%', '18%'],
    ['52%', '6%'],
    ['34%', '46%'],
    ['70%', '42%'],
    ['12%', '66%'],
    ['58%', '70%'],
  ]
  const [left, top] = positions[index % positions.length]

  return {
    width: `${size}px`,
    height: `${size}px`,
    left,
    top,
  }
}

onMounted(() => {
  loadProfilePage()
})
</script>

<template>
  <section class="page-stack profile-page">
    <header class="page-hero profile-hero">
      <div>
        <div class="badge">Profile</div>
        <h2>学习档案</h2>
        <p class="panel-desc">把你的学习偏好、近期状态和系统个性化策略集中展示。</p>
      </div>
      <RouterLink to="/assistant" class="primary-link">去提问</RouterLink>
    </header>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    <p v-if="message" class="success-toast">{{ message }}</p>

    <section class="profile-dashboard">
      <article class="profile-glass-card profile-id-card">
        <div class="profile-orbit">
          <span></span>
          <strong>{{ learningPulse }}</strong>
          <small>学习活跃度</small>
        </div>
        <div>
          <p class="badge">Learner</p>
          <h3>{{ form.nickname || '学习者' }}</h3>
          <p>{{ form.level }} · {{ form.focus }} · {{ form.goal }}</p>
          <div class="profile-mini-stats">
            <span>{{ insights?.questionCount || 0 }} 次提问</span>
            <span>{{ insights?.mistakeCount || 0 }} 条薄弱点</span>
            <span>{{ topTopic }}</span>
          </div>
        </div>
      </article>

      <form class="profile-glass-card profile-preference-card" @submit.prevent="handleSave">
        <div class="section-heading">
          <h3>基础偏好</h3>
          <p class="panel-desc">这些信息会进入答疑提示词，影响回答风格。</p>
        </div>

        <label>
          昵称
          <input v-model="form.nickname" placeholder="学习者" />
        </label>

        <div class="profile-form-grid">
          <label>
            编程水平
            <select v-model="form.level">
              <option v-for="item in levelOptions" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
          <label>
            学习方向
            <select v-model="form.focus">
              <option v-for="item in focusOptions" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
          <label>
            学习目标
            <select v-model="form.goal">
              <option v-for="item in goalOptions" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
          <label>
            回答偏好
            <select v-model="form.answerStyle">
              <option v-for="item in styleOptions" :key="item" :value="item">{{ item }}</option>
            </select>
          </label>
        </div>

        <label>
          薄弱点记录偏好
          <select v-model="form.weakPreference">
            <option v-for="item in weakOptions" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>

        <div class="profile-actions">
          <button class="ghost-btn" type="button" :disabled="saving" @click="handleReset">重置</button>
          <button class="primary-btn" type="submit" :disabled="saving">{{ saving ? '保存中...' : '保存档案' }}</button>
        </div>
      </form>
    </section>

    <section class="profile-visual-grid">
      <article class="profile-glass-card">
        <div class="section-heading">
          <h3>能力能量环</h3>
          <p class="panel-desc">根据提问模式和薄弱点粗略估计。</p>
        </div>
        <div class="energy-ring-grid" v-if="abilityScores.length">
          <div v-for="item in abilityScores" :key="item.name" class="energy-ring-card">
            <div class="energy-ring" :style="ringStyle(item.value)">
              <div>
                <strong>{{ item.value }}</strong>
              </div>
            </div>
            <span>{{ item.name }}</span>
          </div>
        </div>
        <p v-else class="history-empty">{{ loading ? '正在生成能力概览。' : '暂无足够数据。' }}</p>
      </article>

      <article class="profile-glass-card">
        <div class="section-heading">
          <h3>方向气泡图</h3>
          <p class="panel-desc">气泡越大，代表近期关注越多。</p>
        </div>
        <div class="topic-bubble-field" v-if="topicDistribution.length">
          <span
            v-for="(item, index) in topicDistribution"
            :key="item.name"
            class="topic-bubble"
            :style="bubbleStyle(item, index)"
          >
            <strong>{{ item.name }}</strong>
            <small>{{ item.value }}%</small>
          </span>
        </div>
        <p v-else class="history-empty">继续提问后会形成方向分布。</p>
      </article>
    </section>

    <section class="profile-lower-grid">
      <article class="profile-glass-card">
        <div class="section-heading">
          <h3>薄弱点标签云</h3>
          <p class="panel-desc">系统最近捕捉到的知识断点。</p>
        </div>
        <div class="weak-cloud" v-if="recentWeakPoints.length">
          <RouterLink
            v-for="(item, index) in recentWeakPoints"
            :key="item.id"
            to="/mistakes"
            class="weak-cloud-chip"
            :class="`chip-level-${(index % 3) + 1}`"
          >
            #{{ item.topic }} · {{ item.title }}
          </RouterLink>
        </div>
        <p v-else class="history-empty">暂无薄弱点记录。</p>
      </article>

      <article class="profile-glass-card strategy-board">
        <div class="section-heading">
          <h3>个性化策略</h3>
          <p class="panel-desc">系统当前会怎样调整回答。</p>
        </div>
        <div class="strategy-note-list" v-if="strategyTips.length">
          <p v-for="(tip, index) in strategyTips" :key="tip" class="strategy-note">
            <span>{{ String(index + 1).padStart(2, '0') }}</span>
            {{ tip }}
          </p>
        </div>
        <p v-else class="history-empty">暂无策略。</p>
      </article>
    </section>
  </section>
</template>
