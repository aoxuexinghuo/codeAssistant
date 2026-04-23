<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { getLearningTopic } from '../data/learningResources'

const route = useRoute()

const resource = computed(() => getLearningTopic(route.params.slug))
</script>

<template>
  <section class="page-stack" v-if="resource">
    <header class="page-hero">
      <div>
        <div class="badge">Learning Resource</div>
        <h2>{{ resource.title }}</h2>
        <p class="panel-desc">{{ resource.summary }}</p>
      </div>
      <span class="topic-pill">{{ resource.level }}</span>
    </header>

    <section class="summary-grid">
      <article class="summary-card">
        <span class="summary-label">学习方式</span>
        <strong>从基础到重点逐步学习</strong>
        <p>结合资料、练习和答疑，更容易建立完整理解。</p>
      </article>
      <article class="summary-card">
        <span class="summary-label">适合阶段</span>
        <strong>{{ resource.level }}</strong>
        <p>{{ resource.desc }}</p>
      </article>
    </section>

    <section class="page-grid two-column">
      <article class="panel">
        <div class="section-heading">
          <h3>学习重点</h3>
          <p class="panel-desc">进入这个主题时，建议优先掌握这些内容。</p>
        </div>
        <div class="list-block">
          <article v-for="item in resource.focus" :key="item" class="list-row">
            <span class="row-tag">重点</span>
            <div>
              <strong>{{ item }}</strong>
            </div>
          </article>
        </div>
      </article>

      <article class="panel">
        <div class="section-heading">
          <h3>适合人群</h3>
          <p class="panel-desc">了解这个主题更适合哪些学习目标。</p>
        </div>
        <div class="list-block">
          <article v-for="item in resource.audience" :key="item" class="list-row">
            <span class="row-tag">适合</span>
            <div>
              <strong>{{ item }}</strong>
            </div>
          </article>
        </div>
      </article>
    </section>

    <section class="panel">
      <div class="section-heading">
        <h3>官方资料</h3>
        <p class="panel-desc">可直接打开对应资料页开始学习。</p>
      </div>
      <div class="resource-grid">
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
          <p>点击后将在新标签页打开。</p>
        </a>
      </div>
    </section>
  </section>

  <section class="page-stack" v-else>
    <header class="page-hero">
      <div>
        <div class="badge">Learning Resource</div>
        <h2>资料不存在</h2>
        <p class="panel-desc">未找到对应主题，请返回学习中心重新选择。</p>
      </div>
      <RouterLink to="/learning" class="primary-link">返回学习中心</RouterLink>
    </header>
  </section>
</template>
