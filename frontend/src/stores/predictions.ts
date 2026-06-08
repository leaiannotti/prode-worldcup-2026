/**
 * Predictions store — manages user predictions state and operations.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface Prediction {
  id: string
  user_id?: string
  match_id: number
  home_score: number
  away_score: number
  is_frozen: boolean
  submitted_at: string
  points: number | null
}

export interface PredictionRequest {
  match_id: number
  home_score: number
  away_score: number
}

export interface GroupPrediction {
  user_id: string
  name: string
  picture?: string | null
  home_score?: number | null
  away_score?: number | null
  submitted_at?: string
}

export const usePredictionsStore = defineStore('predictions', () => {
  // State
  const predictions = ref<Prediction[]>([])
  const groupPredictions = ref<GroupPrediction[]>([])

  // Actions
  /**
   * Fetch all predictions for the current user.
   * Predictions are global (not per group).
   */
  async function fetchMyPredictions(): Promise<void> {
    try {
      const response = await apiClient.get('/api/predictions')
      predictions.value = response.data
    } catch (error) {
      console.error('Error fetching my predictions:', error)
      throw error
    }
  }

  /**
   * Fetch all group member predictions for a specific match.
   */
  async function fetchGroupPredictions(groupId: string, matchId: number): Promise<void> {
    try {
      const response = await apiClient.get(`/api/predictions/matches/${matchId}/group/${groupId}`)
      groupPredictions.value = response.data
    } catch (error) {
      console.error('Error fetching group predictions:', error)
      throw error
    }
  }

  /**
   * Submit or update a prediction for a match.
   * Throws error with status 423 if deadline has passed.
   */
  async function submitPrediction(
    matchId: number,
    homeScore: number,
    awayScore: number
  ): Promise<Prediction> {
    try {
      const response = await apiClient.post('/api/predictions', {
        match_id: matchId,
        home_score: homeScore,
        away_score: awayScore,
      })

      const prediction = response.data

      // Update local cache
      const existingIndex = predictions.value.findIndex((p) => p.match_id === matchId)
      if (existingIndex >= 0) {
        predictions.value[existingIndex] = prediction
      } else {
        predictions.value.push(prediction)
      }

      return prediction
    } catch (error: any) {
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
