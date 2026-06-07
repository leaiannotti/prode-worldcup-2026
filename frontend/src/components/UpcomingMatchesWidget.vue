<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Próximos Partidos</h2>

    <!-- Loading -->
    <div v-if="matchesStore.isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 bg-surface-container animate-pulse rounded-lg"></div>
    </div>

    <!-- Error -->
    <div v-else-if="matchesStore.error" class="text-error font-body-md">
      Error al cargar partidos
    </div>

    <!-- Empty -->
    <div v-else-if="upcomingMatches.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No hay partidos próximos
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="match in upcomingMatches"
        :key="match.id"
        @click="openDistribution(match.id)"
        class="flex items-center gap-3 p-3 bg-surface-container-low rounded-lg hover:bg-surface-container transition-colors cursor-pointer"
      >
        <!-- Home Team -->
        <div class="flex items-center gap-2 flex-1">
          <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" class="w-8 h-6 object-cover rounded" />
          <span class="font-body-md text-on-surface font-medium">{{ match.home_team.name }}</span>
        </div>

        <!-- VS -->
        <span class="font-label-md text-on-surface-variant">VS</span>

        <!-- Away Team -->
        <div class="flex items-center gap-2 flex-1 justify-end">
          <span class="font-body-md text-on-surface font-medium">{{ match.away_team.name }}</span>
          <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" class="w-8 h-6 object-cover rounded" />
        </div>

        <!-- Date -->
        <span class="font-label-sm text-on-surface-variant ml-2">{{ formatDate(match.kickoff_utc) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useMatchesStore } from '@/stores/matches'

const matchesStore = useMatchesStore()

const upcomingMatches = computed(() => matchesStore.matches)

onMounted(() => {
  matchesStore.fetchMatches({ status: 'upcoming', limit: 5 })
})

function openDistribution(matchId: number) {
  emit('open-distribution', matchId)
}

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const emit = defineEmits<{
  (e: 'open-distribution', matchId: number): void
}>()
</script>
