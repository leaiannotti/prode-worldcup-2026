/**
 * Groups store — manages prediction groups state and operations.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '@/lib/api'

export interface Prize {
  rank: number
  description: string
}

export interface Group {
  id: string
  name: string
  invite_code: string
  created_at: string
  creator_id?: string
  member_count?: number
  prizes?: Prize[]
}

export interface CreateGroupRequest {
  name: string
  prizes?: Prize[]
}

export interface JoinGroupRequest {
  invite_code: string
}

export const useGroupsStore = defineStore('groups', () => {
  // State
  const groups = ref<Group[]>([])
  const currentGroup = ref<Group | null>(null)

  // Computed
  const groupCount = computed(() => groups.value.length)

  // Actions
  /**
   * Fetch all groups user is member of
   */
  async function fetchGroups(): Promise<void> {
    try {
      const response = await apiClient.get('/api/groups')
      groups.value = response.data
    } catch (error) {
      console.error('Error fetching groups:', error)
      throw error
    }
  }

  /**
   * Fetch a specific group by ID
   */
  async function fetchGroup(id: string): Promise<Group | null> {
    try {
      const response = await apiClient.get(`/api/groups/${id}`)
      currentGroup.value = response.data
      return response.data
    } catch (error) {
      console.error(`Error fetching group ${id}:`, error)
      throw error
    }
  }

  /**
   * Create a new prediction group
   */
  async function createGroup(name: string, prizes?: Prize[]): Promise<Group> {
    try {
      const response = await apiClient.post('/api/groups', { name, prizes })
      const newGroup = response.data
      groups.value.push(newGroup)
      return newGroup
    } catch (error) {
      console.error('Error creating group:', error)
      throw error
    }
  }

  /**
   * Join an existing group using invite code
   */
  async function joinGroup(invite_code: string): Promise<Group> {
    try {
      const response = await apiClient.post('/api/groups/join', { invite_code })
      const joinedGroup = response.data
      groups.value.push(joinedGroup)
      return joinedGroup
    } catch (error) {
      console.error('Error joining group:', error)
      throw error
    }
  }

  /**
   * Set prizes for a group (admin only)
   */
  async function setPrizes(
    id: string,
    prizes: Array<{ rank: number; description: string }>
  ): Promise<void> {
    try {
      await apiClient.post(`/api/groups/${id}/prizes`, { prizes })
      // Update local group
      if (currentGroup.value?.id === id) {
        currentGroup.value.prizes = prizes
      }
      const groupIndex = groups.value.findIndex((g) => g.id === id)
      if (groupIndex >= 0) {
        groups.value[groupIndex].prizes = prizes
      }
    } catch (error) {
      console.error('Error setting prizes:', error)
      throw error
    }
  }

  async function leaveGroup(id: string): Promise<void> {
    await apiClient.post(`/api/groups/${id}/leave`)
    groups.value = groups.value.filter(g => g.id !== id)
  }

  async function deleteGroup(id: string): Promise<void> {
    await apiClient.delete(`/api/groups/${id}`)
    groups.value = groups.value.filter(g => g.id !== id)
  }

  return {
    groups,
    currentGroup,
    groupCount,
    fetchGroups,
    fetchGroup,
    createGroup,
    joinGroup,
    setPrizes,
    leaveGroup,
    deleteGroup,
  }
})
