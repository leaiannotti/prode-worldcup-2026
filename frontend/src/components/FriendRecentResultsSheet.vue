<template>
  <BottomSheet
    :is-open="isOpen"
    :show-close="true"
    @close="emit('close')"
  >
    <!-- Loading skeleton -->
    <div v-if="loading" class="p-4 sm:p-6">
      <table class="w-full">
        <thead>
          <tr class="border-b border-outline-variant">
            <th class="w-[45%] py-2 text-left"><div class="h-4 bg-surface-container animate-pulse rounded w-20"></div></th>
            <th class="w-[30%] py-2 text-center"><div class="h-4 bg-surface-container animate-pulse rounded w-16 mx-auto"></div></th>
            <th class="w-[25%] py-2 text-right"><div class="h-4 bg-surface-container animate-pulse rounded w-12 ml-auto"></div></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="i in 5" :key="i" class="border-b border-outline-variant/50">
            <td class="py-2"><div class="h-4 bg-surface-container animate-pulse rounded w-24"></div></td>
            <td class="py-2"><div class="h-4 bg-surface-container animate-pulse rounded w-12 mx-auto"></div></td>
            <td class="py-2"><div class="h-5 bg-surface-container animate-pulse rounded-full w-10 ml-auto"></div></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-8">
      <p class="text-body-md text-on-error">{{ t('friendRecentResults.loadingError') }}</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="history.length === 0" class="text-center py-8">
      <p class="text-body-md text-on-surface-variant">{{ t('friendRecentResults.empty') }}</p>
    </div>

    <!-- Content: header + table -->
    <div v-else class="p-4 sm:p-6">
      <!-- Header block -->
      <div class="flex items-center gap-3 pb-4 mb-4 border-b border-outline-variant">
        <!-- Avatar -->
        <div class="w-11 h-11 rounded-full flex-shrink-0 overflow-hidden bg-primary flex items-center justify-center">
          <img
            v-if="userPicture"
            :src="userPicture"
            :alt="userName"
            class="w-full h-full object-cover"
          />
          <span v-else class="text-on-primary text-sm font-bold">{{ initials(userName) }}</span>
        </div>

        <!-- Name + points -->
        <div class="flex-1 min-w-0">
          <p class="text-headline-sm font-semibold text-on-surface truncate">{{ userName }}</p>
          <p v-if="totalPoints !== null" class="text-body-sm tabular-nums">
            <span class="font-bold text-on-surface">{{ totalPoints }} {{ t('common.pts') }}</span>
          </p>
        </div>
      </div>

      <!-- Table -->
      <table class="w-full border-collapse">
        <thead>
          <tr class="border-b border-outline-variant">
            <th class="w-[45%] py-2 text-left text-label-md text-on-surface-variant font-semibold uppercase tracking-wide text-xs">
              {{ t('friendRecentResults.columnMatch') }}
            </th>
            <th class="w-[30%] py-2 text-center text-label-md text-on-surface-variant font-semibold uppercase tracking-wide text-xs">
              {{ t('friendRecentResults.columnPrediction') }}
            </th>
            <th class="w-[25%] py-2 text-right text-label-md text-on-surface-variant font-semibold uppercase tracking-wide text-xs">
              {{ t('friendRecentResults.columnPoints') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(entry, idx) in history"
            :key="entry.match.id"
            class="border-b border-outline-variant/50"
            :class="{ 'border-b-0': idx === history.length - 1 }"
          >
            <!-- Match -->
            <td class="py-2 text-left">
              <span class="text-sm font-semibold text-on-surface tabular-nums">
                {{ entry.match.home_team_code }} – {{ entry.match.away_team_code }}
              </span>
            </td>

            <!-- Prediction -->
            <td class="py-2 text-center">
              <span class="text-sm font-medium tabular-nums" :class="entry.prediction ? 'text-on-surface' : 'text-on-surface-variant'">
                <template v-if="entry.prediction">
                  {{ entry.prediction.home_score }}–{{ entry.prediction.away_score }}
                </template>
                <template v-else>
                  {{ t('friendRecentResults.noPrediction') }}
                </template>
              </span>
            </td>

            <!-- Points -->
            <td class="py-2 text-right">
              <span
                class="inline-flex items-center justify-center min-w-[2.5rem] px-2 py-1 rounded-full text-sm font-bold tabular-nums"
                :class="pointsBadgeClass(entry.points)"
              >
                {{ pointsPrefix(entry.points) }}{{ entry.points ?? 0 }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Footer note -->
      <p class="mt-3 text-right text-xs text-on-surface-variant/70">
        {{ t('friendRecentResults.subtitle') }}
      </p>
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
  userPicture: string | null
  totalPoints: number | null
  history: MemberHistoryEntry[]
  loading: boolean
  error: string | null
}

defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()

function initials(name: string): string {
  return name
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function pointsBadgeClass(points: number | null): string {
  switch (points) {
    case 3:
      return 'bg-tertiary text-on-tertiary'
    case 1:
      return 'bg-secondary text-on-secondary'
    case 0:
    default:
      return 'bg-surface-container text-on-surface-variant'
  }
}

function pointsPrefix(points: number | null): string {
  if (points === null || points === undefined) return ''
  return points >= 0 ? '+' : ''
}
</script>
