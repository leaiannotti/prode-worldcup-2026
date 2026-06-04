<template>
  <div class="bg-surface-container-lowest rounded-xl p-md border border-outline-variant hover:border-primary hover:shadow-md transition-all">
    <!-- Header: Name and Type -->
    <div class="mb-md">
      <h3 class="font-headline-sm text-headline-sm text-primary mb-xs">{{ group.name }}</h3>
      <p class="font-body-md text-body-md text-on-surface-variant">{{ group.member_count || 0 }} members</p>
    </div>

    <!-- Invite Code -->
    <div class="bg-surface-container-low rounded-lg p-sm mb-md flex items-center justify-between">
      <span class="font-label-sm text-label-sm text-on-surface-variant uppercase">Code:</span>
      <code class="font-bold text-primary">{{ group.invite_code }}</code>
      <button
        @click="copyInviteCode"
        class="text-secondary hover:text-primary transition-colors"
        title="Copy invite code"
      >
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path d="M8 3a1 1 0 011-1h2a1 1 0 011 1v1h2V3a3 3 0 00-3-3H9a3 3 0 00-3 3v1H4a3 3 0 00-3 3v2h1V6a2 2 0 012-2h1V3zm9 8a1 1 0 100-2 1 1 0 000 2zm0 2a3 3 0 110-6 3 3 0 010 6zm0 1a4 4 0 100-8 4 4 0 000 8z" />
        </svg>
      </button>
    </div>

    <!-- Prizes Section -->
    <div v-if="group.prizes && group.prizes.length > 0" class="space-y-xs mb-md">
      <p class="font-label-md text-label-md text-on-surface-variant uppercase">Prizes</p>
      <div class="flex flex-col gap-xs">
        <div
          v-for="prize in group.prizes"
          :key="prize.rank"
          class="flex items-center justify-between bg-surface-container-low p-xs rounded-lg"
        >
          <div class="flex items-center gap-sm">
            <span class="w-6 h-6 flex items-center justify-center font-bold text-xs rounded-full" :class="prizeColor(prize.rank)">
              {{ prize.rank }}
            </span>
            <span class="font-body-md text-body-md text-on-surface">{{ prize.description }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Button -->
    <button
      @click="navigateToGroup"
      class="w-full py-sm px-md bg-primary text-on-primary rounded-lg font-bold hover:opacity-90 transition-all active:scale-95"
    >
      View Details
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Group } from '@/stores/groups'

interface Props {
  group: Group
}

defineProps<Props>()

const router = useRouter()

function navigateToGroup() {
  router.push(`/groups/${props.group.id}`)
}

function prizeColor(rank: number): string {
  switch (rank) {
    case 1:
      return 'bg-secondary text-on-secondary'
    case 2:
      return 'bg-outline text-on-surface'
    case 3:
      return 'bg-surface-variant text-on-surface'
    default:
      return 'bg-surface-container text-on-surface-variant'
  }
}

function copyInviteCode() {
  navigator.clipboard.writeText(props.group.invite_code)
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
