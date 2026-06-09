<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <div class="bg-surface rounded-xl p-6 max-w-md w-full space-y-4">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h3 class="font-headline-sm text-headline-sm text-primary">{{ t('distribution.title') }}</h3>
        <button @click="close" class="text-on-surface-variant hover:text-on-surface">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Match Info -->
      <div v-if="match" class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" class="w-8 h-6 rounded" />
          <span class="font-body-md font-medium">{{ match.home_team.name }}</span>
        </div>
        <span class="font-label-md text-on-surface-variant">VS</span>
        <div class="flex items-center gap-2">
          <span class="font-body-md font-medium">{{ match.away_team.name }}</span>
          <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" class="w-8 h-6 rounded" />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="h-32 bg-surface-container animate-pulse rounded-lg"></div>

      <!-- Pre-deadline -->
      <div v-else-if="distribution && !distribution.available" class="text-center py-6">
        <p class="font-body-md text-on-surface-variant">
          {{ t('distribution.preClosed') }}
        </p>
        <p class="font-label-sm text-on-surface-variant mt-1">
          {{ t('distribution.deadline') }} {{ formatDate(match?.prediction_deadline_at) }}
        </p>
      </div>

      <!-- Distribution -->
      <div v-else-if="distribution && distribution.available" class="space-y-4">
        <p class="font-label-md text-on-surface-variant text-center">
          {{ t('distribution.predictions', { count: distribution.total_predictions }) }}
        </p>

        <!-- Home Win -->
        <div class="space-y-1">
          <div class="flex justify-between font-body-md">
            <span>{{ t('distribution.homeWin', { team: match?.home_team.name }) }}</span>
            <span class="font-bold">{{ distribution.home_win_pct }}%</span>
          </div>
          <div class="h-4 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-primary transition-all" :style="{ width: distribution.home_win_pct + '%' }"></div>
          </div>
        </div>

        <!-- Draw -->
        <div class="space-y-1">
          <div class="flex justify-between font-body-md">
            <span>{{ t('distribution.draw') }}</span>
            <span class="font-bold">{{ distribution.draw_pct }}%</span>
          </div>
          <div class="h-4 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-secondary transition-all" :style="{ width: distribution.draw_pct + '%' }"></div>
          </div>
        </div>

        <!-- Away Win -->
        <div class="space-y-1">
          <div class="flex justify-between font-body-md">
            <span>{{ t('distribution.awayWin', { team: match?.away_team.name }) }}</span>
            <span class="font-bold">{{ distribution.away_win_pct }}%</span>
          </div>
          <div class="h-4 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-tertiary transition-all" :style="{ width: distribution.away_win_pct + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-error font-body-md text-center">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { apiClient } from '@/lib/api'
import { useI18n } from 'vue-i18n'

interface Distribution {
  available: boolean
  match_id: number
  home_win_pct: number
  draw_pct: number
  away_win_pct: number
  total_predictions: number
  reason?: string
}

const props = defineProps<{
  isOpen: boolean
  matchId: number | null
  match: any
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()
const distribution = ref<Distribution | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

watch(() => props.isOpen, async (open) => {
  if (open && props.matchId) {
    await loadDistribution(props.matchId)
  }
})

async function loadDistribution(matchId: number) {
  isLoading.value = true
  error.value = null
  try {
    const response = await apiClient.get(`/api/matches/${matchId}/distribution`)
    distribution.value = response.data
  } catch (err: any) {
        error.value = err.message || t('distribution.error')
  } finally {
    isLoading.value = false
  }
}

function close() {
  distribution.value = null
  error.value = null
  emit('close')
}

function formatDate(isoDate: string | undefined): string {
  if (!isoDate) return ''
  return new Date(isoDate).toLocaleString(undefined, {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
