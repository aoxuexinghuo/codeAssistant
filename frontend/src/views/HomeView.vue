<script setup>
const quickActions = [
  { title: '继续学习 Vue 3', text: '从响应式与组件通信继续推进。', to: '/learning' },
  { title: '查看最近错题', text: '优先复习最近反复出现的问题。', to: '/mistakes' },
  { title: '进入智能答疑', text: '针对具体问题即时提问。', to: '/assistant' },
]

const taskCards = [
  { label: '今日任务', value: '3 项', text: '1 个知识点 + 1 次练习 + 1 次错题复习' },
  { label: '连续学习', value: '5 天', text: '保持节奏比单次高强度更重要' },
  { label: '重点主题', value: 'Vue 3', text: '响应式与组件通信' },
]

const records = [
  { type: '最近学习', title: 'Vue 3 响应式基础', meta: '完成度 60%' },
  { type: '最近提问', title: 'ref 和 reactive 的区别', meta: '学习模式' },
  { type: '最近复习', title: '闭包与作用域链错题', meta: '待再次练习' },
]
</script>

<template>
  <section class="page-stack">
    <header class="page-hero">
      <div>
        <div class="badge">Home</div>
        <h2>学习首页</h2>
        <p class="panel-desc">在这里查看今日任务、最近学习记录和常用入口。</p>
      </div>
      <RouterLink to="/assistant" class="primary-link">立即提问</RouterLink>
    </header>

    <section class="summary-grid">
      <article v-for="card in taskCards" :key="card.label" class="summary-card">
        <span class="summary-label">{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <p>{{ card.text }}</p>
      </article>
    </section>

    <section class="page-grid two-column">
      <article class="panel">
        <div class="section-heading">
          <h3>快速入口</h3>
          <p class="panel-desc">常用功能入口。</p>
        </div>
        <div class="card-list">
          <RouterLink v-for="item in quickActions" :key="item.to" :to="item.to" class="info-card link-card">
            <strong>{{ item.title }}</strong>
            <p>{{ item.text }}</p>
          </RouterLink>
        </div>
      </article>

      <article class="panel">
        <div class="section-heading">
          <h3>最近记录</h3>
          <p class="panel-desc">最近的学习、提问与复习记录。</p>
        </div>
        <div class="list-block">
          <article v-for="item in records" :key="item.title" class="list-row">
            <span class="row-tag">{{ item.type }}</span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.meta }}</p>
            </div>
          </article>
        </div>
      </article>
    </section>
  </section>
</template>
