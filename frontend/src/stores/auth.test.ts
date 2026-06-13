/**
 * Frontend auth store tests.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from './auth';

// Mock API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('initializes with isAuthenticated = false', () => {
    const store = useAuthStore();
    expect(store.isAuthenticated).toBe(false);
    expect(store.user).toBeNull();
  });

  it('fetchMe sets user and marks as authenticated', async () => {
    const store = useAuthStore();
    const { apiClient } = await import('@/lib/api');

    const mockUser = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      picture: 'https://example.com/pic.jpg',
    };

    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockUser });

    await store.fetchMe();

    expect(store.user).toEqual(mockUser);
    expect(store.isAuthenticated).toBe(true);
  });

  it('fetchMe returns false and clears state on 401', async () => {
    const store = useAuthStore();
    const { apiClient } = await import('@/lib/api');

    vi.mocked(apiClient.get).mockRejectedValueOnce({
      response: { status: 401 },
    });

    const result = await store.fetchMe();

    expect(result).toBe(false);
    expect(store.isAuthenticated).toBe(false);
    expect(store.user).toBeNull();
  });

  it('logout clears user and marks as unauthenticated', async () => {
    const store = useAuthStore();
    const { apiClient } = await import('@/lib/api');

    // Set initial state (isAuthenticated is a computed getter derived from user)
    store.user = {
      id: 'user-123',
      email: 'test@example.com',
      name: 'Test User',
      picture: null,
    };
    expect(store.isAuthenticated).toBe(true);

    vi.mocked(apiClient.post).mockResolvedValueOnce({ status: 200 });

    await store.logout();

    expect(store.isAuthenticated).toBe(false);
    expect(store.user).toBeNull();
  });
});
