<script setup>
const navItems = [
  { label: '首页', short: '首', to: '/home' },
  { label: '知识库', short: '库', to: '/learning' },
  { label: '薄弱点', short: '错', to: '/mistakes' },
  { label: '学习档案', short: '档', to: '/profile' },
  { label: '智能答疑', short: '答', to: '/assistant' },
]
</script>

<template>
  <div class="app-shell">
    <aside class="shell-sidebar">
      <RouterLink to="/home" class="shell-brand" title="编程学习助手">
        <span>PA</span>
      </RouterLink>

      <nav class="shell-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="shell-nav-item"
          active-class="active"
          :title="item.label"
        >
          <span class="nav-mark">{{ item.short }}</span>
          <strong>{{ item.label }}</strong>
        </RouterLink>
      </nav>
    </aside>

    <main class="shell-content">
      <RouterView />
    </main>
  </div>
</template>
