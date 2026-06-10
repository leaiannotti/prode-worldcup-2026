<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <RouterLink
      to="/grupos"
      class="group flex items-center justify-between mb-4"
    >
      <h2 class="font-headline-md text-headline-md text-primary">{{ t('standing.myLeagues') }}</h2>
      <span class="flex items-center gap-1 text-xs font-medium text-on-surface-variant group-hover:text-primary transition-colors">
        {{ t('standing.viewLeagues') }}
        <svg class="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </span>
    </RouterLink>

    <!-- Loading -->
    <div v-if="scoresStore.isLoading" class="space-y-3">
      <div v-for="i in 2" :key="i" class="h-20 bg-surface-container animate-pulse rounded-xl"></div>
    </div>

    <!-- Error -->
    <div v-else-if="scoresStore.error" class="text-error font-body-md">
      {{ t('standing.error') }}
    </div>

    <!-- Empty -->
    <div v-else-if="scoresStore.myStanding.length === 0" class="flex flex-col items-center text-center py-6 gap-4">
      <p class="font-body-md text-on-surface-variant">{{ t('standing.noLeagues') }}</p>
      <div class="flex gap-2">
        <button
          @click="emit('create-league')"
          class="px-5 py-2.5 bg-primary text-on-primary rounded-xl font-semibold text-sm hover:opacity-90 transition-all active:scale-95"
        >
          {{ t('standing.createLeague') }}
        </button>
        <button
          @click="emit('join-league')"
          class="px-5 py-2.5 bg-surface-container text-on-surface rounded-xl font-semibold text-sm hover:bg-surface-container-high transition-all active:scale-95 border border-outline-variant"
        >
          {{ t('standing.joinCode') }}
        </button>
      </div>
    </div>

    <!-- Cards -->
    <div v-else class="space-y-3">
      <RouterLink
        v-for="item in scoresStore.myStanding"
        :key="item.group_id"
        :to="`/grupos?group=${item.group_id}`"
        class="flex items-center gap-4 p-4 bg-surface-container-low rounded-xl border border-transparent hover:border-outline-variant hover:bg-surface-container transition-all active:scale-[0.98] group"
      >
        <!-- Rank badge -->
        <div
          class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm"
          :class="rankStyle(item.rank)"
        >
          {{ item.rank }}
        </div>

        <!-- Group info -->
        <div class="flex-1 min-w-0">
          <p class="font-body-md text-on-surface font-semibold truncate">{{ item.group_name }}</p>
          <p class="text-[11px] text-on-surface-variant mt-0.5">{{ item.member_count }} {{ t('standing.members') }}</p>
        </div>

          <!-- Arrow -->
        <svg
          class="w-4 h-4 text-on-surface-variant/40 flex-shrink-0 group-hover:text-primary transition-colors"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { useScoresStore } from '@/stores/scores'

const { t } = useI18n()
const scoresStore = useScoresStore()

const emit = defineEmits<{
  (e: 'create-league'): void
  (e: 'join-league'): void
}>()

onMounted(() => {
  scoresStore.fetchMyStanding()
})

function rankStyle(rank: number): string {
  if (rank === 1) return 'bg-amber-400 text-amber-950'
  if (rank === 2) return 'bg-slate-400 text-slate-950'
  if (rank === 3) return 'bg-orange-400 text-orange-950'
  return 'bg-primary-container text-on-primary-fixed'
}
</script>
