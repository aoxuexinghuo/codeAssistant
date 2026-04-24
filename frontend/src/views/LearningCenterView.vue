<script setup>
import { learningTopics } from '../data/learningResources'
</script>

<template>
  <section class="page-stack">
    <header class="page-hero compact-hero">
      <div>
        <div class="badge">Learning</div>
        <h2>学习中心</h2>
        <p class="panel-desc">选择一个方向，进入对应资料页。</p>
      </div>
    </header>

    <section class="topic-grid">
      <RouterLink
        v-for="item in learningTopics"
        :key="item.slug"
        :to="`/learning/${item.slug}`"
        class="topic-card interactive-card"
      >
        <div class="topic-initial">{{ item.initial }}</div>
        <div class="topic-content">
          <div class="topic-card-head">
            <strong>{{ item.title }}</strong>
            <span class="row-tag">{{ item.level }}</span>
          </div>
          <p>{{ item.desc }}</p>
          <span class="topic-action">查看资料 →</span>
        </div>
      </RouterLink>
    </section>
  </section>
</template>
