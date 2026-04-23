<script setup>
const navItems = [
  { label: '首页', to: '/home' },
  { label: '学习中心', to: '/learning' },
  { label: '错题本', to: '/mistakes' },
  { label: '智能答疑', to: '/assistant' },
]
</script>

<template>
  <div class="app-shell">
    <aside class="shell-sidebar">
      <div class="shell-brand">
        <div class="badge">Assistant</div>
        <h1>编程学习助手</h1>
      </div>

      <nav class="shell-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="shell-nav-item"
          active-class="active"
        >
          <strong>{{ item.label }}</strong>
        </RouterLink>
      </nav>
    </aside>

    <main class="shell-content">
      <RouterView />
    </main>
  </div>
</template>
