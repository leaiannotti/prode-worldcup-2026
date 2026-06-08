/**
 * useCountdown — reactive countdown to a deadline ISO string.
 *
 * Returns:
 *  - timeLeft: formatted string ("1h 45m", "45m 12s", "CERRADO")
 *  - isUrgent: true when < 1h remaining (triggers red styling)
 *  - isClosed: true when deadline has passed
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'

export function useCountdown(deadlineIso: string) {
  const msLeft = ref(new Date(deadlineIso).getTime() - Date.now())

  let timer: ReturnType<typeof setInterval> | null = null

  function tick() {
    msLeft.value = new Date(deadlineIso).getTime() - Date.now()
    if (msLeft.value <= 0 && timer) {
      clearInterval(timer)
      timer = null
    }
  }

  onMounted(() => {
    tick()
    timer = setInterval(tick, 1000)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  const isClosed = computed(() => msLeft.value <= 0)

  const isUrgent = computed(() => msLeft.value > 0 && msLeft.value < 60 * 60 * 1000) // < 1h

  const timeLeft = computed(() => {
    const ms = msLeft.value
    if (ms <= 0) return 'CERRADO'

    const totalSeconds = Math.floor(ms / 1000)
    const h = Math.floor(totalSeconds / 3600)
    const m = Math.floor((totalSeconds % 3600) / 60)
    const s = totalSeconds % 60

    if (h > 0) return `${h}h ${m}m`
    if (m > 0) return `${m}m ${String(s).padStart(2, '0')}s`
    return `${s}s`
  })

  return { timeLeft, isUrgent, isClosed }
}
