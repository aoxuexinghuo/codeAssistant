<script setup>
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

marked.setOptions({
  gfm: true,
  breaks: true,
})

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
  fallback: {
    type: String,
    default: '',
  },
})

const renderedHtml = computed(() => {
  const source = props.content || props.fallback
  return DOMPurify.sanitize(marked.parse(source || ''))
})
</script>

<template>
  <div class="markdown-body" v-html="renderedHtml"></div>
</template>
