<template>
  <!-- Only render when < 1h left or already closed -->
  <div v-if="isUrgent" class="flex items-center gap-1 flex-shrink-0">
    <svg class="w-3 h-3 text-error animate-pulse flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span class="text-[10px] text-error font-bold tabular-nums whitespace-nowrap">
      {{ t('match.closingIn', { time: timeLeft }) }}
    </span>
  </div>
  <div v-else-if="isClosed" class="flex items-center gap-1 flex-shrink-0">
    <svg class="w-3 h-3 text-outline flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
    </svg>
    <span class="text-[10px] text-outline font-medium">{{ t('match.closedBadge') }}</span>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useCountdown } from '@/composables/useCountdown'

const { t } = useI18n()
const props = defineProps<{ deadline: string }>()
const { timeLeft, isUrgent, isClosed } = useCountdown(props.deadline)
</script>
