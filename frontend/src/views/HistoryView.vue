<template>
  <AppLayout>
    <div class="container mx-auto max-w-2xl px-4 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-display-lg font-montserrat font-bold text-on-surface mb-2">
          My Predictions
        </h1>
        <p class="text-body-lg text-on-surface-variant">
          {{ groupName || 'History' }}
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="leaderboardStore.loading" class="py-8 text-center">
        <div class="inline-block animate-spin">⏳</div>
        <p class="mt-4 text-body-md text-on-surface-variant">Loading your predictions...</p>
      </div>

      <!-- Error state -->
      <div
        v-else-if="leaderboardStore.error === 'not_member'"
        class="bg-error-container rounded-lg p-6 text-center"
      >
        <p class="text-body-md text-on-error-container mb-4">
          You're not a member of this group
        </p>
        <RouterLink to="/dashboard" class="btn btn-primary">
          Back to Dashboard
        </RouterLink>
      </div>

      <div v-else-if="leaderboardStore.error" class="bg-error-container rounded-lg p-6 text-center">
        <p class="text-body-md text-on-error-container">
          {{ leaderboardStore.error }}
        </p>
      </div>

      <!-- Main content -->
      <div v-else>
        <!-- Empty state -->
        <div
          v-if="leaderboardStore.history.length === 0"
          class="bg-surface-dim rounded-lg p-8 text-center"
        >
          <p class="text-body-lg text-on-surface-variant">
            No predictions made yet
          </p>
        </div>

        <!-- History list -->
        <div v-else class="space-y-4">
          <div
            v-for="(entry, idx) in leaderboardStore.history"
            :key="`${entry.match.id}-${idx}`"
            class="bg-white rounded-lg border border-outline-variant p-6 hover:shadow-md transition-shadow"
          >
            <!-- Match header -->
            <div class="flex justify-between items-start mb-4">
              <div>
                <p class="text-headline-sm font-bold text-on-surface">
                  {{ entry.match.home_team }} vs {{ entry.match.away_team }}
                </p>
                <p class="text-label-sm text-on-surface-variant mt-1">
                  {{ formatDate(entry.match.kickoff_at) }}
                </p>
              </div>
              <span
                :class="['px-3 py-1 rounded-full text-label-sm font-semibold', statusBadgeClass(entry.match.status)]"
              >
                {{ statusLabel(entry.match.status) }}
              </span>
            </div>

            <!-- Prediction vs Result -->
            <div class="grid grid-cols-2 gap-4 mb-4">
              <!-- Your prediction -->
              <div class="bg-surface-dim rounded-lg p-4">
                <p class="text-label-sm text-on-surface-variant mb-2">Your Prediction</p>
                <p class="text-headline-md font-bold text-on-surface">
                  {{ entry.prediction.home_score }} - {{ entry.prediction.away_score }}
                </p>
              </div>

              <!-- Actual result or pending -->
              <div v-if="entry.actual_result" class="bg-surface-dim rounded-lg p-4">
                <p class="text-label-sm text-on-surface-variant mb-2">Actual Result</p>
                <p class="text-headline-md font-bold text-on-surface">
                  {{ entry.actual_result.home_score }} - {{ entry.actual_result.away_score }}
                </p>
              </div>
              <div v-else class="bg-surface-dim rounded-lg p-4">
                <p class="text-label-sm text-on-surface-variant mb-2">Actual Result</p>
                <p class="text-headline-md font-bold text-on-surface-variant">—</p>
              </div>
            </div>

            <!-- Points earned -->
            <div class="flex items-center justify-between pt-4 border-t border-outline-variant">
              <p class="text-label-md text-on-surface-variant">Points Earned</p>
              <div v-if="entry.points !== undefined && entry.points !== null">
                <span
                  :class="['px-4 py-2 rounded-full font-semibold text-white', pointsBadgeColor(entry.points)]"
                >
                  {{ entry.points }} pts
                </span>
              </div>
              <div v-else>
                <span class="px-4 py-2 rounded-full font-semibold text-on-surface-variant bg-surface-dim">
                  Pending
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex gap-4 justify-center mt-8">
          <RouterLink
            :to="`/groups/${groupId}/leaderboard`"
            class="btn btn-primary"
          >
            View Leaderboard
          </RouterLink>
          <RouterLink to="/dashboard" class="btn btn-secondary">
            Back to Dashboard
          </RouterLink>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLeaderboardStore } from '@/stores/leaderboard'
import { useGroupsStore } from '@/stores/groups'
import { useScoreFormatter } from '@/composables/useScoreFormatter'
import AppLayout from '@/components/AppLayout.vue'

const router = useRouter()
const route = useRoute()
const leaderboardStore = useLeaderboardStore()
const groupsStore = useGroupsStore()
const { pointsBadgeColor } = useScoreFormatter()

const groupId = computed(() => route.params.id as string)

const groupName = computed(() => {
  return groupsStore.currentGroup?.name || 'History'
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    'scheduled': 'Upcoming',
    'in_progress': 'Live',
    'finished': 'Finished'
  }
  return labels[status] || status
}

function statusBadgeClass(status: string): string {
  const classes: Record<string, string> = {
    'scheduled': 'bg-secondary-container text-on-secondary-container',
    'in_progress': 'bg-tertiary-container text-on-tertiary-container animate-pulse',
    'finished': 'bg-surface-variant text-on-surface-variant'
  }
  return classes[status] || 'bg-surface-variant text-on-surface-variant'
}

onMounted(async () => {
  if (!groupId.value) {
    router.push('/dashboard')
    return
  }

  // Load group info if not already loaded
  if (!groupsStore.currentGroup?.id) {
    await groupsStore.fetchGroup(groupId.value)
  }

  // Load history
  await leaderboardStore.fetchHistory(groupId.value)
})
</script>

<style scoped>
.btn {
  @apply px-6 py-3 rounded-lg font-semibold text-body-md transition-colors;
}

.btn-primary {
  @apply bg-primary text-on-primary hover:bg-primary-dark;
}

.btn-secondary {
  @apply bg-secondary text-on-secondary hover:bg-secondary-dark;
}
</style>
