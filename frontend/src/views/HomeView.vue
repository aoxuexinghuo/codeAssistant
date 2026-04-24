<script setup>
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
    title: '学习中心',
    text: '按 C、Java、Go、Rust、Vue 3 查看对应的学习资料入口。',
    to: '/learning',
    mark: '学',
  },
]
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
