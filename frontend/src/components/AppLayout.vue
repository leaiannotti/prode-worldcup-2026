<template>
  <div class="min-h-screen bg-background flex flex-col">
    <NavBar />
    <main class="flex-1 pt-16 pb-16 md:pb-0 overflow-y-auto">
      <slot />
    </main>
    <!-- "What's New" modal — only opens when the backend returns changelog
         entries newer than what the user has acknowledged. First-time users
         see nothing; storage is seeded so future releases pop. -->
    <WhatsNewModal />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import NavBar from './NavBar.vue'
import WhatsNewModal from './WhatsNewModal.vue'
import { useChangelog } from '@/composables/useChangelog'

// AppLayout only mounts on authenticated routes, so triggering the changelog
// check here guarantees we never pop the modal over the login screen.
const { checkForUpdates } = useChangelog()

onMounted(() => {
  checkForUpdates()
})
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
