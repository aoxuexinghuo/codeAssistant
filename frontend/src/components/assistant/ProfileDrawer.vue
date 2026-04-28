<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  profile: {
    type: Object,
    default: null,
  },
  insights: {
    type: Object,
    default: null,
  },
  saving: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'save', 'reset'])

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

const hasInsights = computed(() => Boolean(props.insights))
const topTopics = computed(() => props.insights?.topicDistribution || [])
const abilityScores = computed(() => props.insights?.abilityScores || [])
const recentWeakPoints = computed(() => props.insights?.recentWeakPoints || [])
const strategyTips = computed(() => props.insights?.strategyTips || [])

watch(
  () => props.profile,
  (profile) => {
    if (!profile) {
      return
    }

    form.nickname = profile.nickname || ''
    form.level = profile.level || '初级'
    form.focus = profile.focus || 'C语言'
    form.goal = profile.goal || '课程学习'
    form.answerStyle = profile.answerStyle || '简洁直接'
    form.weakPreference = profile.weakPreference || '自动记录'
  },
  { immediate: true }
)

function submit() {
  emit('save', { ...form })
}
</script>

<template>
  <transition name="history-fade">
    <div v-if="visible" class="history-overlay" @click.self="$emit('close')">
      <aside class="history-drawer profile-drawer">
        <header class="history-head">
          <div>
            <p class="badge">Profile</p>
            <h2>学习画像</h2>
            <p class="panel-desc">基础偏好由你设置，学习状态由系统根据历史和薄弱点统计。</p>
          </div>
          <button class="ghost-btn" type="button" @click="$emit('close')">关闭</button>
        </header>

        <section class="profile-card profile-summary-card">
          <div>
            <strong>{{ form.nickname || '学习者' }}</strong>
            <p>{{ form.level }} · {{ form.focus }} · {{ form.goal }}</p>
          </div>
          <div class="profile-stat-grid" v-if="hasInsights">
            <span>{{ insights.questionCount || 0 }} 次提问</span>
            <span>{{ insights.mistakeCount || 0 }} 条薄弱点</span>
          </div>
        </section>

        <form class="profile-card profile-form" @submit.prevent="submit">
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
            <button class="ghost-btn" type="button" :disabled="saving" @click="$emit('reset')">重置</button>
            <button class="primary-btn" type="submit" :disabled="saving">{{ saving ? '保存中...' : '保存画像' }}</button>
          </div>
        </form>

        <section class="profile-card">
          <div class="section-heading">
            <h3>能力概览</h3>
            <p class="panel-desc">由历史提问和薄弱点粗略估计，先用于展示和个性化策略。</p>
          </div>
          <div class="ability-list" v-if="abilityScores.length">
            <div v-for="item in abilityScores" :key="item.name" class="ability-row">
              <span>{{ item.name }}</span>
              <div class="ability-track"><i :style="{ width: `${item.value}%` }"></i></div>
              <strong>{{ item.value }}</strong>
            </div>
          </div>
          <p v-else class="history-empty">暂无足够数据。</p>
        </section>

        <section class="profile-card">
          <div class="section-heading">
            <h3>学习方向分布</h3>
          </div>
          <div class="topic-progress-list" v-if="topTopics.length">
            <div v-for="item in topTopics" :key="item.name" class="topic-progress-row">
              <span>{{ item.name }}</span>
              <div class="ability-track"><i :style="{ width: `${item.value}%` }"></i></div>
              <strong>{{ item.value }}%</strong>
            </div>
          </div>
          <p v-else class="history-empty">继续提问后会自动统计方向。</p>
        </section>

        <section class="profile-card">
          <div class="section-heading">
            <h3>最近薄弱点</h3>
          </div>
          <div class="profile-chip-list" v-if="recentWeakPoints.length">
            <span v-for="item in recentWeakPoints" :key="item.id" class="profile-chip">
              {{ item.topic }} · {{ item.title }}
            </span>
          </div>
          <p v-else class="history-empty">暂无薄弱点记录。</p>
        </section>

        <section class="profile-card">
          <div class="section-heading">
            <h3>个性化策略</h3>
          </div>
          <ul class="profile-strategy-list" v-if="strategyTips.length">
            <li v-for="tip in strategyTips" :key="tip">{{ tip }}</li>
          </ul>
          <p v-else class="history-empty">{{ loading ? '正在分析画像。' : '暂无策略。' }}</p>
        </section>
      </aside>
    </div>
  </transition>
</template>
