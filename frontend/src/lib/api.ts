import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
  withCredentials: true,
});

export function getMemberRecentHistory(groupId: string, userId: string, limit = 5) {
  return apiClient.get(
    `/api/scores/groups/${groupId}/members/${userId}/recent-history?limit=${limit}`
  );
}
