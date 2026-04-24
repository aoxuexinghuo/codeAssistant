<script setup>
const highlights = [
  {
    title: '三种答疑模式',
    text: '调试、学习、面试，各自使用不同回答策略。',
  },
  {
    title: '薄弱点沉淀',
    text: '答疑后自动整理可能需要复盘的知识点。',
  },
  {
    title: '资料入口',
    text: '按语言和框架进入官方学习资料。',
  },
]
</script>

<template>
  <article class="hero-card auth-hero-panel">
    <div class="brand-lockup">
      <span class="brand-mark">PA</span>
      <div>
        <p class="badge">Programming Assistant</p>
        <h1>编程学习助手</h1>
      </div>
    </div>

    <p class="subtitle">
      面向编程学习、排错和面试准备的答疑工作台。
    </p>

    <div class="hero-grid">
      <div v-for="item in highlights" :key="item.title" class="mini-card">
        <strong>{{ item.title }}</strong>
        <span>{{ item.text }}</span>
      </div>
    </div>
  </article>
</template>
