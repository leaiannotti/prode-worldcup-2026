<template>
  <div
    class="bg-surface-container-lowest rounded-lg p-md border transition-all"
    :class="isOpen ? 'border-outline-variant hover:border-primary' : 'border-error bg-opacity-75'"
  >
    <!-- Header: Time and Status Badge -->
    <div class="flex justify-between items-center mb-md">
      <div class="space-y-xs">
        <p class="font-label-md text-label-md text-on-surface-variant uppercase">
          {{ formatDate(match.kickoff_utc) }}
        </p>
        <p class="font-label-md text-label-md font-bold text-primary">{{ formatTime(match.kickoff_utc) }}</p>
      </div>

      <!-- Status Badge -->
      <div
        v-if="isOpen"
        class="flex items-center gap-xs bg-secondary text-on-secondary px-sm py-xs rounded-full font-label-md text-label-md uppercase animate-pulse"
      >
        <span class="w-2 h-2 rounded-full bg-on-secondary" />
        Open
      </div>
      <div v-else class="flex items-center gap-xs bg-error text-on-error px-sm py-xs rounded-full font-label-md text-label-md uppercase">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path
            fill-rule="evenodd"
            d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
            clip-rule="evenodd"
          />
        </svg>
        Closed
      </div>
    </div>

    <!-- Teams Section -->
    <div class="space-y-md mb-md">
      <!-- Home Team -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-sm flex-1">
          <div class="w-12 h-8 rounded border border-outline-variant overflow-hidden flex-shrink-0">
            <img :src="teamFlagUrl(match.home_team.code)" :alt="match.home_team.code" class="w-full h-full object-cover" />
          </div>
          <span class="font-headline-sm text-headline-sm text-primary truncate">{{ match.home_team.code }}</span>
        </div>
        <span v-if="match.status === 'finished' && match.home_score !== null" class="font-display-lg text-headline-lg text-on-surface">
          {{ match.home_score }}
        </span>
      </div>

      <!-- Away Team -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-sm flex-1">
          <div class="w-12 h-8 rounded border border-outline-variant overflow-hidden flex-shrink-0">
            <img :src="teamFlagUrl(match.away_team.code)" :alt="match.away_team.code" class="w-full h-full object-cover" />
          </div>
          <span class="font-headline-sm text-headline-sm text-primary truncate">{{ match.away_team.code }}</span>
        </div>
        <span v-if="match.status === 'finished' && match.away_score !== null" class="font-display-lg text-headline-lg text-on-surface">
          {{ match.away_score }}
        </span>
      </div>
    </div>

    <!-- Prediction Form or Result Display -->
    <div v-if="match.status !== 'finished'" class="space-y-md">
      <slot name="prediction-form" :is-open="isOpen">
        <div class="p-md bg-surface-container-low rounded-lg text-center text-on-surface-variant font-body-md">
          Add prediction form here
        </div>
      </slot>
    </div>
    <div v-else class="p-md bg-surface-container-low rounded-lg text-center">
      <p class="font-label-md text-label-md text-on-surface-variant uppercase mb-xs">Final Result</p>
      <p class="font-headline-sm text-headline-sm text-primary">
        {{ match.home_score }} - {{ match.away_score }}
      </p>
    </div>

    <!-- Time Remaining or Closed Message -->
    <div class="mt-md text-center">
      <p v-if="isOpen" class="text-secondary font-bold font-label-md text-label-md">
        Closes in {{ timeLeft }}
      </p>
      <p v-else class="text-error font-bold font-label-md text-label-md">
        Prediction Closed
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDeadlineGuard } from '@/composables/useDeadlineGuard'
import type { Match } from '@/stores/matches'

interface Props {
  match: Match
}

const props = defineProps<Props>()

const { isOpen, timeLeft } = useDeadlineGuard(props.match.deadline_utc)

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true })
}

function teamFlagUrl(teamCode: string): string {
  // Use placeholder flag service
  return `https://flagcdn.com/w80/${countryCodeMap[teamCode] || 'un'}.png`
}

// Map team codes to ISO country codes
const countryCodeMap: Record<string, string> = {
  USA: 'us',
  MEX: 'mx',
  CAN: 'ca',
  ARG: 'ar',
  BRA: 'br',
  URU: 'uy',
  FRA: 'fr',
  ESP: 'es',
  POR: 'pt',
  GER: 'de',
  ITA: 'it',
  NED: 'nl',
  BEL: 'be',
  ENG: 'gb-eng',
  JPN: 'jp',
  AUS: 'au',
  KOR: 'kr',
  CHN: 'cn',
  NZL: 'nz',
  MAR: 'ma',
  SEN: 'sn',
  CMR: 'cm',
  GHA: 'gh',
}
</script>

<style scoped>
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
