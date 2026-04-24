<script setup>
import MarkdownRenderer from '../common/MarkdownRenderer.vue'

defineProps({
  items: {
    type: Array,
    required: true,
  },
  visible: {
    type: Boolean,
    required: true,
  },
  clearing: {
    type: Boolean,
    required: true,
  },
  deletingId: {
    type: Number,
    default: null,
  },
  loading: {
    type: Boolean,
    required: true,
  },
  searchKeyword: {
    type: String,
    required: true,
  },
  selectedMode: {
    type: String,
    required: true,
  },
  modeOptions: {
    type: Array,
    required: true,
  },
})

defineEmits([
  'close',
  'reuse-question',
  'clear',
  'delete-history',
  'search',
  'update:search-keyword',
  'update:selected-mode',
])
</script>

<template>
  <transition name="history-fade">
    <div v-if="visible" class="history-overlay" @click.self="$emit('close')">
      <section class="history-drawer">
        <div class="section-heading history-head">
          <div>
            <h2>会话历史</h2>
            <p class="panel-desc">支持按关键词和模式筛选，按时间倒序展示。</p>
          </div>
          <div class="history-actions">
            <button
              class="ghost-btn history-clear"
              type="button"
              :disabled="!items.length || clearing"
              @click="$emit('clear')"
            >
              {{ clearing ? '清空中...' : '清空历史' }}
            </button>
            <button class="ghost-btn" type="button" @click="$emit('close')">关闭</button>
          </div>
        </div>

        <div class="history-toolbar">
          <input
            class="history-search-input"
            type="text"
            placeholder="搜索问题或回答"
            :value="searchKeyword"
            @input="$emit('update:search-keyword', $event.target.value)"
            @keyup.enter="$emit('search')"
          />
          <select
            class="history-filter-select"
            :value="selectedMode"
            @change="$emit('update:selected-mode', $event.target.value)"
          >
            <option value="">全部模式</option>
            <option v-for="mode in modeOptions" :key="mode.key" :value="mode.key">
              {{ mode.label }}
            </option>
          </select>
          <button class="ghost-btn" type="button" @click="$emit('search')">查询</button>
        </div>

        <div v-if="loading" class="history-empty">
          <p>正在加载历史记录...</p>
        </div>

        <div v-else-if="items.length" class="history-timeline">
          <article v-for="item in items" :key="item.id" class="history-entry">
            <div class="history-line"></div>
            <div class="history-card">
              <div class="history-meta">
                <span class="history-tag">{{ item.modeLabel }}</span>
                <div class="history-card-actions">
                  <time>{{ new Date(item.createdAt).toLocaleString('zh-CN', { hour12: false }) }}</time>
                  <button
                    class="icon-btn danger-icon-btn history-delete-btn"
                    type="button"
                    title="删除该会话"
                    :disabled="deletingId === item.id"
                    @click="$emit('delete-history', item.id)"
                  >
                    {{ deletingId === item.id ? '…' : '×' }}
                  </button>
                </div>
              </div>
              <h3>{{ item.question }}</h3>
              <MarkdownRenderer :content="item.reply" />
              <button class="link-btn history-reuse" type="button" @click="$emit('reuse-question', item.question)">
                重新提问
              </button>
            </div>
          </article>
        </div>

        <div v-else class="history-empty">
          <p>没有匹配的历史记录，可以调整关键词或模式后重试。</p>
        </div>
      </section>
    </div>
  </transition>
</template>
