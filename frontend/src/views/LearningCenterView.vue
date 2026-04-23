<script setup>
import { learningTopics } from '../data/learningResources'
</script>

<template>
  <section class="page-stack">
    <header class="page-hero">
      <div>
        <div class="badge">Learning Center</div>
        <h2>学习中心</h2>
        <p class="panel-desc">按语言和框架查看学习主题，进入后可直接访问对应资料。</p>
      </div>
    </header>

    <section class="panel">
      <div class="section-heading">
        <h3>学习主题</h3>
        <p class="panel-desc">选择一个主题开始学习。</p>
      </div>
      <div class="resource-grid topic-grid">
        <RouterLink
          v-for="item in learningTopics"
          :key="item.slug"
          :to="`/learning/${item.slug}`"
          class="resource-card topic-card interactive-card"
        >
          <span class="row-tag">{{ item.level }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.desc }}</p>
        </RouterLink>
      </div>
    </section>
  </section>
</template>
