<script setup>
import MarkdownRenderer from '../common/MarkdownRenderer.vue'

const modeShortLabels = {
  debug: '调试',
  learning: '学习',
  interview: '面试',
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
  extractionMessage: {
    type: String,
    default: '',
  },
  extractionState: {
    type: String,
    default: '',
  },
})

defineEmits(['update:question', 'update:autoExtractEnabled', 'submit', 'select-mode'])
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
