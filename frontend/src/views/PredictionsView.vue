<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-7xl mx-auto space-y-6">
      <!-- Header -->
      <section class="space-y-4">
        <h1 class="font-headline-lg text-headline-lg text-primary mb-1">{{ t('predictionsView.title') }}</h1>
        <p class="font-body-lg text-body-lg text-on-surface-variant">
          {{ t('predictionsView.subtitle') }}
        </p>
      </section>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-6">
        <p class="text-on-surface-variant font-body-lg">{{ t('predictionsView.loading') }}</p>
      </div>

      <!-- Predictions List -->
      <div v-else-if="predictionsStore.predictions.length > 0" class="space-y-4">
        <div v-for="prediction in predictionsStore.predictions" :key="prediction.id" class="bg-surface-container-lowest rounded-lg p-4 border border-outline-variant">
          <div class="flex flex-col md:flex-row justify-between md:items-center gap-4">
            <div class="space-y-1">
              <p class="font-label-md text-label-md text-on-surface-variant uppercase">{{ t('predictionsView.submittedAt', { time: formatDate(prediction.submitted_at) }) }}</p>
              <p class="font-headline-sm text-headline-sm text-primary">
                {{ prediction.home_score }} - {{ prediction.away_score }}
              </p>
              <p :class="`font-body-md ${prediction.is_frozen ? 'text-error' : 'text-secondary'}`">
                {{ prediction.is_frozen ? t('predictionsView.frozen') : t('predictionsView.canEdit') }}
              </p>
            </div>
            <button
              v-if="!prediction.is_frozen"
              @click="editPrediction(prediction)"
              class="px-6 py-4 bg-primary text-on-primary rounded-lg font-bold hover:opacity-90 transition-all"
            >
              {{ t('predictionsView.edit') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-6">
        <svg class="w-16 h-16 mx-auto mb-4 text-on-surface-variant opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="font-body-lg text-body-lg text-on-surface-variant">{{ t('predictionsView.empty') }}</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePredictionsStore, type Prediction } from '@/stores/predictions'
import AppLayout from '@/components/AppLayout.vue'

const { t } = useI18n()
const predictionsStore = usePredictionsStore()

const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    await predictionsStore.fetchMyPredictions()
  } catch (error) {
    console.error('Error loading predictions:', error)
  } finally {
    isLoading.value = false
  }
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function editPrediction(prediction: Prediction) {
  console.log('Edit prediction:', prediction)
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
