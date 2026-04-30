<script setup>
import { onMounted, ref } from 'vue'
import { deleteStudyPlan, fetchStudyPlans, updateStudyPlanStep } from '../services/api/assistant'

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
  try {
    const nextPlan = await updateStudyPlanStep(planId, stepIndex, completed)
    replacePlan(nextPlan)
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
            </li>
          </ol>
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
