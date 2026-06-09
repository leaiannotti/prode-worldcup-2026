<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen && match"
        class="fixed inset-0 bg-black/60 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4"
        @click.self="emit('close')"
      >
        <div class="bg-surface w-full sm:max-w-md sm:rounded-xl rounded-t-2xl p-6 space-y-5 shadow-xl">

          <!-- Header -->
          <div class="flex items-center justify-between">
            <div>
              <p class="text-[11px] font-medium uppercase tracking-widest text-on-surface-variant">
                Grupo {{ match.group?.name }} · {{ formatDay(match.kickoff_at) }}
              </p>
              <p class="text-sm font-bold text-primary mt-0.5">{{ formatTime(match.kickoff_at) }}</p>
            </div>
            <button
              @click="emit('close')"
              class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors text-on-surface-variant"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Teams -->
          <div class="flex items-center justify-between gap-4">
            <!-- Home -->
            <div class="flex flex-col items-center gap-2 flex-1">
              <img
                v-if="match.home_team.flag_url"
                :src="match.home_team.flag_url"
                :alt="match.home_team.code"
                class="w-12 h-8 object-cover rounded border border-outline-variant/40"
              />
              <div v-else class="w-12 h-8 rounded bg-surface-container flex items-center justify-center">
                <span class="text-xs font-mono text-on-surface-variant">{{ match.home_team.code }}</span>
              </div>
              <span class="text-sm font-medium text-on-surface text-center leading-tight">{{ match.home_team.name }}</span>
            </div>

            <!-- VS -->
            <span class="text-sm font-bold text-on-surface-variant">VS</span>

            <!-- Away -->
            <div class="flex flex-col items-center gap-2 flex-1">
              <img
                v-if="match.away_team.flag_url"
                :src="match.away_team.flag_url"
                :alt="match.away_team.code"
                class="w-12 h-8 object-cover rounded border border-outline-variant/40"
              />
              <div v-else class="w-12 h-8 rounded bg-surface-container flex items-center justify-center">
                <span class="text-xs font-mono text-on-surface-variant">{{ match.away_team.code }}</span>
              </div>
              <span class="text-sm font-medium text-on-surface text-center leading-tight">{{ match.away_team.name }}</span>
            </div>
          </div>

          <!-- Deadline warning if close -->
          <div v-if="isDeadlineSoon" class="flex items-center gap-2 bg-error-container text-on-error-container text-xs font-medium px-3 py-2 rounded-lg">
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            {{ t('prediction.closesIn') }} {{ timeLeft }}
          </div>

          <!-- Score inputs -->
          <div class="flex items-center gap-4">
            <!-- Home score -->
            <div class="flex-1 space-y-1">
              <label class="text-xs font-medium text-on-surface-variant block text-center">{{ match.home_team.name }}</label>
              <div class="flex items-center justify-center gap-2">
                <button
                  @click="homeScore = Math.max(0, homeScore - 1)"
                  class="w-9 h-9 rounded-full bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface font-bold text-lg active:scale-95"
                >−</button>
                <span class="text-3xl font-bold text-on-surface tabular-nums w-8 text-center">{{ homeScore }}</span>
                <button
                  @click="homeScore++"
                  class="w-9 h-9 rounded-full bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface font-bold text-lg active:scale-95"
                >+</button>
              </div>
            </div>

            <span class="text-xl font-bold text-on-surface-variant self-end pb-1">:</span>

            <!-- Away score -->
            <div class="flex-1 space-y-1">
              <label class="text-xs font-medium text-on-surface-variant block text-center">{{ match.away_team.name }}</label>
              <div class="flex items-center justify-center gap-2">
                <button
                  @click="awayScore = Math.max(0, awayScore - 1)"
                  class="w-9 h-9 rounded-full bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface font-bold text-lg active:scale-95"
                >−</button>
                <span class="text-3xl font-bold text-on-surface tabular-nums w-8 text-center">{{ awayScore }}</span>
                <button
                  @click="awayScore++"
                  class="w-9 h-9 rounded-full bg-surface-container hover:bg-surface-container-high transition-colors text-on-surface font-bold text-lg active:scale-95"
                >+</button>
              </div>
            </div>
          </div>

          <!-- Error -->
          <p v-if="errorMsg" class="text-error text-sm text-center">{{ errorMsg }}</p>

          <!-- Submit -->
          <button
            @click="submit"
            :disabled="isSubmitting || isDeadlinePassed"
            class="w-full py-3 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all active:scale-[0.98] disabled:opacity-40"
          >
            <span v-if="isSubmitting">{{ t('prediction.saving') }}</span>
            <span v-else-if="isDeadlinePassed">{{ t('prediction.closed') }}</span>
            <span v-else-if="existingPrediction">{{ t('prediction.update') }}</span>
            <span v-else>{{ t('prediction.save') }}</span>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { usePredictionsStore } from '@/stores/predictions'
import type { Match } from '@/stores/matches'
import { formatDay, formatTime } from '@/composables/useDateFormat'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  isOpen: boolean
  match: Match | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
}>()

const { t } = useI18n()
const predictionsStore = usePredictionsStore()

const homeScore = ref(0)
const awayScore = ref(0)
const isSubmitting = ref(false)
const errorMsg = ref<string | null>(null)

// Pre-fill with existing prediction when modal opens
watch(() => props.isOpen, (open) => {
  if (!open || !props.match) return
  errorMsg.value = null

  const existing = predictionsStore.predictions.find(p => p.match_id === props.match!.id)
  if (existing) {
    homeScore.value = existing.home_score
    awayScore.value = existing.away_score
  } else {
    homeScore.value = 0
    awayScore.value = 0
  }
})

const existingPrediction = computed(() =>
  props.match
    ? predictionsStore.predictions.find(p => p.match_id === props.match!.id) ?? null
    : null
)

const isDeadlinePassed = computed(() => {
  if (!props.match) return false
  return new Date() > new Date(props.match.prediction_deadline_at)
})

const isDeadlineSoon = computed(() => {
  if (!props.match || isDeadlinePassed.value) return false
  const msLeft = new Date(props.match.prediction_deadline_at).getTime() - Date.now()
  return msLeft < 3 * 60 * 60 * 1000 // less than 3 hours
})

const timeLeft = computed(() => {
  if (!props.match) return ''
  const ms = new Date(props.match.prediction_deadline_at).getTime() - Date.now()
  const h = Math.floor(ms / 3600000)
  const m = Math.floor((ms % 3600000) / 60000)
  if (ms <= 0) return t('prediction.closedLabel')
  return h > 0 ? `${h}h ${m}m` : `${m}m`
})

async function submit() {
  if (!props.match || isSubmitting.value) return
  isSubmitting.value = true
  errorMsg.value = null
  try {
    await predictionsStore.submitPrediction(
      props.match.id,
      homeScore.value,
      awayScore.value
    )
    emit('saved')
    emit('close')
  } catch (err: any) {
    if (err.status === 423) {
      errorMsg.value = t('prediction.closedError')
    } else {
      errorMsg.value = t('prediction.saveError')
    }
  } finally {
    isSubmitting.value = false
  }
}


</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .bg-surface,
.modal-leave-active .bg-surface {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .bg-surface {
  transform: translateY(2rem);
}
</style>
