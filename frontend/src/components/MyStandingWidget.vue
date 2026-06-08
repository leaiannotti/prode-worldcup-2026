<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Mis Posiciones</h2>

    <!-- Loading -->
    <div v-if="scoresStore.isLoading" class="space-y-3">
      <div v-for="i in 2" :key="i" class="h-20 bg-surface-container animate-pulse rounded-xl"></div>
    </div>

    <!-- Error -->
    <div v-else-if="scoresStore.error" class="text-error font-body-md">
      Error al cargar posición
    </div>

    <!-- Empty -->
    <div v-else-if="scoresStore.myStanding.length === 0" class="text-on-surface-variant font-body-md text-center py-6">
      No perteneces a ninguna liga aún
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
          <p class="text-[11px] text-on-surface-variant mt-0.5">{{ item.member_count }} miembros</p>
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
import { useScoresStore } from '@/stores/scores'

const scoresStore = useScoresStore()

onMounted(() => {
  scoresStore.fetchMyStanding()
})

function rankStyle(rank: number): string {
  if (rank === 1) return 'bg-amber-400 text-amber-950'
  if (rank === 2) return 'bg-slate-300 text-slate-800'
  if (rank === 3) return 'bg-orange-300 text-orange-900'
  return 'bg-surface-container text-on-surface-variant'
}
</script>
