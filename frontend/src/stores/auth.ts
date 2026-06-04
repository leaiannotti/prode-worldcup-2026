/**
 * Auth store — manages user authentication state via Pinia.
 * Handles login status, user data, and session persistence.
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiClient } from '@/lib/api';

export interface User {
  id: string;
  email: string;
  name: string;
  picture: string | null;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => user.value !== null);

  // Actions
  /**
   * Fetch current user from /api/auth/me.
   * Returns true if authenticated, false on 401.
   */
  async function fetchMe(): Promise<boolean> {
    try {
      const response = await apiClient.get('/api/auth/me');
      user.value = response.data as User;
      return true;
    } catch (error: any) {
      if (error.response?.status === 401) {
        user.value = null;
        return false;
      }
      throw error;
    }
  }

  /**
   * Logout by calling /api/auth/logout and clearing state.
   */
  async function logout(): Promise<void> {
    try {
      await apiClient.post('/api/auth/logout');
    } finally {
      user.value = null;
    }
  }

  return {
    user,
    isAuthenticated,
    fetchMe,
    logout,
  };
});
