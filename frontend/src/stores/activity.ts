/**
 * Activity store — manages activity feed state.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface ActivityEvent {
  id: string
  event_type: 'group_joined' | 'group_created' | 'prediction_submitted' | 'prediction_updated' | 'score_calculated'
  group_id: string | null
  match_id: number | null
  payload: Record<string, any>
  occurred_at: string
}

export const useActivityStore = defineStore('activity', () => {
  // State
  const events = ref<ActivityEvent[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  /**
   * Fetch activity events for current user
   */
  async function fetchActivity(limit: number = 10): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/api/activity?limit=${limit}`)
      events.value = response.data.events
    } catch (err: any) {
      error.value = err.message || 'Error al cargar actividad'
      console.error('Error fetching activity:', err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    events,
    isLoading,
    error,
    fetchActivity,
  }
})
