<template>
  <BottomSheet
    :is-open="isOpen"
    :show-close="true"
    @close="emit('close')"
  >
    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="h-12 bg-surface-container animate-pulse rounded-xl"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-body-md text-on-error">{{ t('friendRecentResults.loadingError') }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="history.length === 0" class="text-center py-8">
      <p class="text-body-md text-on-surface-variant">{{ t('friendRecentResults.empty') }}</p>
    </div>

    <!-- History rows -->
    <div v-else class="space-y-2">
      <div
        v-for="entry in history"
        :key="entry.match.id"
        class="flex items-center justify-between py-3 px-4 rounded-xl bg-surface-container-low"
      >
        <!-- Match teams -->
        <span class="text-sm font-semibold text-on-surface tabular-nums">
          {{ entry.match.home_team_code }} - {{ entry.match.away_team_code }}
        </span>

        <!-- Prediction or dash -->
        <span class="text-sm font-medium text-on-surface-variant tabular-nums">
          <template v-if="entry.prediction">
            {{ entry.prediction.home_score }} - {{ entry.prediction.away_score }}
          </template>
          <template v-else>
            {{ t('friendRecentResults.noPrediction') }}
          </template>
        </span>

        <!-- Points badge -->
        <span
          class="inline-flex items-center justify-center min-w-[2.5rem] px-2 py-1 rounded-full text-sm font-bold tabular-nums"
          :class="pointsBadgeClass(entry.points)"
        >
          {{ pointsPrefix(entry.points) }}{{ entry.points ?? 0 }}
        </span>
      </div>
    </div>
  </BottomSheet>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BottomSheet from './BottomSheet.vue'

interface MatchInfo {
  id: number
  home_team_code: string
  away_team_code: string
  kickoff_utc: string
  status: string
}

interface PredictionInfo {
  home_score: number
  away_score: number
}

export interface MemberHistoryEntry {
  match: MatchInfo
  actual_result?: { home_score: number; away_score: number } | null
  prediction?: PredictionInfo | null
  points: number | null
  score_type?: string | null
}

interface Props {
  isOpen: boolean
  userName: string
  history: MemberHistoryEntry[]
  loading: boolean
  error: string | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()

function pointsBadgeClass(points: number | null): string {
  switch (points) {
    case 3:
      return 'bg-tertiary-container text-on-tertiary-container'
    case 1:
      return 'bg-secondary-container text-on-secondary-container'
    case 0:
    default:
      return 'bg-error-container text-on-error-container'
  }
}

function pointsPrefix(points: number | null): string {
  if (points === null || points === undefined) return ''
  return points >= 0 ? '+' : ''
}
</script>
