/**
 * Frontend groups store tests.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useGroupsStore } from './groups';

// Mock API client
vi.mock('@/lib/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

describe('useGroupsStore — patchPrizes', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('calls PATCH /api/groups/:id/prizes with bulk body', async () => {
    const store = useGroupsStore();
    const { apiClient } = await import('@/lib/api');

    vi.mocked(apiClient.patch).mockResolvedValueOnce({
      data: { changed: [{ rank: 1, previous: 'Pizza', new: 'Asado' }] },
    });

    await store.patchPrizes('group-1', { first: 'Asado' });

    expect(apiClient.patch).toHaveBeenCalledTimes(1);
    expect(apiClient.patch).toHaveBeenCalledWith(
      '/api/groups/group-1/prizes',
      { first: 'Asado' }
    );
  });

  it('updates currentGroup prizes on success', async () => {
    const store = useGroupsStore();
    const { apiClient } = await import('@/lib/api');

    store.currentGroup = {
      id: 'group-1',
      name: 'Test Group',
      invite_code: 'ABC123',
      created_at: '2024-01-01',
      prizes: [
        { rank: 1, description: 'Pizza' },
        { rank: 2, description: 'Cerveza' },
      ],
    };

    vi.mocked(apiClient.patch).mockResolvedValueOnce({
      data: { changed: [{ rank: 1, previous: 'Pizza', new: 'Asado' }] },
    });

    await store.patchPrizes('group-1', { first: 'Asado' });

    expect(store.currentGroup.prizes).toEqual([
      { rank: 1, description: 'Asado' },
      { rank: 2, description: 'Cerveza' },
    ]);
  });

  it('updates groups array prize on success', async () => {
    const store = useGroupsStore();
    const { apiClient } = await import('@/lib/api');

    store.groups = [
      {
        id: 'group-1',
        name: 'Test Group',
        invite_code: 'ABC123',
        created_at: '2024-01-01',
        prizes: [{ rank: 1, description: 'Pizza' }],
      },
    ];

    vi.mocked(apiClient.patch).mockResolvedValueOnce({
      data: { changed: [{ rank: 1, previous: 'Pizza', new: 'Asado' }] },
    });

    await store.patchPrizes('group-1', { first: 'Asado' });

    expect(store.groups[0].prizes).toEqual([
      { rank: 1, description: 'Asado' },
    ]);
  });

  it('throws on 403 forbidden', async () => {
    const store = useGroupsStore();
    const { apiClient } = await import('@/lib/api');

    const error = new Error('Forbidden');
    (error as any).response = { status: 403, data: { error: 'forbidden' } };
    vi.mocked(apiClient.patch).mockRejectedValueOnce(error);

    await expect(store.patchPrizes('group-1', { first: 'Asado' })).rejects.toThrow('Forbidden');
  });

  it('throws on 422 validation error', async () => {
    const store = useGroupsStore();
    const { apiClient } = await import('@/lib/api');

    const error = new Error('Unprocessable Entity');
    (error as any).response = { status: 422, data: { error: 'invalid_request', details: 'too long' } };
    vi.mocked(apiClient.patch).mockRejectedValueOnce(error);

    await expect(store.patchPrizes('group-1', { first: 'x'.repeat(300) })).rejects.toThrow('Unprocessable Entity');
  });

  it('throws on generic error', async () => {
    const store = useGroupsStore();
    const { apiClient } = await import('@/lib/api');

    const error = new Error('Network Error');
    vi.mocked(apiClient.patch).mockRejectedValueOnce(error);

    await expect(store.patchPrizes('group-1', { first: 'Asado' })).rejects.toThrow('Network Error');
  });
});
