<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Próximos Partidos</h2>

    <div v-if="matchesStore.isLoading" class="space-y-2">
      <div v-for="i in 3" :key="i" class="h-14 bg-surface-container animate-pulse rounded-lg"></div>
    </div>

    <div v-else-if="matchesStore.error" class="text-error font-body-md">
      Error al cargar partidos
    </div>

    <div v-else-if="upcomingMatches.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No hay partidos próximos
    </div>

    <div v-else class="divide-y divide-outline-variant">
      <MatchRow
        v-for="match in upcomingMatches"
        :key="match.id"
        :match="match"
        :prediction="getPrediction(match.id)"
        :disabled="isDeadlinePassed(match.prediction_deadline_at)"
        :show-countdown="true"
        :show-add-icon="true"
        @click="emit('open-prediction', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useMatchesStore } from '@/stores/matches'
import { usePredictionsStore } from '@/stores/predictions'
import MatchRow from './MatchRow.vue'

const matchesStore = useMatchesStore()
const predictionsStore = usePredictionsStore()

const upcomingMatches = computed(() => matchesStore.matches)

const emit = defineEmits<{
  (e: 'open-prediction', matchId: number): void
}>()

onMounted(() => {
  matchesStore.fetchMatches({ status: 'upcoming', limit: 5 })
})

function getPrediction(matchId: number) {
  return predictionsStore.predictions.find(p => p.match_id === matchId) ?? null
}

function isDeadlinePassed(deadline: string): boolean {
  return new Date() > new Date(deadline)
}
</script>
