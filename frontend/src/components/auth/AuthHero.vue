<script setup>
const highlights = [
  {
    title: '提问',
    text: '按调试、学习、面试场景组织回答。',
  },
  {
    title: '沉淀',
    text: '自动整理需要复盘的知识卡片。',
  },
  {
    title: '补齐',
    text: '结合本地知识库和学习资料继续巩固。',
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
      用答疑、知识库和薄弱点卡片，把一次次提问整理成可复盘的学习过程。
    </p>

    <div class="hero-grid">
      <div v-for="(item, index) in highlights" :key="item.title" class="mini-card auth-step-card">
        <span class="auth-step-index">0{{ index + 1 }}</span>
        <strong>{{ item.title }}</strong>
        <span>{{ item.text }}</span>
      </div>
    </div>
  </article>
</template>
