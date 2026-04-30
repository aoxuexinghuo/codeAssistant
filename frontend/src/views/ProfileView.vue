<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  fetchProfile,
  fetchProfileInsights,
  fetchStudyPlans,
  resetProfile,
  updateProfile,
} from '../services/api/assistant'

const profile = ref(null)
const insights = ref(null)
const loading = ref(true)
const saving = ref(false)
const message = ref('')
const errorMessage = ref('')
const studyPlans = ref([])

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
const recentWeakPoints = computed(() => insights.value?.recentWeakPoints || [])
const strategyTips = computed(() => insights.value?.strategyTips || [])

const topTopic = computed(() => topicDistribution.value[0]?.name || form.focus)
const currentPlan = computed(() => studyPlans.value[0] || null)
const currentProgress = computed(() => currentPlan.value?.plan?.progress || { total: 0, completed: 0, percent: 0 })
const pendingTaskCount = computed(() => Math.max(0, currentProgress.value.total - currentProgress.value.completed))
const totalPoints = computed(() => profile.value?.totalPoints || 0)
const pointLevel = computed(() => Math.floor(totalPoints.value / 50) + 1)
const currentLevelStart = computed(() => (pointLevel.value - 1) * 50)
const nextLevelPoint = computed(() => pointLevel.value * 50)
const levelProgress = computed(() => Math.min(100, ((totalPoints.value - currentLevelStart.value) / 50) * 100))
const pointsToNextLevel = computed(() => nextLevelPoint.value - totalPoints.value)
const statusCards = computed(() => [
  {
    label: '累计提问',
    value: insights.value?.questionCount || 0,
    unit: '次',
    text: '来自会话历史',
  },
  {
    label: '薄弱点',
    value: insights.value?.mistakeCount || 0,
    unit: '条',
    text: '来自知识点卡片',
  },
  {
    label: '进行中任务',
    value: pendingTaskCount.value,
    unit: '项',
    text: currentPlan.value ? currentPlan.value.title : '暂无计划',
  },
  {
    label: '当前方向',
    value: topTopic.value,
    unit: '',
    text: `${form.level} · ${form.goal}`,
  },
])
const weakTopicGroups = computed(() => {
  const groups = recentWeakPoints.value.reduce((result, item) => {
    const topic = item.topic || '编程基础'
    if (!result[topic]) {
      result[topic] = []
    }
    result[topic].push(item)
    return result
  }, {})

  return Object.entries(groups).map(([topic, items]) => ({
    topic,
    count: items.length,
    items: items.slice(0, 3),
  }))
})
const nextActions = computed(() => {
  const actions = []

  if (currentPlan.value && currentProgress.value.percent < 100) {
    const nextStep = currentPlan.value.plan?.steps?.find((step) => !step.completed)
    if (nextStep) {
      actions.push({
        title: `继续完成：${nextStep.title}`,
        text: nextStep.task,
        to: '/home',
        action: '去首页',
      })
    }
  }

  if (recentWeakPoints.value.length) {
    const weakPoint = recentWeakPoints.value[0]
    actions.push({
      title: `复盘：${weakPoint.title}`,
      text: `最近薄弱点集中在 ${weakPoint.topic || '编程基础'}，建议先补一个最小示例。`,
      to: '/mistakes',
      action: '看薄弱点',
    })
  }

  actions.push({
    title: `围绕 ${topTopic.value} 提一个追问`,
    text: '用一个具体代码片段或报错来提问，系统更容易给出可执行建议。',
    to: '/assistant',
    action: '去提问',
  })

  return actions.slice(0, 3)
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
    const [profileData, insightsData, planData] = await Promise.all([
      fetchProfile(),
      fetchProfileInsights(),
      fetchStudyPlans(),
    ])
    profile.value = profileData
    insights.value = insightsData
    studyPlans.value = planData
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

    <section class="level-progress-card">
      <div>
        <h3>Lv.{{ pointLevel }} 学习等级</h3>
        <p>累计 {{ totalPoints }} 积分，距离 Lv.{{ pointLevel + 1 }} 还差 {{ pointsToNextLevel }} 分。</p>
      </div>
      <div class="level-progress-track">
        <span :style="{ width: `${levelProgress}%` }"></span>
      </div>
    </section>

    <section class="diagnosis-status-grid">
      <article v-for="card in statusCards" :key="card.label" class="diagnosis-stat-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}<small>{{ card.unit }}</small></strong>
        <p>{{ card.text }}</p>
      </article>
    </section>

    <section class="diagnosis-layout">
      <article class="profile-glass-card diagnosis-action-card">
        <div class="section-heading">
          <h3>下一步建议</h3>
          <p class="panel-desc">根据当前计划和近期薄弱点生成。</p>
        </div>
        <div class="diagnosis-action-list">
          <RouterLink v-for="(item, index) in nextActions" :key="item.title" :to="item.to" class="diagnosis-action">
            <span>{{ String(index + 1).padStart(2, '0') }}</span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.text }}</p>
            </div>
            <em>{{ item.action }}</em>
          </RouterLink>
        </div>
      </article>

      <article class="profile-glass-card diagnosis-focus-card">
        <div class="section-heading">
          <h3>薄弱点诊断</h3>
          <p class="panel-desc">按主题聚合最近暴露出的知识断点。</p>
        </div>
        <div v-if="weakTopicGroups.length" class="weak-diagnosis-list">
          <div v-for="group in weakTopicGroups" :key="group.topic" class="weak-diagnosis-item">
            <div>
              <strong>{{ group.topic }}</strong>
              <span>{{ group.count }} 条近期记录</span>
            </div>
            <p v-for="item in group.items" :key="item.id">{{ item.title }}</p>
            <RouterLink to="/mistakes" class="text-link">查看记录</RouterLink>
          </div>
        </div>
        <p v-else class="history-empty">暂无薄弱点记录。完成几次答疑后，这里会形成诊断。</p>
      </article>
    </section>

    <section class="profile-dashboard">
      <form class="profile-glass-card profile-preference-card" @submit.prevent="handleSave">
        <div class="section-heading">
          <h3>个人偏好</h3>
          <p class="panel-desc">这些设置会影响答疑时的解释方式。</p>
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

      <article class="profile-glass-card diagnosis-context-card">
        <div class="section-heading">
          <h3>画像依据</h3>
          <p class="panel-desc">根据历史提问和薄弱点记录形成。</p>
        </div>
        <div class="topic-rank-list" v-if="topicDistribution.length">
          <div v-for="item in topicDistribution" :key="item.name" class="topic-rank-item">
            <span>{{ item.name }}</span>
            <div>
              <i :style="{ width: `${item.value}%` }"></i>
            </div>
            <strong>{{ item.value }}%</strong>
          </div>
        </div>
        <p v-else class="history-empty">继续提问后会形成方向分布。</p>
        <div class="strategy-note-list compact-strategy" v-if="strategyTips.length">
          <p v-for="tip in strategyTips" :key="tip">{{ tip }}</p>
        </div>
      </article>
    </section>
  </section>
</template>
