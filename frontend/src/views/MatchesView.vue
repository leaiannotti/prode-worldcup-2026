<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-3xl mx-auto space-y-6">

      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="font-headline-lg text-headline-lg text-primary">Partidos</h1>
          <p class="font-body-md text-on-surface-variant mt-1">Mundial 2026 — todos los partidos de la fase de grupos</p>
        </div>

        <!-- Filter -->
        <div class="relative">
          <select
            v-model="selectedGroup"
            @change="load"
            class="appearance-none w-full sm:w-44 px-4 py-2.5 pr-10 bg-surface-container-low border border-outline-variant rounded-xl text-sm font-medium text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none cursor-pointer"
          >
            <option value="">Todos los grupos</option>
            <option v-for="g in WORLD_CUP_GROUPS" :key="g" :value="g">Grupo {{ g }}</option>
          </select>
          <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="space-y-6">
        <div v-for="i in 3" :key="i" class="space-y-2">
          <div class="h-5 w-24 bg-surface-container animate-pulse rounded"></div>
          <div v-for="j in 3" :key="j" class="h-14 bg-surface-container animate-pulse rounded-xl"></div>
        </div>
      </div>

      <!-- Grouped matches -->
      <div v-else-if="groupedMatches.length > 0" class="space-y-6">
        <section v-for="group in groupedMatches" :key="group.name">
          <!-- Group header -->
          <div class="flex items-center gap-3 mb-2">
            <span class="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Grupo {{ group.name }}</span>
            <div class="flex-1 h-px bg-outline-variant"></div>
          </div>

          <!-- Matches list -->
          <div class="bg-surface-container-lowest rounded-xl border border-outline-variant divide-y divide-outline-variant overflow-hidden">
            <MatchRow
              v-for="match in group.matches"
              :key="match.id"
              :match="match"
              :prediction="getPrediction(match.id)"
              :disabled="isDeadlinePassed(match.prediction_deadline_at)"
              :show-countdown="true"
              :show-add-icon="!isDeadlinePassed(match.prediction_deadline_at)"
              @click="onMatchClick(matchesStore.matches.find(m => m.id === $event)!)"
            />
          </div>
        </section>
      </div>

      <!-- Empty -->
      <div v-else class="text-center py-12 text-on-surface-variant">
        <p class="font-body-md">No hay partidos para este grupo.</p>
      </div>
    </div>

    <!-- Prediction Modal -->
    <PredictionModal
      :is-open="isPredictionModalOpen"
      :match="selectedMatch"
      @close="isPredictionModalOpen = false; selectedMatch = null"
      @saved="predictionsStore.fetchMyPredictions(); activityStore.fetchActivity(10)"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useMatchesStore } from '@/stores/matches'
import { usePredictionsStore } from '@/stores/predictions'
import { useActivityStore } from '@/stores/activity'
import AppLayout from '@/components/AppLayout.vue'
import MatchRow from '@/components/MatchRow.vue'
import PredictionModal from '@/components/PredictionModal.vue'
import type { Match } from '@/stores/matches'

const WORLD_CUP_GROUPS = ['A','B','C','D','E','F','G','H','I','J','K','L']

const matchesStore = useMatchesStore()
const predictionsStore = usePredictionsStore()
const activityStore = useActivityStore()

const selectedGroup = ref('')
const isLoading = ref(false)
const isPredictionModalOpen = ref(false)
const selectedMatch = ref<Match | null>(null)

// Group matches by world cup group
const groupedMatches = computed(() => {
  const matches = matchesStore.matches
  if (!matches.length) return []

  if (selectedGroup.value) {
    return [{ name: selectedGroup.value, matches }]
  }

  const map = new Map<string, Match[]>()
  for (const m of matches) {
    const g = m.group?.name ?? '?'
    if (!map.has(g)) map.set(g, [])
    map.get(g)!.push(m)
  }

  return WORLD_CUP_GROUPS
    .filter(g => map.has(g))
    .map(g => ({ name: g, matches: map.get(g)! }))
})

onMounted(async () => {
  await Promise.all([load(), predictionsStore.fetchMyPredictions()])
})

async function load() {
  isLoading.value = true
  try {
    await matchesStore.fetchMatches({
      group: selectedGroup.value || undefined,
    })
  } finally {
    isLoading.value = false
  }
}

function onMatchClick(match: Match) {
  if (isDeadlinePassed(match.prediction_deadline_at)) return
  selectedMatch.value = match
  isPredictionModalOpen.value = true
}

function getPrediction(matchId: number) {
  return predictionsStore.predictions.find(p => p.match_id === matchId) ?? null
}

function isDeadlinePassed(deadline: string): boolean {
  return new Date() > new Date(deadline)
}



</script>
