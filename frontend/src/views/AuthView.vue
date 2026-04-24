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
  isLogin.value ? '继续你的编程学习和答疑记录。' : '开启学习、答疑和薄弱点沉淀。'
)

function handleSubmit(form) {
  if (!isLogin.value && form.password !== form.confirmPassword) {
    window.alert('两次密码不一致，请重新输入。')
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
