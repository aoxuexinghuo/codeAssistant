<script setup>
defineProps({
  historyCount: {
    type: Number,
    required: true,
  },
})

defineEmits(['logout', 'toggle-history'])
</script>

<template>
  <header class="assistant-header">
    <div class="header-copy">
      <p class="badge">Programming Assistant Workspace</p>
      <h1>基于大模型的编程答疑助手</h1>
    </div>
    <div class="assistant-actions">
      <button class="ghost-btn" type="button" @click="$emit('toggle-history')">
        会话历史
        <span class="header-count" v-if="historyCount">{{ historyCount }}</span>
      </button>
      <button class="ghost-btn" type="button" @click="$emit('logout')">退出登录</button>
    </div>
  </header>
</template>
