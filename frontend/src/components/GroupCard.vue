<template>
  <div class="bg-surface-container-lowest rounded-xl p-4 border border-outline-variant hover:border-primary transition-all">
    <!-- Name + members + rank -->
    <div class="flex items-start justify-between mb-3 gap-2">
      <div class="min-w-0">
        <h3 class="font-headline-sm text-headline-sm text-primary">{{ group.name }}</h3>
        <p class="text-xs text-on-surface-variant mt-0.5">{{ group.member_count ?? 0 }} {{ t('leagueDetail.members') }}</p>
      </div>
      <div v-if="standing" class="flex-shrink-0 flex flex-col items-center bg-primary-container rounded-lg px-3 py-1.5 min-w-[3.5rem]">
        <span class="text-[10px] font-medium text-on-primary-container uppercase tracking-wide leading-none">{{ t('leagues.rank') }}</span>
        <span class="text-xl font-bold text-primary leading-tight tabular-nums">#{{ standing.rank }}</span>
        <span class="text-[10px] text-on-surface-variant leading-none">{{ t('leagues.rankOf', { total: standing.member_count }) }}</span>
      </div>
    </div>

    <!-- Prizes preview -->
    <div v-if="group.prizes && group.prizes.length > 0" class="flex gap-1.5 mb-3 flex-wrap">
      <span
        v-for="prize in group.prizes"
        :key="prize.rank"
        class="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full"
        :class="rankBadge(prize.rank)"
      >
        <span>{{ prize.rank }}°</span>
        <span class="truncate max-w-[80px]">{{ prize.description }}</span>
      </span>
    </div>

    <!-- Points row (if standing available) -->
    <div v-if="standing" class="flex items-center gap-1.5 mb-3">
      <span class="text-xs text-on-surface-variant">{{ t('leagues.myPoints') }}</span>
      <span class="text-sm font-bold text-primary tabular-nums">{{ standing.total_points }} pts</span>
    </div>

    <!-- View Details button -->
    <button
      @click="emit('open-detail', group)"
      class="w-full py-2 px-4 bg-primary text-on-primary rounded-lg font-semibold text-sm hover:opacity-90 transition-all active:scale-95 cursor-pointer"
    >
      {{ t('groupCard.viewDetail') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Group } from '@/stores/groups'
import type { MyStandingItem } from '@/stores/scores'
import { useI18n } from 'vue-i18n'

defineProps<{
  group: Group
  standing?: MyStandingItem | null
}>()

const { t } = useI18n()

const emit = defineEmits<{
  (e: 'open-detail', group: Group): void
}>()

function rankBadge(rank: number): string {
  if (rank === 1) return 'bg-amber-100 text-amber-800'
  if (rank === 2) return 'bg-slate-100 text-slate-700'
  return 'bg-orange-100 text-orange-800'
}
</script>
