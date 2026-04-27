<script setup>
import MarkdownRenderer from '../common/MarkdownRenderer.vue'

const modeShortLabels = {
  debug: '调试',
  learning: '学习',
  interview: '面试',
}

function formatScore(score) {
  return `${Math.round(Number(score || 0) * 100)}%`
}

defineProps({
  modes: {
    type: Array,
    required: true,
  },
  activeMode: {
    type: String,
    required: true,
  },
  currentMode: {
    type: Object,
    required: true,
  },
  question: {
    type: String,
    required: true,
  },
  answer: {
    type: String,
    required: true,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  modeLoading: {
    type: Boolean,
    required: true,
  },
  errorMessage: {
    type: String,
    default: '',
  },
  autoExtractEnabled: {
    type: Boolean,
    default: true,
  },
  ragEnabled: {
    type: Boolean,
    default: false,
  },
  ragSources: {
    type: Array,
    default: () => [],
  },
  ragHits: {
    type: Array,
    default: () => [],
  },
  extractionMessage: {
    type: String,
    default: '',
  },
  extractionState: {
    type: String,
    default: '',
  },
})

defineEmits(['update:question', 'update:autoExtractEnabled', 'update:ragEnabled', 'submit', 'select-mode'])
</script>

<template>
  <section class="qa-panel">
    <div class="qa-topbar">
      <div>
        <h2>{{ currentMode.label }}</h2>
        <p class="tone-text" v-if="currentMode.tone">{{ currentMode.tone }}</p>
      </div>

      <div class="mode-segmented" aria-label="答疑模式">
        <button
          v-for="mode in modes"
          :key="mode.key"
          type="button"
          class="mode-segment-item"
          :class="{ active: activeMode === mode.key }"
          @click="$emit('select-mode', mode.key)"
        >
          {{ modeShortLabels[mode.key] || mode.label.replace('模式', '') }}
        </button>
      </div>
    </div>

    <div class="answer-box">
      <h3>助手输出</h3>
      <MarkdownRenderer :content="answer" fallback="这里会显示回答内容。" />
      <div v-if="ragSources.length" class="rag-source-list">
        <span>参考来源</span>
        <ul>
          <li v-for="source in ragSources" :key="`${source.file}-${source.chunkIndex}`">
            {{ source.title }} / {{ source.file }}
          </li>
        </ul>
      </div>
      <details v-if="ragHits.length" class="rag-hit-details">
        <summary>查看知识库命中 {{ ragHits.length }} 条</summary>
        <div class="rag-hit-list">
          <article v-for="hit in ragHits" :key="`${hit.file}-${hit.chunkIndex}`" class="rag-hit-item">
            <div class="rag-hit-meta">
              <strong>{{ hit.title }}</strong>
              <span>{{ formatScore(hit.score) }}</span>
            </div>
            <p>{{ hit.content }}</p>
            <small>{{ hit.file }} · 片段 {{ hit.chunkIndex }}</small>
          </article>
        </div>
      </details>
    </div>

    <div class="composer">
      <label class="field">
        你的问题
        <textarea
          :value="question"
          rows="4"
          :placeholder="currentMode.placeholder"
          :disabled="modeLoading"
          @input="$emit('update:question', $event.target.value)"
        />
      </label>

      <div class="composer-footer">
        <label class="inline-toggle">
          <input
            type="checkbox"
            :checked="autoExtractEnabled"
            @change="$emit('update:autoExtractEnabled', $event.target.checked)"
          />
          <span>自动沉淀薄弱点</span>
        </label>

        <label class="inline-toggle">
          <input
            type="checkbox"
            :checked="ragEnabled"
            @change="$emit('update:ragEnabled', $event.target.checked)"
          />
          <span>知识库增强</span>
        </label>

        <p
          v-if="extractionMessage"
          class="inline-tip"
          :class="{
            'is-success': extractionState === 'success',
            'is-neutral': extractionState === 'neutral',
            'is-error': extractionState === 'error',
          }"
        >
          {{ extractionMessage }}
        </p>

        <button class="primary-btn" type="button" :disabled="loading || modeLoading" @click="$emit('submit')">
          {{ loading ? '生成中...' : '生成回答' }}
        </button>
      </div>
    </div>

    <p class="error-text" v-if="errorMessage">{{ errorMessage }}</p>
  </section>
</template>
