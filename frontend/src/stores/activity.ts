/**
 * Activity store — manages activity feed state.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface ActivityEvent {
  id: string
  event_type: 'group_joined' | 'group_created' | 'prediction_submitted' | 'prediction_updated' | 'score_calculated' | 'prize_changed'
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
   * Fetch activity events for current user or group
   */
  async function fetchActivity(options?: { groupId?: string | number; eventType?: string; limit?: number }): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      const limit = options?.limit ?? 10
      params.append('limit', String(limit))
      if (options?.groupId !== undefined) {
        params.append('group_id', String(options.groupId))
      }
      if (options?.eventType !== undefined) {
        params.append('event_type', options.eventType)
      }
      const response = await apiClient.get(`/api/activity?${params.toString()}`)
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
