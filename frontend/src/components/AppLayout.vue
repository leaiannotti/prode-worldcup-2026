<template>
  <div class="min-h-screen bg-background flex flex-col">
    <NavBar />
    <main class="flex-1 pt-16 pb-16 md:pb-0 overflow-y-auto">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import NavBar from './NavBar.vue'
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
