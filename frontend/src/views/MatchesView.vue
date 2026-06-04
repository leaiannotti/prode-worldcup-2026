<template>
  <AppLayout>
    <div class="px-gutter py-lg max-w-7xl mx-auto space-y-lg">
      <!-- Header -->
      <section class="space-y-md">
        <h1 class="font-headline-lg text-headline-lg text-primary mb-xs">Matches</h1>
        <p class="font-body-lg text-body-lg text-on-surface-variant">
          Place your predictions for upcoming fixtures.
        </p>

        <!-- Filters -->
        <div class="flex flex-col md:flex-row gap-md">
          <select
            v-model="selectedGroup"
            @change="fetchMatches"
            class="flex-1 px-md py-sm border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none"
          >
            <option value="">All Groups</option>
            <option v-for="group in groupsStore.groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
          <input
            v-model="selectedDate"
            @change="fetchMatches"
            type="date"
            class="flex-1 px-md py-sm border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none"
          />
        </div>
      </section>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-lg">
        <p class="text-on-surface-variant font-body-lg">Loading matches...</p>
      </div>

      <!-- Matches Grid -->
      <div v-else-if="matchesStore.matches.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-md">
        <div v-for="match in matchesStore.matches" :key="match.id">
          <MatchCard :match="match">
            <template #prediction-form="{ isOpen }">
              <PredictionForm
                :deadline-utc="match.deadline_utc"
                :group-id="selectedGroup || ''"
                :match-id="match.id"
                :button-label="'Place Prediction'"
                @success="onPredictionSuccess"
                @error="onPredictionError"
              />
            </template>
          </MatchCard>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-lg">
        <svg class="w-16 h-16 mx-auto mb-md text-on-surface-variant opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
        </svg>
        <p class="font-body-lg text-body-lg text-on-surface-variant">No matches found.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { useMatchesStore } from '@/stores/matches'
import AppLayout from '@/components/AppLayout.vue'
import MatchCard from '@/components/MatchCard.vue'
import PredictionForm from '@/components/PredictionForm.vue'

const groupsStore = useGroupsStore()
const matchesStore = useMatchesStore()

const selectedGroup = ref('')
const selectedDate = ref('')
const isLoading = ref(false)

onMounted(async () => {
  try {
    await groupsStore.fetchGroups()
    await fetchMatches()
  } catch (error) {
    console.error('Error loading data:', error)
  }
})

async function fetchMatches() {
  isLoading.value = true
  try {
    await matchesStore.fetchMatches({
      group: selectedGroup.value || undefined,
      date: selectedDate.value || undefined,
    })
  } catch (error) {
    console.error('Error fetching matches:', error)
  } finally {
    isLoading.value = false
  }
}

function onPredictionSuccess(homeScore: number, awayScore: number) {
  console.log(`Prediction saved: ${homeScore} - ${awayScore}`)
}

function onPredictionError(error: Error) {
  console.error('Prediction error:', error)
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
