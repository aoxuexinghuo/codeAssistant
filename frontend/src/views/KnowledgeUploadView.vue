<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  router.replace({ name: 'learning', query: { upload: '1' } })
})
</script>

<template>
  <section class="page-stack">
    <div class="history-empty">
      <p>正在打开上传窗口...</p>
    </div>
  </section>
</template>
