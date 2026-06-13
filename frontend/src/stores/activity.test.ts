/**
 * Frontend activity store tests.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useActivityStore } from './activity';

// Mock API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

describe('useActivityStore — fetchActivity', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it('preserves default behavior with no args', async () => {
    const store = useActivityStore();
    const { apiClient } = await import('@/lib/api');

    const mockEvents = [
      { id: '1', event_type: 'group_joined', group_id: null, match_id: null, payload: {}, occurred_at: '2024-01-01' },
    ];
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: mockEvents },
    });

    await store.fetchActivity();

    expect(apiClient.get).toHaveBeenCalledTimes(1);
    expect(apiClient.get).toHaveBeenCalledWith('/api/activity?limit=10');
    expect(store.events).toEqual(mockEvents);
  });

  it('adds group_id query param when provided', async () => {
    const store = useActivityStore();
    const { apiClient } = await import('@/lib/api');

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: [] },
    });

    await store.fetchActivity({ groupId: 5 });

    expect(apiClient.get).toHaveBeenCalledTimes(1);
    expect(apiClient.get).toHaveBeenCalledWith('/api/activity?limit=10&group_id=5');
  });

  it('adds all query params when provided', async () => {
    const store = useActivityStore();
    const { apiClient } = await import('@/lib/api');

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: [] },
    });

    await store.fetchActivity({ groupId: 5, eventType: 'prize_changed', limit: 10 });

    expect(apiClient.get).toHaveBeenCalledTimes(1);
    expect(apiClient.get).toHaveBeenCalledWith('/api/activity?limit=10&group_id=5&event_type=prize_changed');
  });

  it('stores result correctly', async () => {
    const store = useActivityStore();
    const { apiClient } = await import('@/lib/api');

    const mockEvents = [
      { id: '1', event_type: 'prize_changed', group_id: '5', match_id: null, payload: { rank: 1 }, occurred_at: '2024-01-01' },
    ];
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: mockEvents },
    });

    await store.fetchActivity({ groupId: 5, eventType: 'prize_changed', limit: 10 });

    expect(store.events).toEqual(mockEvents);
  });
});
