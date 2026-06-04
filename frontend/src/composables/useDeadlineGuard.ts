/**
 * useDeadlineGuard composable — provides deadline-based state for predictions.
 * Determines if a prediction is still open based on the deadline UTC time.
 */
import { computed, ref } from 'vue'

export function useDeadlineGuard(deadlineUtc: string) {
  const now = ref(new Date())

  // Update current time every second
  if (typeof window !== 'undefined') {
    setInterval(() => {
      now.value = new Date()
    }, 1000)
  }

  /**
   * Check if prediction is still open (current time < deadline)
   */
  const isOpen = computed(() => {
    const deadline = new Date(deadlineUtc)
    return now.value < deadline
  })

  /**
   * Format time remaining until deadline as a countdown string
   */
  const timeLeft = computed(() => {
    const deadline = new Date(deadlineUtc)
    const msLeft = deadline.getTime() - now.value.getTime()

    if (msLeft <= 0) {
      return 'Closed'
    }

    const totalSeconds = Math.floor(msLeft / 1000)
    const days = Math.floor(totalSeconds / 86400)
    const hours = Math.floor((totalSeconds % 86400) / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const seconds = totalSeconds % 60

    if (days > 0) {
      return `${days}d ${hours}h`
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`
    } else {
      return `${seconds}s`
    }
  })

  return {
    isOpen,
    timeLeft,
  }
}
