<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getLearningTopic } from '../data/learningResources'

const route = useRoute()
const resource = computed(() => getLearningTopic(route.params.slug))
</script>

<template>
  <section class="page-stack" v-if="resource">
    <header class="page-hero compact-hero">
      <div>
        <div class="badge">Learning</div>
        <h2>{{ resource.title }}</h2>
        <p class="panel-desc">{{ resource.summary }}</p>
      </div>
      <span class="topic-pill">{{ resource.level }}</span>
    </header>

    <section class="page-grid two-column">
      <article class="panel">
        <div class="section-heading">
          <h3>学习重点</h3>
        </div>
        <div class="list-block">
          <article v-for="item in resource.focus" :key="item" class="list-row">
            <span class="row-tag">重点</span>
            <strong>{{ item }}</strong>
          </article>
        </div>
      </article>

      <article class="panel">
        <div class="section-heading">
          <h3>适合人群</h3>
        </div>
        <div class="list-block">
          <article v-for="item in resource.audience" :key="item" class="list-row">
            <span class="row-tag">适合</span>
            <strong>{{ item }}</strong>
          </article>
        </div>
      </article>
    </section>

    <section class="resource-grid">
      <a
        v-for="link in resource.links"
        :key="link.url"
        :href="link.url"
        target="_blank"
        rel="noreferrer"
        class="resource-card interactive-card"
      >
        <span class="row-tag">{{ link.source }}</span>
        <strong>{{ link.label }}</strong>
        <p>打开官方资料</p>
      </a>
    </section>
  </section>

  <section class="page-stack" v-else>
    <header class="page-hero compact-hero">
      <div>
        <div class="badge">Learning</div>
        <h2>资料不存在</h2>
        <p class="panel-desc">未找到对应主题。</p>
      </div>
      <RouterLink to="/learning" class="primary-link">返回学习中心</RouterLink>
    </header>
  </section>
</template>
