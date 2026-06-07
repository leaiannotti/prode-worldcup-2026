/**
 * Scores store — manages my-standing and leaderboard state.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface MyStandingItem {
  group_id: string
  group_name: string
  rank: number
  total_points: number
  member_count: number
}

export const useScoresStore = defineStore('scores', () => {
  // State
  const myStanding = ref<MyStandingItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  /**
   * Fetch cross-group rank summary for current user
   */
  async function fetchMyStanding(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/scores/my-standing')
      myStanding.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Error al cargar posición'
      console.error('Error fetching my standing:', err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    myStanding,
    isLoading,
    error,
    fetchMyStanding,
  }
})
