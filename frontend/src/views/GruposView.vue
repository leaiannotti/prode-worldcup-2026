<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-3xl mx-auto space-y-8">

      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 class="font-headline-lg text-headline-lg text-primary">{{ t('leagues.title') }}</h1>
          <p class="font-body-md text-on-surface-variant mt-1">
            {{ t('leagues.subtitle') }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="showCreate = true"
            class="px-4 py-2.5 bg-primary text-on-primary rounded-xl font-semibold text-sm hover:opacity-90 transition-all active:scale-95 whitespace-nowrap"
          >
            {{ t('leagues.create') }}
          </button>
          <button
            @click="showJoin = true"
            class="px-4 py-2.5 border border-outline-variant text-on-surface rounded-xl font-semibold text-sm hover:bg-surface-container transition-all active:scale-95 whitespace-nowrap"
          >
            {{ t('leagues.join') }}
          </button>
        </div>
      </div>

      <!-- No groups -->
      <div v-if="groupsStore.groups.length === 0" class="text-center py-16">
        <p class="font-body-md text-on-surface-variant">{{ t('leagues.noLeagues') }}</p>
      </div>

      <template v-else>
        <!-- Posiciones -->
        <section class="space-y-4">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <h2 class="font-headline-md text-headline-md text-on-surface">{{ t('leagues.standings') }}</h2>

            <!-- Group selector -->
            <div class="relative">
              <select
                v-model="selectedGroupId"
                @change="onGroupChange"
                class="appearance-none w-full sm:w-56 px-4 py-2.5 pr-10 bg-surface-container-low border border-outline-variant rounded-xl text-sm font-medium text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none cursor-pointer"
              >
                <option v-for="g in groupsStore.groups" :key="g.id" :value="g.id">
                  {{ g.name }}
                </option>
              </select>
              <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-on-surface-variant pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="leaderboardStore.loading" class="space-y-3">
            <div v-for="i in 5" :key="i" class="h-14 bg-surface-container animate-pulse rounded-xl"></div>
          </div>

          <!-- Error -->
          <div v-else-if="leaderboardStore.error" class="text-center py-8 text-error font-body-md">
            {{ t('leagues.errorStandings') }}
          </div>

          <!-- Table -->
          <div v-else-if="leaderboardStore.sortedStandings.length > 0" class="bg-surface-container-lowest rounded-xl border border-outline-variant overflow-hidden">

            <!-- Top 3 podium -->
            <div v-if="leaderboardStore.topThree.length >= 2" class="grid grid-cols-3 divide-x divide-outline-variant border-b border-outline-variant">
              <div
                v-for="entry in leaderboardStore.topThree"
                :key="entry.user_id"
                class="flex flex-col items-center py-4 px-3 gap-2"
              >
                <div class="relative">
                  <img
                    v-if="entry.picture"
                    :src="entry.picture"
                    :alt="entry.name"
                    class="w-10 h-10 rounded-full object-cover border-2"
                    :class="medalBorder(entry.rank)"
                  />
                  <div v-else class="w-10 h-10 rounded-full flex items-center justify-center border-2 text-xs font-bold text-white"
                    :class="medalBg(entry.rank)"
                  >
                    {{ initials(entry.name) }}
                  </div>
                  <span class="absolute -bottom-1 -right-1 text-xs leading-none">{{ medalEmoji(entry.rank) }}</span>
                </div>
                <p class="text-xs font-semibold text-on-surface text-center truncate w-full">{{ entry.name }}</p>
                <p class="text-sm font-bold tabular-nums" :class="medalText(entry.rank)">{{ entry.total_points }} pts</p>
              </div>
            </div>

            <!-- Full standings list -->
            <div class="divide-y divide-outline-variant">
              <div
                v-for="entry in leaderboardStore.sortedStandings"
                :key="entry.user_id"
                class="flex items-center gap-3 px-4 py-3"
                :class="entry.rank <= 3 ? 'bg-surface-container/40' : ''"
              >
                <div
                  class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                  :class="rankStyle(entry.rank)"
                >
                  {{ entry.rank }}
                </div>
                <img
                  v-if="entry.picture"
                  :src="entry.picture"
                  :alt="entry.name"
                  class="w-8 h-8 rounded-full object-cover flex-shrink-0"
                />
                <div v-else class="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <span class="text-on-primary text-xs font-bold">{{ initials(entry.name) }}</span>
                </div>
                <span class="flex-1 font-body-md text-on-surface font-medium truncate">{{ entry.name }}</span>
                <span
                  v-if="entry.prize_description && entry.rank <= 3"
                  class="hidden sm:inline text-xs text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full"
                >
                  {{ entry.prize_description }}
                </span>
                <span class="flex-shrink-0 font-bold tabular-nums text-sm text-primary">
                  {{ entry.total_points }} pts
                </span>
              </div>
            </div>
          </div>

          <!-- Empty standings -->
          <div v-else class="text-center py-10 text-on-surface-variant">
            <p class="font-body-md">{{ t('leagues.noStandings') }}</p>
          </div>
        </section>

        <!-- Divider -->
        <div class="border-t border-outline-variant"></div>

        <!-- Mis Ligas -->
        <section class="space-y-3">
          <h2 class="font-headline-md text-headline-md text-on-surface">{{ t('leagues.myLeagues') }}</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <GroupCard
              v-for="group in groupsStore.groups"
              :key="group.id"
              :group="group"
              :standing="getStanding(group.id)"
              @open-detail="detailGroup = $event"
            />
          </div>
        </section>
      </template>
    </div>

    <!-- Group Dialogs -->
    <GroupDialogs
      :show-create="showCreate"
      :show-join="showJoin"
      @close-create="showCreate = false"
      @close-join="showJoin = false"
      @created="onGroupCreatedOrJoined"
      @joined="onGroupCreatedOrJoined"
    />

    <!-- League Detail Modal -->
    <LeagueDetailModal
      :is-open="!!detailGroup"
      :group="detailGroup"
      @close="detailGroup = null"
      @left="onGroupCreatedOrJoined"
      @deleted="onGroupCreatedOrJoined"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useGroupsStore } from '@/stores/groups'
import { useLeaderboardStore } from '@/stores/leaderboard'
import { useScoresStore } from '@/stores/scores'
import AppLayout from '@/components/AppLayout.vue'
import GroupCard from '@/components/GroupCard.vue'
import GroupDialogs from '@/components/GroupDialogs.vue'
import LeagueDetailModal from '@/components/LeagueDetailModal.vue'
import type { Group } from '@/stores/groups'

const { t } = useI18n()
const route = useRoute()
const groupsStore = useGroupsStore()
const leaderboardStore = useLeaderboardStore()
const scoresStore = useScoresStore()

const selectedGroupId = ref<string>('')
const showCreate = ref(false)
const showJoin = ref(false)
const detailGroup = ref<Group | null>(null)

onMounted(async () => {
  if (groupsStore.groups.length === 0) {
    await groupsStore.fetchGroups()
  }
  await scoresStore.fetchMyStanding()
  if (groupsStore.groups.length > 0) {
    const fromQuery = route.query.group as string | undefined
    const valid = fromQuery && groupsStore.groups.some(g => g.id === fromQuery)
    selectedGroupId.value = valid ? fromQuery : groupsStore.groups[0].id
    await leaderboardStore.fetchLeaderboard(selectedGroupId.value)
  }
})

function getStanding(groupId: string) {
  return scoresStore.myStanding.find(s => s.group_id === groupId) ?? null
}

async function onGroupChange() {
  if (selectedGroupId.value) {
    await leaderboardStore.fetchLeaderboard(selectedGroupId.value)
  }
}

async function onGroupCreatedOrJoined() {
  await groupsStore.fetchGroups()
  if (groupsStore.groups.length > 0 && !selectedGroupId.value) {
    selectedGroupId.value = groupsStore.groups[0].id
    await leaderboardStore.fetchLeaderboard(selectedGroupId.value)
  }
}

function initials(name: string): string {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

function medalEmoji(rank: number): string {
  return rank === 1 ? '🥇' : rank === 2 ? '🥈' : '🥉'
}

function medalBorder(rank: number): string {
  if (rank === 1) return 'border-amber-400'
  if (rank === 2) return 'border-slate-400'
  return 'border-orange-300'
}

function medalBg(rank: number): string {
  if (rank === 1) return 'bg-amber-400 border-amber-400'
  if (rank === 2) return 'bg-slate-400 border-slate-400'
  return 'bg-orange-300 border-orange-300'
}

function medalText(rank: number): string {
  if (rank === 1) return 'text-amber-600'
  if (rank === 2) return 'text-slate-500'
  return 'text-orange-500'
}

function rankStyle(rank: number): string {
  if (rank === 1) return 'bg-amber-400 text-amber-950'
  if (rank === 2) return 'bg-slate-300 text-slate-800'
  if (rank === 3) return 'bg-orange-300 text-orange-900'
  return 'bg-surface-container text-on-surface-variant'
}
</script>
