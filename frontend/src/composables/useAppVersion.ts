/**
 * App version composable — fetches /api/version once at app boot and exposes
 * the running version as a reactive ref.
 *
 * Why a composable and not a Pinia store: the version is read in exactly two
 * places (the avatar dropdown and the "What's New" modal logic), it does not
 * mutate after boot, and it has no cross-component coordination. A composable
 * with module-level state is the cheapest thing that works.
 */
import { ref, readonly, type Ref } from 'vue'
import { apiClient } from '@/lib/api'

// Module-level singleton state. All callers share the same ref.
const version = ref<string | null>(null)
const isLoading = ref(false)
const hasFetched = ref(false)

async function fetchVersion(): Promise<void> {
  // Idempotent: never refetch in the same session. The version cannot change
  // until the user reloads the page anyway.
  if (hasFetched.value || isLoading.value) return
  isLoading.value = true
  try {
    const res = await apiClient.get<{ version: string }>('/api/version')
    version.value = res.data.version
  } catch {
    // Swallow errors — a missing version badge is not worth surfacing.
    // The modal logic checks for `version.value` before doing anything.
    version.value = null
  } finally {
    isLoading.value = false
    hasFetched.value = true
  }
}

export function useAppVersion(): {
  version: Readonly<Ref<string | null>>
  isLoading: Readonly<Ref<boolean>>
  fetchVersion: () => Promise<void>
} {
  return {
    version: readonly(version),
    isLoading: readonly(isLoading),
    fetchVersion,
  }
}
