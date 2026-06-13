<template>
  <AppLayout>
    <div class="container mx-auto max-w-4xl px-4 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-display-lg font-montserrat font-bold text-on-surface mb-2">
          {{ t('leaderboard.title') }}
        </h1>
        <p class="text-body-lg text-on-surface-variant">
          {{ groupName }}
        </p>
      </div>

      <!-- Loading state -->
      <div v-if="leaderboardStore.loading" class="py-8 text-center">
        <div class="inline-block animate-spin">⏳</div>
        <p class="mt-4 text-body-md text-on-surface-variant">{{ t('leaderboard.loading') }}</p>
      </div>

      <!-- Error state -->
      <div
        v-else-if="leaderboardStore.error === 'not_member'"
        class="bg-error-container rounded-lg p-6 text-center"
      >
        <p class="text-body-md text-on-error-container mb-4">
          {{ t('leaderboard.notMember') }}
        </p>
        <RouterLink to="/dashboard" class="px-6 py-3 rounded-lg font-semibold text-body-md transition-colors bg-primary text-on-primary">
          {{ t('common.backToDashboard') }}
        </RouterLink>
      </div>

      <div v-else-if="leaderboardStore.error" class="bg-error-container rounded-lg p-6 text-center">
        <p class="text-body-md text-on-error-container">
          {{ leaderboardStore.error }}
        </p>
      </div>

      <!-- Main content -->
      <div v-else>
        <!-- Leaderboard Table -->
        <div class="mb-8 bg-white rounded-lg shadow-sm border border-outline-variant p-6">
          <LeaderboardTable :standings="leaderboardStore.sortedStandings" @select-user="handleSelectUser" />
        </div>

        <!-- Friend Recent Results Sheet -->
        <FriendRecentResultsSheet
          :is-open="isRecentResultsOpen"
          :user-name="selectedUser?.name ?? ''"
          :user-picture="selectedUser?.picture ?? null"
          :total-points="selectedUser?.total_points ?? null"
          :history="leaderboardStore.memberRecentHistory"
          :loading="leaderboardStore.memberRecentHistoryLoading"
          :error="leaderboardStore.memberRecentHistoryError"
          @close="handleCloseSheet"
        />

        <!-- Prizes section (if any) -->
        <div
          v-if="leaderboardStore.topThree.length > 0"
          class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
        >
          <div
            v-for="entry in leaderboardStore.topThree"
            :key="entry.user_id"
            class="bg-secondary-container rounded-lg p-6 text-center border-l-4 border-secondary"
          >
            <div class="text-4xl mb-2">{{ prizeIcon(entry.rank) }}</div>
            <p class="text-label-lg font-semibold text-on-secondary-container">
              {{ entry.prize_description || t('leaderboard.rankLabel', { rank: entry.rank }) }}
            </p>
            <p class="text-body-md text-on-secondary-container mt-2">{{ entry.name }}</p>
            <p class="text-headline-md font-bold text-secondary mt-2">{{ entry.total_points }} {{ t('common.pts') }}</p>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex gap-4 justify-center">
          <RouterLink
            :to="`/groups/${groupId}/history`"
            class="px-6 py-3 rounded-lg font-semibold text-body-md transition-colors bg-primary text-on-primary"
          >
            {{ t('leaderboard.viewHistory') }}
          </RouterLink>
          <RouterLink to="/dashboard" class="px-6 py-3 rounded-lg font-semibold text-body-md transition-colors bg-secondary text-on-secondary">
            {{ t('common.backToDashboard') }}
          </RouterLink>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLeaderboardStore } from '@/stores/leaderboard'
import { useGroupsStore } from '@/stores/groups'
import type { LeaderboardEntry } from '@/stores/leaderboard'
import AppLayout from '@/components/AppLayout.vue'
import LeaderboardTable from '@/components/LeaderboardTable.vue'
import FriendRecentResultsSheet from '@/components/FriendRecentResultsSheet.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const leaderboardStore = useLeaderboardStore()
const groupsStore = useGroupsStore()

const groupId = computed(() => route.params.id as string)

const groupName = computed(() => {
  return groupsStore.currentGroup?.name || t('leaderboard.defaultTitle')
})

const selectedUser = ref<LeaderboardEntry | null>(null)
const isRecentResultsOpen = ref(false)

function handleSelectUser(entry: LeaderboardEntry) {
  selectedUser.value = entry
  isRecentResultsOpen.value = true
}

function handleCloseSheet() {
  isRecentResultsOpen.value = false
  selectedUser.value = null
}

watch(isRecentResultsOpen, async (open) => {
  if (open && selectedUser.value && groupId.value) {
    await leaderboardStore.fetchMemberRecentHistory(groupId.value, selectedUser.value.user_id)
  }
})

function prizeIcon(rank: number): string {
  const icons = { 1: '🥇', 2: '🥈', 3: '🥉' }
  return icons[rank as keyof typeof icons] || ''
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

  // Load leaderboard
  await leaderboardStore.fetchLeaderboard(groupId.value)
})
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
