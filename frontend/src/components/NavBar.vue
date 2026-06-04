<template>
  <nav class="bg-indigo-600 text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo/Title -->
        <router-link to="/dashboard" class="flex items-center gap-2">
          <span class="text-2xl font-bold">⚽ Prode</span>
        </router-link>

        <!-- Navigation Links -->
        <div class="hidden md:flex items-center gap-6">
          <router-link
            to="/dashboard"
            class="hover:text-indigo-200 transition-colors"
          >
            Dashboard
          </router-link>
          <router-link
            to="/matches"
            class="hover:text-indigo-200 transition-colors"
          >
            Matches
          </router-link>
          <router-link
            to="/history"
            class="hover:text-indigo-200 transition-colors"
          >
            History
          </router-link>
        </div>

        <!-- User Menu -->
        <div v-if="authStore.user" class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <img
              v-if="authStore.user.picture"
              :src="authStore.user.picture"
              :alt="authStore.user.name"
              class="w-8 h-8 rounded-full"
            />
            <span class="font-semibold">{{ authStore.user.name }}</span>
          </div>
          <button
            @click="handleLogout"
            class="
              px-4 py-2 bg-indigo-700 rounded-lg
              hover:bg-indigo-800 transition-colors
            "
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push({ name: 'Login' })
}
</script>
