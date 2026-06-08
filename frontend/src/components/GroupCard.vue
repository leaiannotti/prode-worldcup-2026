<template>
  <div class="bg-surface-container-lowest rounded-xl p-4 border border-outline-variant hover:border-primary transition-all">
    <!-- Name + members -->
    <div class="mb-3">
      <h3 class="font-headline-sm text-headline-sm text-primary">{{ group.name }}</h3>
      <p class="text-xs text-on-surface-variant mt-0.5">{{ group.member_count ?? 0 }} miembros</p>
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

    <!-- View Details button -->
    <button
      @click="emit('open-detail', group)"
      class="w-full py-2 px-4 bg-primary text-on-primary rounded-lg font-semibold text-sm hover:opacity-90 transition-all active:scale-95 cursor-pointer"
    >
      Ver detalle
    </button>
  </div>
</template>

<script setup lang="ts">
import type { Group } from '@/stores/groups'

defineProps<{ group: Group }>()

const emit = defineEmits<{
  (e: 'open-detail', group: Group): void
}>()

function rankBadge(rank: number): string {
  if (rank === 1) return 'bg-amber-100 text-amber-800'
  if (rank === 2) return 'bg-slate-100 text-slate-700'
  return 'bg-orange-100 text-orange-800'
}
</script>
