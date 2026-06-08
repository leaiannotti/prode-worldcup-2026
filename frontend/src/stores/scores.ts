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
  const myStanding = ref<MyStandingItem[]>([])
  const myTotalPoints = ref<number | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMyStanding(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/scores/my-standing')
      myStanding.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Error al cargar posición'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMyTotal(): Promise<void> {
    try {
      const response = await apiClient.get('/api/scores/my-total')
      myTotalPoints.value = response.data.total_points
    } catch {
      myTotalPoints.value = null
    }
  }

  return {
    myStanding,
    myTotalPoints,
    isLoading,
    error,
    fetchMyStanding,
    fetchMyTotal,
  }
})
