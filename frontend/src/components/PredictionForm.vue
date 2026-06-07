<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <!-- Score Inputs -->
    <div class="flex items-center justify-center gap-2 md:gap-4">
      <!-- Home Score -->
      <div class="flex flex-col items-center">
        <label class="font-label-md text-label-md text-on-surface-variant mb-1">Home</label>
        <input
          v-model.number="formData.homeScore"
          type="number"
          min="0"
          max="15"
          :disabled="!isOpen"
          class="w-16 h-16 text-center font-display-lg text-headline-lg border-2 rounded-xl transition-all"
          :class="
            isOpen
              ? 'border-outline-variant focus:border-secondary focus:ring-2 focus:ring-secondary-container'
              : 'border-outline-variant bg-surface-container-low text-on-surface-variant cursor-not-allowed'
          "
        />
      </div>

      <!-- Dash Separator -->
      <div class="font-display-lg text-outline-variant text-2xl mb-4">-</div>

      <!-- Away Score -->
      <div class="flex flex-col items-center">
        <label class="font-label-md text-label-md text-on-surface-variant mb-1">Away</label>
        <input
          v-model.number="formData.awayScore"
          type="number"
          min="0"
          max="15"
          :disabled="!isOpen"
          class="w-16 h-16 text-center font-display-lg text-headline-lg border-2 rounded-xl transition-all"
          :class="
            isOpen
              ? 'border-outline-variant focus:border-secondary focus:ring-2 focus:ring-secondary-container'
              : 'border-outline-variant bg-surface-container-low text-on-surface-variant cursor-not-allowed'
          "
        />
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="errorMessage" class="text-center">
      <p class="text-error font-label-md text-label-md">{{ errorMessage }}</p>
    </div>

    <!-- Deadline or Open Status -->
    <div class="text-center text-on-surface-variant font-body-md text-body-md">
      <p v-if="isOpen" class="text-secondary font-bold">
        Closes in {{ timeLeft }}
      </p>
      <p v-else class="text-error font-bold">
        Closed
      </p>
    </div>

    <!-- Submit Button -->
    <button
      type="submit"
      :disabled="!isOpen || isSubmitting"
      class="w-full py-4 px-6 rounded-lg font-bold transition-all active:scale-95"
      :class="
        isOpen && !isSubmitting
          ? 'bg-primary text-on-primary hover:opacity-90'
          : 'bg-surface-container text-on-surface-variant cursor-not-allowed opacity-50'
      "
    >
      <span v-if="isSubmitting">Saving...</span>
      <span v-else>{{ buttonLabel }}</span>
    </button>
  </form>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDeadlineGuard } from '@/composables/useDeadlineGuard'
import { usePredictionsStore } from '@/stores/predictions'

interface Props {
  deadlineUtc: string
  groupId: string
  matchId: number
  initialHomeScore?: number
  initialAwayScore?: number
  buttonLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  buttonLabel: 'Place Prediction',
})

const emit = defineEmits<{
  success: [homeScore: number, awayScore: number]
  error: [error: Error]
}>()

const { isOpen, timeLeft } = useDeadlineGuard(props.deadlineUtc)
const predictionsStore = usePredictionsStore()

const formData = ref({
  homeScore: props.initialHomeScore ?? 0,
  awayScore: props.initialAwayScore ?? 0,
})

const isSubmitting = ref(false)
const errorMessage = ref('')

const isFormValid = computed(() => {
  return (
    formData.value.homeScore >= 0 &&
    formData.value.awayScore >= 0 &&
    formData.value.homeScore <= 15 &&
    formData.value.awayScore <= 15
  )
})

async function handleSubmit() {
  if (!isFormValid.value || !isOpen.value) return

  isSubmitting.value = true
  errorMessage.value = ''

  try {
    await predictionsStore.submitPrediction(
      props.groupId,
      props.matchId,
      formData.value.homeScore,
      formData.value.awayScore
    )
    emit('success', formData.value.homeScore, formData.value.awayScore)
  } catch (error: any) {
    if (error.status === 423) {
      errorMessage.value = 'Predicción cerrada'
    } else {
      errorMessage.value = error.message || 'Error submitting prediction'
    }
    emit('error', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* Remove number input spinners */
input[type='number']::-webkit-outer-spin-button,
input[type='number']::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type='number'] {
  -moz-appearance: textfield;
}
</style>
