/**
 * Matches store — manages matches and fixtures state.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface Team {
  id: number
  code: string
  name: string
  flag_url: string | null
}

export interface Match {
  id: number
  home_team: Team
  away_team: Team
  group: { id: number; name: string }
  kickoff_at: string
  prediction_deadline_at: string
  status: 'scheduled' | 'in_progress' | 'finished'
  home_score: number | null
  away_score: number | null
}

export interface MatchFilters {
  group?: string
  date?: string
  status?: 'upcoming' | 'scheduled' | 'in_progress' | 'finished'
  limit?: number
}

export const useMatchesStore = defineStore('matches', () => {
  // State
  const matches = ref<Match[]>([])
  const currentMatch = ref<Match | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  /**
   * Fetch matches with optional filters
   */
  async function fetchMatches(filters?: MatchFilters): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      if (filters?.group) params.append('group', filters.group)
      if (filters?.date) params.append('date', filters.date)
      if (filters?.status) params.append('status', filters.status)
      if (filters?.limit) params.append('limit', String(filters.limit))

      const queryString = params.toString()
      const url = queryString ? `/api/matches?${queryString}` : '/api/matches'
      const response = await apiClient.get(url)
      matches.value = response.data
    } catch (err) {
      error.value = 'Error al cargar partidos'
      console.error('Error fetching matches:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a specific match by ID
   */
  async function fetchMatch(id: number): Promise<Match | null> {
    try {
      const response = await apiClient.get(`/api/matches/${id}`)
      currentMatch.value = response.data
      return response.data
    } catch (error) {
      console.error(`Error fetching match ${id}:`, error)
      throw error
    }
  }

  return {
    matches,
    currentMatch,
    isLoading,
    error,
    fetchMatches,
    fetchMatch,
  }
})
