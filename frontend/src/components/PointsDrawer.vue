<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-[60] flex justify-end"
        @click.self="emit('close')"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/30" @click="emit('close')"></div>

        <!-- Panel -->
        <div class="relative w-full max-w-sm bg-surface h-full shadow-2xl flex flex-col">

          <!-- Header -->
          <div class="flex items-center justify-between px-5 py-4 border-b border-outline-variant">
            <div>
              <p class="text-xs font-medium uppercase tracking-widest text-on-surface-variant">{{ t('points.title') }}</p>
              <p class="text-2xl font-bold text-primary tabular-nums mt-0.5">{{ totalPoints ?? '—' }} pts</p>
            </div>
            <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors text-on-surface-variant">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Content -->
          <div class="flex-1 overflow-y-auto">

            <!-- Loading -->
            <div v-if="isLoading" class="p-5 space-y-3">
              <div v-for="i in 5" :key="i" class="h-14 bg-surface-container animate-pulse rounded-xl"></div>
            </div>

            <!-- Empty -->
            <div v-else-if="!scoredHistory.length" class="flex flex-col items-center justify-center h-48 text-on-surface-variant">
              <p class="text-sm">{{ t('points.noPoints') }}</p>
              <p class="text-xs mt-1">{{ t('points.noPointsHint') }}</p>
            </div>

            <!-- Scored predictions -->
            <div v-else class="divide-y divide-outline-variant">
              <div
                v-for="entry in scoredHistory"
                :key="`${entry.match.id}`"
                class="px-5 py-4 flex items-center gap-3"
              >
                <!-- Points badge -->
                <div
                  class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm tabular-nums"
                  :class="pointsStyle(entry.points)"
                >
                  +{{ entry.points }}
                </div>

                <!-- Match info -->
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-on-surface">
                    {{ entry.match.home_team_code }} vs {{ entry.match.away_team_code }}
                  </p>
                  <div class="flex items-center gap-2 mt-0.5">
                    <!-- Actual result -->
                    <span class="text-xs text-on-surface-variant tabular-nums">
                      {{ entry.actual_result?.home_score }}-{{ entry.actual_result?.away_score }}
                    </span>
                    <span class="text-on-surface-variant/30 text-xs">·</span>
                    <!-- My prediction -->
                    <span class="text-xs text-on-surface-variant">
                      {{ t('points.myPred') }} {{ entry.prediction.home_score }}-{{ entry.prediction.away_score }}
                    </span>
                  </div>
                </div>

                <!-- Score type label -->
                <span class="flex-shrink-0 text-[10px] uppercase tracking-wide font-medium" :class="typeColor(entry.points)">
                  {{ scoreLabel(entry.points) }}
                </span>
              </div>
            </div>

            <!-- Pending predictions (no score yet) -->
            <div v-if="pendingHistory.length" class="border-t border-outline-variant">
              <p class="px-5 py-3 text-[10px] uppercase tracking-widest text-on-surface-variant font-medium">
                {{ t('points.pending') }}
              </p>
              <div class="divide-y divide-outline-variant">
                <div
                  v-for="entry in pendingHistory"
                  :key="`pending-${entry.match.id}`"
                  class="px-5 py-3 flex items-center gap-3 opacity-50"
                >
                  <div class="w-10 h-10 rounded-full border-2 border-dashed border-outline-variant flex items-center justify-center text-xs text-on-surface-variant">?</div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm text-on-surface">{{ entry.match.home_team_code }} vs {{ entry.match.away_team_code }}</p>
                    <p class="text-xs text-on-surface-variant mt-0.5">{{ t('points.myPred') }} {{ entry.prediction.home_score }}-{{ entry.prediction.away_score }}</p>
                  </div>
                  <span class="text-[10px] text-on-surface-variant uppercase tracking-wide">{{ t('points.waiting') }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { apiClient } from '@/lib/api'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  isOpen: boolean
  totalPoints: number | null
}>()

const emit = defineEmits<{ (e: 'close'): void }>()
const { t } = useI18n()

interface HistoryEntry {
  match: { id: number; home_team_code: string; away_team_code: string; kickoff_utc: string; status: string }
  prediction: { home_score: number; away_score: number }
  actual_result: { home_score: number; away_score: number } | null
  points: number | null
}

const history = ref<HistoryEntry[]>([])
const isLoading = ref(false)

const scoredHistory = computed(() => history.value.filter(e => e.points !== null))
const pendingHistory = computed(() => history.value.filter(e => e.points === null && e.match.status !== 'finished'))

watch(() => props.isOpen, async (open) => {
  if (open) await load()
})

async function load() {
  isLoading.value = true
  try {
    const res = await apiClient.get('/api/scores/history')
    history.value = res.data.history
  } catch (e) {
    console.error('Error loading history', e)
  } finally {
    isLoading.value = false
  }
}

function pointsStyle(points: number | null): string {
  if (points === 3) return 'bg-tertiary text-on-tertiary'
  if (points === 1) return 'bg-secondary text-on-secondary'
  return 'bg-surface-container text-on-surface-variant'
}

function typeColor(points: number | null): string {
  if (points === 3) return 'text-tertiary'
  if (points === 1) return 'text-secondary'
  return 'text-on-surface-variant'
}

function scoreLabel(points: number | null): string {
  if (points === 3) return t('points.exact')
  if (points === 1) return t('points.outcome')
  return t('points.noScore')
}
</script>

<style scoped>
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-enter-active .relative,
.drawer-leave-active .relative {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}
.drawer-enter-from .relative {
  transform: translateX(100%);
}
</style>
