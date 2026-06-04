<template>
  <AppLayout>
    <div class="px-gutter py-lg max-w-7xl mx-auto space-y-lg">
      <!-- Header -->
      <section class="space-y-md">
        <h1 class="font-headline-lg text-headline-lg text-primary mb-xs">My Predictions</h1>
        <p class="font-body-lg text-body-lg text-on-surface-variant">
          Track all your predictions across groups.
        </p>

        <!-- Group Filter -->
        <select
          v-model="selectedGroup"
          @change="fetchPredictions"
          class="w-full md:w-64 px-md py-sm border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none"
        >
          <option value="">All Groups</option>
          <option v-for="group in groupsStore.groups" :key="group.id" :value="group.id">
            {{ group.name }}
          </option>
        </select>
      </section>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-lg">
        <p class="text-on-surface-variant font-body-lg">Loading predictions...</p>
      </div>

      <!-- Predictions List -->
      <div v-else-if="predictionsStore.predictions.length > 0" class="space-y-md">
        <div v-for="prediction in predictionsStore.predictions" :key="prediction.id" class="bg-surface-container-lowest rounded-lg p-md border border-outline-variant">
          <div class="flex flex-col md:flex-row justify-between md:items-center gap-md">
            <div class="space-y-xs">
              <p class="font-label-md text-label-md text-on-surface-variant uppercase">Submitted at {{ formatDate(prediction.submitted_at) }}</p>
              <p class="font-headline-sm text-headline-sm text-primary">
                {{ prediction.home_score }} - {{ prediction.away_score }}
              </p>
              <p :class="`font-body-md ${prediction.is_frozen ? 'text-error' : 'text-secondary'}`">
                {{ prediction.is_frozen ? 'Frozen' : 'Can Edit' }}
              </p>
            </div>
            <button
              v-if="!prediction.is_frozen"
              @click="editPrediction(prediction)"
              class="px-lg py-md bg-primary text-on-primary rounded-lg font-bold hover:opacity-90 transition-all"
            >
              Edit
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-lg">
        <svg class="w-16 h-16 mx-auto mb-md text-on-surface-variant opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="font-body-lg text-body-lg text-on-surface-variant">No predictions yet.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { usePredictionsStore } from '@/stores/predictions'
import AppLayout from '@/components/AppLayout.vue'

const groupsStore = useGroupsStore()
const predictionsStore = usePredictionsStore()

const selectedGroup = ref('')
const isLoading = ref(false)

onMounted(async () => {
  try {
    await groupsStore.fetchGroups()
    if (groupsStore.groups.length > 0) {
      selectedGroup.value = groupsStore.groups[0].id
      await fetchPredictions()
    }
  } catch (error) {
    console.error('Error loading data:', error)
  }
})

async function fetchPredictions() {
  if (!selectedGroup.value) return

  isLoading.value = true
  try {
    await predictionsStore.fetchMyPredictions(selectedGroup.value)
  } catch (error) {
    console.error('Error fetching predictions:', error)
  } finally {
    isLoading.value = false
  }
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function editPrediction(prediction: any) {
  console.log('Edit prediction:', prediction)
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
