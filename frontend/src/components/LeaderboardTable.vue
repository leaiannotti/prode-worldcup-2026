<template>
  <div class="w-full overflow-x-auto">
    <table class="w-full border-collapse min-w-[320px]">
      <thead>
        <tr class="border-b border-outline-variant">
          <th class="text-left py-3 px-4 text-label-md font-semibold">Rank</th>
          <th class="text-left py-3 px-4 text-label-md font-semibold">Player</th>
          <th class="text-right py-3 px-4 text-label-md font-semibold">Points</th>
          <th class="text-center py-3 px-4 text-label-md font-semibold">Prize</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(entry, idx) in standings"
          :key="entry.user_id"
          :class="[
            'border-b border-outline-variant hover:bg-surface-dim transition-colors',
            idx % 2 === 0 ? 'bg-white' : 'bg-tertiary-container'
          ]"
          :style="entry.rank <= 3 ? 'border-left: 4px solid #236391' : ''"
        >
          <!-- Rank -->
          <td class="py-4 px-4">
            <span class="font-montserrat font-bold text-2xl" :class="{
              'text-secondary': entry.rank <= 3,
              'text-on-surface': entry.rank > 3
            }">
              {{ entry.rank }}
            </span>
          </td>

          <!-- Player -->
          <td class="py-4 px-4">
            <div class="flex items-center gap-3">
              <img
                v-if="entry.picture"
                :src="entry.picture"
                :alt="entry.name"
                class="w-10 h-10 rounded-full object-cover"
              />
              <div v-else class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                <span class="text-white text-xs font-bold">{{ initials(entry.name) }}</span>
              </div>
              <span class="font-body-md">{{ entry.name }}</span>
            </div>
          </td>

          <!-- Total Points -->
          <td class="py-4 px-4 text-right">
            <span class="font-montserrat font-bold text-lg">{{ entry.total_points }}</span>
          </td>

          <!-- Prize Badge -->
          <td class="py-4 px-4 text-center">
            <span
              v-if="entry.prize_description && entry.rank <= 3"
              class="inline-block px-3 py-1 rounded-full text-sm font-semibold bg-secondary text-on-secondary"
            >
              {{ prizeIcon(entry.rank) }} {{ entry.prize_description }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Empty state -->
    <div v-if="standings.length === 0" class="text-center py-8 text-on-surface-variant">
      <p class="text-body-md">No standings available yet</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LeaderboardEntry } from '@/stores/leaderboard'

interface Props {
  standings: LeaderboardEntry[]
}

defineProps<Props>()

function initials(name: string): string {
  return name
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

function prizeIcon(rank: number): string {
  switch (rank) {
    case 1:
      return '🥇'
    case 2:
      return '🥈'
    case 3:
      return '🥉'
    default:
      return ''
  }
}
</script>

<style scoped>
table {
  table-layout: auto;
}

thead tr {
  background-color: rgba(0, 19, 77, 0.02);
}
</style>
