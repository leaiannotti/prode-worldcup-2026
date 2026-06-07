/**
 * Leaderboard and history store for predictions
 * Task 4.3: Store actions for fetchLeaderboard, fetchHistory
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient as api } from '@/lib/api'

export interface LeaderboardEntry {
  rank: number
  user_id: string
  name: string
  picture?: string
  total_points: number
  prize_description?: string
}

export interface MatchRef {
  id: number
  home_team: string
  away_team: string
  kickoff_at: string
  status: string
}

export interface PredictionRef {
  home_score: number
  away_score: number
}

export interface ActualResultRef {
  home_score: number
  away_score: number
}

export interface HistoryEntry {
  match: MatchRef
  prediction: PredictionRef
  actual_result?: ActualResultRef
  points?: number
}

export const useLeaderboardStore = defineStore('leaderboard', () => {
  const standings = ref<LeaderboardEntry[]>([])
  const history = ref<HistoryEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const sortedStandings = computed(() => {
    return [...standings.value].sort((a, b) => {
      if (a.rank !== b.rank) {
        return a.rank - b.rank
      }
      return b.total_points - a.total_points
    })
  })

  const topThree = computed(() => {
    return sortedStandings.value.slice(0, 3)
  })

  async function fetchLeaderboard(groupId: string) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/scores/leaderboard?group_id=${groupId}`)
      standings.value = response.data.standings || []
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch leaderboard'
      if (err.response?.status === 403) {
        error.value = 'not_member'
      }
      standings.value = []
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(groupId: string) {
    loading.value = true
    error.value = null
    try {
      const response = await api.get(`/scores/history?group_id=${groupId}`)
      history.value = response.data.history || []
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch history'
      if (err.response?.status === 403) {
        error.value = 'not_member'
      }
      history.value = []
    } finally {
      loading.value = false
    }
  }

  return {
    standings,
    history,
    loading,
    error,
    sortedStandings,
    topThree,
    fetchLeaderboard,
    fetchHistory
  }
})
