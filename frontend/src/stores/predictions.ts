/**
 * Predictions store — manages user predictions state and operations.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface Prediction {
  id: string
  user_id: string
  match_id: number
  group_id: string
  home_score: number
  away_score: number
  is_frozen: boolean
  submitted_at: string
}

export interface PredictionRequest {
  match_id: number
  group_id: string
  home_score: number
  away_score: number
}

export interface GroupPrediction {
  id: string
  user_id: string
  match_id: number
  home_score?: number | null
  away_score?: number | null
  submitted_at?: string
  is_frozen: boolean
}

export const usePredictionsStore = defineStore('predictions', () => {
  // State
  const predictions = ref<Prediction[]>([])
  const groupPredictions = ref<GroupPrediction[]>([])

  // Actions
  /**
   * Fetch user's predictions for a specific group
   */
  async function fetchMyPredictions(groupId: string): Promise<void> {
    try {
      const response = await apiClient.get(`/api/predictions?group_id=${groupId}`)
      predictions.value = response.data
    } catch (error) {
      console.error('Error fetching my predictions:', error)
      throw error
    }
  }

  /**
   * Fetch all predictions for a specific match in a group
   */
  async function fetchGroupPredictions(groupId: string, matchId: number): Promise<void> {
    try {
      const response = await apiClient.get(`/api/groups/${groupId}/matches/${matchId}/predictions`)
      groupPredictions.value = response.data
    } catch (error) {
      console.error('Error fetching group predictions:', error)
      throw error
    }
  }

  /**
   * Submit or update a prediction
   * Throws 423 error if match deadline has passed
   */
  async function submitPrediction(
    groupId: string,
    matchId: number,
    homeScore: number,
    awayScore: number
  ): Promise<Prediction> {
    try {
      const response = await apiClient.post('/api/predictions', {
        match_id: matchId,
        group_id: groupId,
        home_score: homeScore,
        away_score: awayScore,
      })

      const prediction = response.data

      // Update local cache
      const existingIndex = predictions.value.findIndex(
        (p) => p.match_id === matchId && p.group_id === groupId
      )
      if (existingIndex >= 0) {
        predictions.value[existingIndex] = prediction
      } else {
        predictions.value.push(prediction)
      }

      return prediction
    } catch (error: any) {
      // 423 Locked (deadline passed)
      if (error.response?.status === 423) {
        const err = new Error('Prediction locked: match deadline has passed')
        ;(err as any).status = 423
        throw err
      }
      console.error('Error submitting prediction:', error)
      throw error
    }
  }

  return {
    predictions,
    groupPredictions,
    fetchMyPredictions,
    fetchGroupPredictions,
    submitPrediction,
  }
})
