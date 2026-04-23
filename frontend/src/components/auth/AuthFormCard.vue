<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  isLogin: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['submit', 'switch-mode'])

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

watch(
  () => props.isLogin,
  (nextValue) => {
    if (nextValue) {
      form.confirmPassword = ''
    }
  }
)

function handleSubmit() {
  emit('submit', {
    username: form.username.trim(),
    password: form.password.trim(),
    confirmPassword: form.confirmPassword.trim(),
  })
}
</script>

<template>
  <section class="auth-card">
    <div class="badge">{{ isLogin ? 'Login' : 'Register' }}</div>
    <h2>{{ title }}</h2>
    <p class="subtitle">{{ subtitle }}</p>

    <form class="auth-form" @submit.prevent="handleSubmit">
      <label>
        用户名
        <input v-model.trim="form.username" type="text" placeholder="请输入用户名" required />
      </label>

      <label>
        密码
        <input v-model.trim="form.password" type="password" placeholder="请输入密码" required />
      </label>

      <label v-if="!isLogin">
        确认密码
        <input
          v-model.trim="form.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          required
        />
      </label>

      <button type="submit">{{ isLogin ? '登录进入工作台' : '注册并进入工作台' }}</button>
    </form>

    <p class="switch-text">
      {{ isLogin ? '还没有账号？' : '已经有账号了？' }}
      <button class="link-btn" type="button" @click="$emit('switch-mode')">
        {{ isLogin ? '去注册' : '去登录' }}
      </button>
    </p>
  </section>
</template>
