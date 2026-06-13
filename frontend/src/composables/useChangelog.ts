/**
 * Changelog composable — decides whether to show the "What's New" modal
 * and fetches the entries the user hasn't seen yet.
 *
 * Storage contract:
 *   localStorage['prode.lastSeenChangelogVersion'] = "1.1.0"
 *
 * If the key is missing (first-time user or cleared storage), we treat it
 * as "already up to date" so we don't blast new users with a wall of release
 * notes. The very first time a user logs in, the modal stays silent and the
 * key is initialized to the current version on first acknowledgement.
 */
import { ref, readonly, type Ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface ChangelogTranslation {
  title: string
  new: string[]
  fixed: string[]
  improved?: string[]
}

export interface ChangelogEntry {
  version: string
  released_at: string
  translations: {
    es: ChangelogTranslation
    en: ChangelogTranslation
  }
}

interface ChangelogResponse {
  current: string
  entries: ChangelogEntry[]
}

const STORAGE_KEY = 'prode.lastSeenChangelogVersion'

const entries = ref<ChangelogEntry[]>([])
const currentVersion = ref<string | null>(null)
const isOpen = ref(false)
const isLoading = ref(false)
const hasChecked = ref(false)

function getLastSeen(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function setLastSeen(version: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, version)
  } catch {
    // localStorage can throw in private mode or when quota is exceeded.
    // The modal still works — it just won't remember on next boot.
  }
}

/**
 * Check whether to show the modal. Call this once after the user is
 * authenticated (so we don't pop a modal over the login screen).
 *
 * Behavior:
 * - First-time user (no key in localStorage): seed with the current version,
 *   do NOT open the modal. The user will only see changelogs for releases
 *   that ship AFTER their first session.
 * - Returning user with up-to-date version: do nothing.
 * - Returning user behind: fetch entries since their last seen version and
 *   open the modal if any came back.
 */
async function checkForUpdates(): Promise<void> {
  if (hasChecked.value || isLoading.value) return
  isLoading.value = true

  try {
    const lastSeen = getLastSeen()

    if (lastSeen === null) {
      // First-time user — seed the storage to the current version without
      // opening the modal. We still need to know what "current" is, so we
      // hit /api/version (cheap, no entries returned).
      const res = await apiClient.get<{ version: string }>('/api/version')
      currentVersion.value = res.data.version
      setLastSeen(res.data.version)
      return
    }

    // Returning user — ask the backend for anything newer than lastSeen.
    const res = await apiClient.get<ChangelogResponse>(
      `/api/changelog?since=${encodeURIComponent(lastSeen)}`
    )
    currentVersion.value = res.data.current
    entries.value = res.data.entries

    if (res.data.entries.length > 0) {
      isOpen.value = true
    } else {
      // Up to date — nothing to show.
    }
  } catch {
    // Network or backend error — fail silently. The "What's New" modal is
    // not critical functionality; a broken /api/changelog must not block
    // the app from rendering.
  } finally {
    isLoading.value = false
    hasChecked.value = true
  }
}

/**
 * Acknowledge the modal — close it and persist the current version so we
 * don't show the same entries on next login.
 */
function acknowledge(): void {
  isOpen.value = false
  if (currentVersion.value) {
    setLastSeen(currentVersion.value)
  }
  // Clear entries so re-opening (if any future flow allows it) starts fresh.
  entries.value = []
}

export function useChangelog() {
  return {
    isOpen: readonly(isOpen) as Readonly<Ref<boolean>>,
    isLoading: readonly(isLoading) as Readonly<Ref<boolean>>,
    entries: readonly(entries) as Readonly<Ref<ChangelogEntry[]>>,
    currentVersion: readonly(currentVersion) as Readonly<Ref<string | null>>,
    checkForUpdates,
    acknowledge,
  }
}
