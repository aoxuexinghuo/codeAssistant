<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AuthFormCard from '../components/auth/AuthFormCard.vue'
import AuthHero from '../components/auth/AuthHero.vue'

const route = useRoute()
const router = useRouter()

const isLogin = computed(() => route.params.mode === 'login')
const title = computed(() => (isLogin.value ? '欢迎回来' : '创建账号'))
const subtitle = computed(() =>
  isLogin.value ? '登录后继续使用编程答疑助手' : '注册后可体验多种答疑模式'
)

function handleSubmit(form) {
  if (!isLogin.value && form.password !== form.confirmPassword) {
    window.alert('两次密码不一致，请检查后重试。')
    return
  }

  router.push('/home')
}

function switchMode() {
  router.push(isLogin.value ? '/auth/register' : '/auth/login')
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-layout">
      <AuthHero />
      <AuthFormCard
        :is-login="isLogin"
        :title="title"
        :subtitle="subtitle"
        @submit="handleSubmit"
        @switch-mode="switchMode"
      />
    </section>
  </main>
</template>
