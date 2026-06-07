<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Mi Posición</h2>

    <!-- Loading -->
    <div v-if="scoresStore.isLoading" class="space-y-3">
      <div v-for="i in 2" :key="i" class="h-14 bg-surface-container animate-pulse rounded-lg"></div>
    </div>

    <!-- Error -->
    <div v-else-if="scoresStore.error" class="text-error font-body-md">
      Error al cargar posición
    </div>

    <!-- Empty -->
    <div v-else-if="scoresStore.myStanding.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No perteneces a ningún grupo aún
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="item in scoresStore.myStanding"
        :key="item.group_id"
        class="flex items-center justify-between p-3 bg-surface-container-low rounded-lg"
      >
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold"
               :class="rankColor(item.rank)">
            {{ item.rank }}
          </div>
          <div>
            <p class="font-body-md text-on-surface font-medium">{{ item.group_name }}</p>
            <p class="font-label-sm text-on-surface-variant">{{ item.member_count }} miembros</p>
          </div>
        </div>
        <div class="text-right">
          <p class="font-headline-sm text-primary font-bold">{{ item.total_points }} pts</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useScoresStore } from '@/stores/scores'

const scoresStore = useScoresStore()

onMounted(() => {
  scoresStore.fetchMyStanding()
})

function rankColor(rank: number): string {
  if (rank === 1) return 'bg-tertiary text-on-tertiary'
  if (rank === 2) return 'bg-secondary text-on-secondary'
  if (rank === 3) return 'bg-primary text-on-primary'
  return 'bg-surface-container text-on-surface'
}
</script>
