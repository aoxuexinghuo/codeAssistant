<script setup>
const highlights = [
  {
    title: '模式化输出',
    text: '同一个问题可以切换不同回答策略',
  },
  {
    title: '接口边界清晰',
    text: '前端专注展示，后端专注模式和回复',
  },
  {
    title: '扩展成本低',
    text: '新增功能时只需要补路由、控制器和视图',
  },
]
</script>

<template>
  <article class="hero-card">
    <div class="badge">Frontend + Backend Separation</div>
    <h1>基于大模型的编程答疑助手</h1>
    <p class="subtitle">
      面向调试、学习、面试三类场景的编程学习助手，帮助你更系统地理解知识、解决问题并积累经验。
    </p>

    <div class="hero-grid">
      <div v-for="item in highlights" :key="item.title" class="mini-card">
        <strong>{{ item.title }}</strong>
        <span>{{ item.text }}</span>
      </div>
    </div>
  </article>
</template>
