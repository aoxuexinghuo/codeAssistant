<script setup>
import { onMounted, ref } from 'vue'
import {
  deleteStudyPlan,
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
const summarizingPlanId = ref(null)
const pointsToast = ref('')

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
})
</script>

<template>
  <section class="page-stack home-page">
    <header class="page-hero compact-hero home-hero">
      <div>
        <div class="badge">Home</div>
        <h2>编程学习助手</h2>
        <p class="panel-desc">用答疑、薄弱点记录和资料入口组织你的学习过程。</p>
      </div>
      <RouterLink to="/assistant" class="primary-link">开始答疑</RouterLink>
    </header>

    <section id="home-study-plans" class="home-study-panel">
      <div class="section-heading">
        <div>
          <span class="badge">Plan</span>
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
