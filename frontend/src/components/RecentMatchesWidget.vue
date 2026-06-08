<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Partidos Finalizados</h2>

    <div v-if="isLoading" class="space-y-2">
      <div v-for="i in 3" :key="i" class="h-14 bg-surface-container animate-pulse rounded-lg"></div>
    </div>

    <div v-else-if="matches.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No hay partidos finalizados aún
    </div>

    <div v-else class="divide-y divide-outline-variant">
      <MatchRow
        v-for="match in matches"
        :key="match.id"
        :match="match"
        :prediction="getPrediction(match.id)"
        :clickable="false"
        :show-countdown="false"
        :show-add-icon="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/lib/api'
import { usePredictionsStore } from '@/stores/predictions'
import type { Match } from '@/stores/matches'
import MatchRow from './MatchRow.vue'

const predictionsStore = usePredictionsStore()
const matches = ref<Match[]>([])
const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const res = await apiClient.get('/api/matches?status=closed&limit=4')
    matches.value = res.data
  } catch (e) {
    console.error('Error loading recent matches', e)
  } finally {
    isLoading.value = false
  }
})

function getPrediction(matchId: number) {
  return predictionsStore.predictions.find(p => p.match_id === matchId) ?? null
}
</script>
