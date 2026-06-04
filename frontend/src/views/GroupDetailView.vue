<template>
  <AppLayout>
    <div class="px-gutter py-lg max-w-7xl mx-auto space-y-lg">
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-lg">
        <p class="text-on-surface-variant font-body-lg">Loading group...</p>
      </div>

      <!-- Group Detail -->
      <div v-else-if="groupsStore.currentGroup">
        <!-- Header -->
        <section class="space-y-md border-b border-outline-variant pb-lg">
          <div class="flex flex-col md:flex-row justify-between md:items-start gap-md">
            <div>
              <h1 class="font-headline-lg text-headline-lg text-primary mb-xs">
                {{ groupsStore.currentGroup.name }}
              </h1>
              <p class="font-body-lg text-body-lg text-on-surface-variant">
                {{ groupsStore.currentGroup.member_count || 0 }} members
              </p>
            </div>
            <RouterLink
              :to="`/groups/${route.params.id}/leaderboard`"
              class="px-lg py-md bg-secondary text-on-secondary rounded-lg font-bold hover:opacity-90 transition-all"
            >
              View Leaderboard
            </RouterLink>
          </div>

          <!-- Invite Code -->
          <div class="bg-surface-container-low rounded-lg p-md flex items-center justify-between">
            <div>
              <p class="font-label-md text-label-md text-on-surface-variant uppercase mb-xs">Invite Code</p>
              <code class="font-bold text-primary text-lg">{{ groupsStore.currentGroup.invite_code }}</code>
            </div>
            <button
              @click="copyInviteCode"
              class="p-md bg-primary text-on-primary rounded-lg hover:opacity-90 transition-all"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 011 1v1h2V3a3 3 0 00-3-3H9a3 3 0 00-3 3v1H4a3 3 0 00-3 3v2h1V6a2 2 0 012-2h1V3zm9 8a1 1 0 100-2 1 1 0 000 2zm0 2a3 3 0 110-6 3 3 0 010 6zm0 1a4 4 0 100-8 4 4 0 000 8z" />
              </svg>
            </button>
          </div>
        </section>

        <!-- Prizes Section -->
        <section v-if="groupsStore.currentGroup.prizes && groupsStore.currentGroup.prizes.length > 0" class="space-y-md">
          <h2 class="font-headline-md text-headline-md text-primary">Prizes</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-md">
            <div
              v-for="prize in groupsStore.currentGroup.prizes"
              :key="prize.rank"
              :class="`rounded-lg p-md text-center ${prizeClass(prize.rank)}`"
            >
              <p class="font-label-md text-label-md uppercase mb-xs opacity-75">Rank {{ prize.rank }}</p>
              <p class="font-headline-sm text-headline-sm">{{ prize.description }}</p>
            </div>
          </div>
        </section>

        <!-- Navigation Tabs -->
        <section class="border-b border-outline-variant">
          <div class="flex gap-md overflow-x-auto">
            <button
              @click="activeTab = 'members'"
              :class="`px-md py-md font-bold border-b-2 ${activeTab === 'members' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant'}`"
            >
              Members
            </button>
            <button
              @click="activeTab = 'matches'"
              :class="`px-md py-md font-bold border-b-2 ${activeTab === 'matches' ? 'border-primary text-primary' : 'border-transparent text-on-surface-variant'}`"
            >
              Matches
            </button>
          </div>
        </section>

        <!-- Members Tab -->
        <section v-show="activeTab === 'members'" class="space-y-md">
          <h3 class="font-headline-sm text-headline-sm text-primary">Group Members</h3>
          <div class="space-y-sm">
            <div class="text-center text-on-surface-variant py-lg">
              <p class="font-body-lg">Members list coming soon</p>
            </div>
          </div>
        </section>

        <!-- Matches Tab -->
        <section v-show="activeTab === 'matches'" class="space-y-md">
          <h3 class="font-headline-sm text-headline-sm text-primary">Group Matches</h3>
          <div class="text-center text-on-surface-variant py-lg">
            <p class="font-body-lg">Matches list coming soon</p>
          </div>
        </section>
      </div>

      <!-- Not Found -->
      <div v-else class="text-center py-lg">
        <p class="text-on-surface-variant font-body-lg">Group not found</p>
        <RouterLink to="/dashboard" class="text-primary font-bold hover:underline">
          Back to Dashboard
        </RouterLink>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()
const groupsStore = useGroupsStore()

const isLoading = ref(false)
const activeTab = ref<'members' | 'matches'>('members')

onMounted(async () => {
  isLoading.value = true
  try {
    await groupsStore.fetchGroup(route.params.id as string)
  } catch (error) {
    console.error('Error loading group:', error)
  } finally {
    isLoading.value = false
  }
})

function prizeClass(rank: number): string {
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
  if (groupsStore.currentGroup?.invite_code) {
    navigator.clipboard.writeText(groupsStore.currentGroup.invite_code)
  }
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
