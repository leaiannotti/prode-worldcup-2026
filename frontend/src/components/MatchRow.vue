<template>
  <div
    @click="handleClick"
    role="button"
    :tabindex="disabled || clickable === false ? -1 : 0"
    @keydown.enter="handleClick"
    class="w-full text-left transition-colors rounded-lg"
    :class="[
      disabled ? 'cursor-default opacity-60' : clickable === false ? 'cursor-default' : 'hover:bg-surface-container cursor-pointer active:bg-surface-container'
    ]"
  >
  <!-- Mobile: 2-line compact layout (< sm) -->
  <div class="flex sm:hidden items-center gap-2 px-3 py-3 select-none">
      <!-- Flags side by side -->
      <div class="flex flex-col items-center gap-1 flex-shrink-0">
        <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" :alt="match.home_team.code"
          class="w-6 h-4 object-cover rounded-sm border border-outline-variant/40" />
        <div v-else class="w-6 h-4 rounded-sm bg-surface-container flex items-center justify-center">
          <span class="text-[8px] font-mono text-on-surface-variant">{{ match.home_team.code }}</span>
        </div>
        <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" :alt="match.away_team.code"
          class="w-6 h-4 object-cover rounded-sm border border-outline-variant/40" />
        <div v-else class="w-6 h-4 rounded-sm bg-surface-container flex items-center justify-center">
          <span class="text-[8px] font-mono text-on-surface-variant">{{ match.away_team.code }}</span>
        </div>
      </div>

      <!-- Team names -->
      <div class="flex-1 min-w-0 space-y-0.5">
        <p class="text-xs font-medium text-on-surface truncate" :class="homeWon ? 'font-bold' : ''">{{ match.home_team.name }}</p>
        <p class="text-xs font-medium text-on-surface truncate" :class="awayWon ? 'font-bold' : ''">{{ match.away_team.name }}</p>
      </div>

      <!-- Score / VS -->
      <div class="flex-shrink-0 flex flex-col items-center justify-center w-10">
        <template v-if="match.status === 'finished' && match.home_score !== null">
          <span class="text-xs font-bold text-on-surface tabular-nums">{{ match.home_score }}-{{ match.away_score }}</span>
          <span class="text-[8px] uppercase tracking-wide text-on-surface-variant">Final</span>
        </template>
        <template v-else-if="isPendingResult">
          <span class="text-[9px] font-medium text-on-surface-variant/60 leading-tight text-center">Procesando</span>
          <span class="text-[8px] text-on-surface-variant/40">resultado</span>
        </template>
        <template v-else>
          <span class="text-[10px] font-medium text-on-surface-variant">{{ formatTime(match.kickoff_at) }}</span>
          <span class="text-[9px] text-on-surface-variant/70">{{ formatDay(match.kickoff_at) }}</span>
        </template>
      </div>

      <!-- Prediction + countdown -->
      <div class="flex-shrink-0 flex flex-col items-end gap-0.5 min-w-[2.5rem]">
        <template v-if="prediction">
          <span class="text-[10px] font-bold tabular-nums text-secondary bg-secondary-container px-1 py-0.5 rounded">
            {{ prediction.home_score }}-{{ prediction.away_score }}
          </span>
          <span v-if="prediction.points !== null" class="text-[9px] font-bold tabular-nums text-tertiary">+{{ prediction.points }}pts</span>
        </template>
        <svg v-else-if="showAddIcon" class="w-3.5 h-3.5 text-on-surface-variant/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
        </svg>
        <MatchCountdownBadge v-if="showCountdown" :deadline="match.prediction_deadline_at" class="text-[9px]" />
      </div>
    </div>

    <!-- Desktop: single-row layout (>= sm) -->
    <div class="hidden sm:flex flex-col gap-1 py-3 px-3">
      <div class="flex items-center gap-3">
        <!-- Date column -->
        <div class="flex-shrink-0 w-14 text-center">
          <p class="text-[10px] font-medium uppercase tracking-wide text-on-surface-variant leading-none">{{ formatDay(match.kickoff_at) }}</p>
          <p class="text-xs font-bold text-primary leading-tight mt-0.5">{{ formatTime(match.kickoff_at) }}</p>
        </div>

        <div class="w-px h-8 bg-outline-variant flex-shrink-0"></div>

        <!-- Home team -->
        <div class="flex items-center gap-2 flex-1 min-w-0 justify-end">
          <span class="text-sm truncate text-right" :class="homeWon ? 'font-bold text-on-surface' : 'text-on-surface-variant'">{{ match.home_team.name }}</span>
          <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" :alt="match.home_team.code"
            class="w-7 h-5 object-cover rounded-sm flex-shrink-0 border border-outline-variant/40" />
          <div v-else class="w-7 h-5 rounded-sm flex-shrink-0 bg-surface-container flex items-center justify-center">
            <span class="text-[9px] font-mono text-on-surface-variant">{{ match.home_team.code }}</span>
          </div>
        </div>

        <!-- Score / VS -->
        <div class="flex-shrink-0 w-12 flex flex-col items-center">
          <template v-if="match.status === 'finished' && match.home_score !== null">
            <span class="text-sm font-bold text-on-surface tabular-nums">{{ match.home_score }} - {{ match.away_score }}</span>
            <span class="text-[9px] uppercase tracking-wide text-on-surface-variant">Final</span>
          </template>
          <template v-else-if="isPendingResult">
            <span class="text-[10px] font-medium text-on-surface-variant/60 leading-tight text-center">Procesando</span>
            <span class="text-[9px] text-on-surface-variant/40">resultado</span>
          </template>
          <template v-else>
            <span class="text-xs font-medium text-on-surface-variant">VS</span>
          </template>
        </div>

        <!-- Away team -->
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" :alt="match.away_team.code"
            class="w-7 h-5 object-cover rounded-sm flex-shrink-0 border border-outline-variant/40" />
          <div v-else class="w-7 h-5 rounded-sm flex-shrink-0 bg-surface-container flex items-center justify-center">
            <span class="text-[9px] font-mono text-on-surface-variant">{{ match.away_team.code }}</span>
          </div>
          <span class="text-sm truncate" :class="awayWon ? 'font-bold text-on-surface' : 'text-on-surface-variant'">{{ match.away_team.name }}</span>
        </div>

        <!-- Prediction badge -->
        <div class="flex-shrink-0 ml-1 flex flex-col items-end gap-0.5 min-w-[3rem]">
          <template v-if="prediction">
            <span class="text-xs font-bold tabular-nums text-secondary bg-secondary-container px-1.5 py-0.5 rounded">
              {{ prediction.home_score }}-{{ prediction.away_score }}
            </span>
            <span v-if="prediction.points !== null" :class="pointsColor(prediction.points)" class="text-[10px] font-bold tabular-nums">
              +{{ prediction.points }}pts
            </span>
          </template>
          <svg v-else-if="showAddIcon" class="w-4 h-4 text-on-surface-variant/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4" />
          </svg>
        </div>
      </div>

      <!-- Countdown -->
      <div v-if="showCountdown" class="pl-[4.5rem]">
        <MatchCountdownBadge :deadline="match.prediction_deadline_at" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Match } from '@/stores/matches'
import type { Prediction } from '@/stores/predictions'
import MatchCountdownBadge from './MatchCountdownBadge.vue'
import { formatDay, formatTime } from '@/composables/useDateFormat'

const props = withDefaults(defineProps<{
  match: Match
  prediction?: Prediction | null
  clickable?: boolean
  disabled?: boolean
  showCountdown?: boolean
  showAddIcon?: boolean
}>(), {
  clickable: true,
  disabled: false,
})

const emit = defineEmits<{ (e: 'select', matchId: number): void }>()

const isPendingResult = computed(() =>
  props.match.home_score === null &&
  new Date() > new Date(props.match.prediction_deadline_at)
)

const homeWon = computed(() =>
  props.match.status === 'finished' &&
  props.match.home_score !== null &&
  props.match.away_score !== null &&
  props.match.home_score > props.match.away_score
)

const awayWon = computed(() =>
  props.match.status === 'finished' &&
  props.match.home_score !== null &&
  props.match.away_score !== null &&
  props.match.away_score > props.match.home_score
)

function handleClick() {
  if (!props.disabled && props.clickable !== false) {
    emit('select', props.match.id)
  }
}

function pointsColor(points: number | null) {
  if (points === 3) return 'text-tertiary'
  if (points === 1) return 'text-secondary'
  return 'text-on-surface-variant'
}
</script>
