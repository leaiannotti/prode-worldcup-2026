<template>
  <div id="app" class="min-h-screen bg-background">
    <PageLoader :show="isNavigating" />
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterView, useRouter } from 'vue-router'
import PageLoader from '@/components/PageLoader.vue'

const router = useRouter()
const isNavigating = ref(false)

router.beforeEach(() => {
  isNavigating.value = true
})

router.afterEach(() => {
  setTimeout(() => {
    isNavigating.value = false
  }, 1500)
})
</script>
