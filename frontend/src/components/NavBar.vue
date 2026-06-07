<template>
  <header class="fixed top-0 z-50 w-full bg-surface shadow-sm h-16 border-b border-outline-variant">
    <div class="flex justify-between items-center w-full px-5 h-full">
      <!-- Logo and Brand Name -->
      <div class="flex items-center gap-4">
        <span class="font-display-lg text-headline-lg font-black text-primary uppercase tracking-tighter">
          PRODE 2026
        </span>
        <!-- Navigation Links (Desktop) -->
        <nav class="hidden md:flex gap-4 ml-6">
          <RouterLink
            to="/dashboard"
            class="text-on-surface-variant hover:text-primary font-label-md text-body-md transition-colors"
            active-class="text-primary border-b-2 border-primary pb-1"
          >
            Dashboard
          </RouterLink>
          <RouterLink
            to="/matches"
            class="text-on-surface-variant hover:text-primary font-label-md text-body-md transition-colors"
            active-class="text-primary border-b-2 border-primary pb-1"
          >
            Matches
          </RouterLink>
          <RouterLink
            to="/predictions"
            class="text-on-surface-variant hover:text-primary font-label-md text-body-md transition-colors"
            active-class="text-primary border-b-2 border-primary pb-1"
          >
            Predictions
          </RouterLink>
        </nav>
      </div>

      <!-- Right Section: Points, Notifications, Avatar, Logout -->
      <div class="flex items-center gap-2">
        <!-- Points Display (Desktop) -->
        <div v-if="authStore.user" class="hidden sm:flex items-center bg-primary-fixed text-on-primary-fixed px-2 py-1 rounded-full">
          <span class="font-bold font-label-md text-label-md">Points: 1,250</span>
        </div>

        <!-- Notifications Button -->
        <button class="p-1 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors duration-200">
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            />
          </svg>
        </button>

        <!-- User Avatar -->
        <div v-if="authStore.user" class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary-fixed">
          <img
            :src="authStore.user.picture || 'https://via.placeholder.com/40'"
            :alt="authStore.user.name"
            class="w-full h-full object-cover"
          />
        </div>

        <!-- Logout Button -->
        <button
          @click="handleLogout"
          class="p-1 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors duration-200"
          title="Logout"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

async function handleLogout() {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
