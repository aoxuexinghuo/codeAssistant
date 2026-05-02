<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  deleteStudyPlan,
  fetchMistakes,
  fetchStudyPlans,
  generateStudyPlanSummary,
  updateStudyPlanStep,
} from '../services/api/assistant'

const entries = [
  {
    step: '01',
    title: '智能答疑',
    text: '在调试、学习、面试三种模式之间切换，获得更贴近场景的回答。',
    to: '/assistant',
    mark: '答',
  },
  {
    step: '02',
    title: '薄弱点记录',
    text: '查看答疑过程中自动沉淀的知识卡片，也可以手动补充。',
    to: '/mistakes',
    mark: '记',
  },
  {
    step: '03',
    title: '知识库',
    text: '按 C、Java、Go、Rust、Vue 3 查看对应资料，并用于知识库增强回答。',
    to: '/learning',
    mark: '库',
  },
]

const studyPlans = ref([])
const loadingPlan = ref(true)
const weakPoints = ref([])
const loadingWeakPoints = ref(true)
const summarizingPlanId = ref(null)
const pointsToast = ref('')

const typeLabels = {
  concept: '概念',
  logic: '逻辑',
  boundary: '边界',
  syntax: '语法',
  expression: '表达',
  debugging: '调试',
}

const todayWeakPoints = computed(() => {
  const today = new Date().toDateString()
  return weakPoints.value.filter((item) => item.createdAt && new Date(item.createdAt).toDateString() === today)
})

const visibleWeakPoints = computed(() => {
  const source = todayWeakPoints.value.length ? todayWeakPoints.value : weakPoints.value
  return source.slice(0, 3)
})

const weakPanelTitle = computed(() => (todayWeakPoints.value.length ? '今日薄弱点' : '最近需要复盘'))

async function loadStudyPlans() {
  loadingPlan.value = true

  try {
    studyPlans.value = await fetchStudyPlans()
  } catch {
    studyPlans.value = []
  } finally {
    loadingPlan.value = false
  }
}

async function loadWeakPoints() {
  loadingWeakPoints.value = true

  try {
    const records = await fetchMistakes()
    weakPoints.value = records.filter((item) => item.reviewStatus !== 'mastered').sort((a, b) => {
      const timeA = new Date(a.createdAt || 0).getTime()
      const timeB = new Date(b.createdAt || 0).getTime()
      return timeB - timeA
    })
  } catch (error) {
    console.error('[home-weak-points] load failed', error)
    weakPoints.value = []
  } finally {
    loadingWeakPoints.value = false
  }
}

function replacePlan(nextPlan) {
  studyPlans.value = studyPlans.value.map((item) => (item.id === nextPlan.id ? nextPlan : item))
}

async function handleTogglePlanStep(planId, stepIndex, completed) {
  pointsToast.value = ''

  try {
    const result = await updateStudyPlanStep(planId, stepIndex, completed)
    const nextPlan = result.plan || result
    replacePlan(nextPlan)

    if (result.awardedPoints) {
      pointsToast.value = `已获得 ${result.awardedPoints} 积分`
    }
  } catch (error) {
    console.error('[study-plan] update step failed', error)
  }
}

async function handleDeletePlan(id) {
  try {
    await deleteStudyPlan(id)
    studyPlans.value = studyPlans.value.filter((item) => item.id !== id)
  } catch (error) {
    console.error('[study-plan] delete failed', error)
  }
}

function planProgress(plan) {
  return plan?.plan?.progress || { total: 0, completed: 0, percent: 0 }
}

function typeLabel(type) {
  return typeLabels[type] || '知识点'
}

function weakSummary(item) {
  return item.referenceAnswer || item.mistakeReason || item.improvementSuggestion || '建议回看本轮问答，补一个最小示例。'
}

async function handleGenerateSummary(id) {
  summarizingPlanId.value = id

  try {
    const nextPlan = await generateStudyPlanSummary(id)
    replacePlan(nextPlan)
  } catch (error) {
    console.error('[study-plan] summary failed', error)
  } finally {
    summarizingPlanId.value = null
  }
}

onMounted(() => {
  loadStudyPlans()
  loadWeakPoints()
})
</script>

<template>
  <section class="page-stack home-page">
    <header class="page-hero compact-hero home-hero">
      <div>
        <h2>编程学习助手</h2>
        <p class="panel-desc">用答疑、薄弱点记录和资料入口组织你的学习过程。</p>
      </div>
      <RouterLink to="/assistant" class="primary-link">开始答疑</RouterLink>
    </header>

    <section class="home-weak-panel">
      <div class="section-heading">
        <div>
          <h3>{{ weakPanelTitle }}</h3>
        </div>
        <RouterLink to="/mistakes" class="primary-link">查看全部</RouterLink>
      </div>

      <div v-if="visibleWeakPoints.length" class="home-weak-grid">
        <RouterLink v-for="item in visibleWeakPoints" :key="item.id" to="/mistakes" class="home-weak-card interactive-card">
          <div class="home-weak-card-head">
            <span class="row-tag">{{ item.topic }}</span>
            <span class="topic-pill">{{ typeLabel(item.mistakeType) }}</span>
          </div>
          <strong>{{ item.question }}</strong>
          <p>{{ weakSummary(item) }}</p>
          <span class="topic-action">去复盘 →</span>
        </RouterLink>
      </div>

      <div v-else class="home-weak-empty">
        <p>{{ loadingWeakPoints ? '正在读取薄弱点。' : '暂时没有需要复盘的薄弱点。' }}</p>
        <RouterLink to="/assistant" class="text-link">去提一个问题</RouterLink>
      </div>
    </section>

    <section id="home-study-plans" class="home-study-panel">
      <div class="section-heading">
        <div>
          <h3>我的学习计划</h3>
        </div>
        <RouterLink to="/learning" class="primary-link">生成新计划</RouterLink>
      </div>
      <p v-if="pointsToast" class="success-toast compact-toast">{{ pointsToast }}</p>

      <div v-if="studyPlans.length" class="study-plan-grid">
        <article v-for="plan in studyPlans" :key="plan.id" class="study-plan-card">
          <div class="study-plan-head">
            <div>
              <h4>{{ plan.title }}</h4>
            </div>
            <button class="icon-btn danger-icon-btn" type="button" title="删除计划" @click="handleDeletePlan(plan.id)">
              ×
            </button>
          </div>
          <p>{{ plan.goal }}</p>
          <div class="study-plan-progress">
            <span>{{ planProgress(plan).completed }}/{{ planProgress(plan).total }} 已完成</span>
            <div class="plan-progress-line">
              <span :style="{ width: `${planProgress(plan).percent}%` }"></span>
            </div>
          </div>
          <ol class="study-step-list">
            <li
              v-for="(step, index) in plan.plan.steps"
              :key="`${plan.id}-${step.resource}-${step.title}`"
              :class="{ 'is-completed': step.completed }"
            >
              <label class="study-step-check">
                <input
                  type="checkbox"
                  :checked="step.completed"
                  @change="handleTogglePlanStep(plan.id, index, $event.target.checked)"
                />
                <span></span>
              </label>
              <div>
                <strong>{{ step.title }}</strong>
                <span>{{ step.task }}</span>
              </div>
              <div class="task-points">
                <span v-if="!step.accepted">+{{ step.points || 1 }}</span>
                <em v-else>已获得 {{ step.points || 1 }}</em>
              </div>
            </li>
          </ol>
          <div v-if="planProgress(plan).percent === 100" class="study-summary-area">
            <div v-if="!plan.plan.stageSummary" class="study-complete-banner">
              <span>✓</span>
              <div>
                <strong>计划已完成</strong>
                <p>可以整理一次阶段收获，为下一轮学习做准备。</p>
              </div>
              <button
                class="summary-action-btn"
                type="button"
                :disabled="summarizingPlanId === plan.id"
                @click="handleGenerateSummary(plan.id)"
              >
                {{ summarizingPlanId === plan.id ? '生成中' : '生成总结' }}
              </button>
            </div>
            <div v-else class="study-summary-card">
              <div class="study-summary-title">
                <span>✓</span>
                <strong>阶段总结</strong>
              </div>
              <p>{{ plan.plan.stageSummary.achievement }}</p>
              <ul v-if="plan.plan.stageSummary.keyPoints?.length">
                <li v-for="point in plan.plan.stageSummary.keyPoints" :key="point">{{ point }}</li>
              </ul>
              <span>{{ plan.plan.stageSummary.nextStep }}</span>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="history-empty">
        <p>{{ loadingPlan ? '正在读取学习计划。' : '暂无学习计划。' }}</p>
        <RouterLink to="/learning" class="primary-link">去选择资料</RouterLink>
      </div>
    </section>

    <section class="home-entry-grid">
      <RouterLink v-for="item in entries" :key="item.to" :to="item.to" class="home-entry-card interactive-card">
        <div class="home-entry-top">
          <span class="home-entry-mark">{{ item.mark }}</span>
          <span class="home-entry-step">{{ item.step }}</span>
        </div>
        <div class="home-entry-copy">
          <strong>{{ item.title }}</strong>
          <p>{{ item.text }}</p>
        </div>
        <span class="topic-action">进入 →</span>
      </RouterLink>
    </section>
  </section>
</template>
