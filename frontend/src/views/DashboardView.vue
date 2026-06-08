<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-7xl mx-auto space-y-6">

      <!-- Hero Section -->
      <section>
        <h1 class="font-headline-lg text-headline-lg text-primary mb-1">Dashboard</h1>
        <p class="font-body-lg text-body-lg text-on-surface-variant">
          Bienvenido, {{ authStore.user?.name }}
        </p>
      </section>

      <!-- Widgets Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UpcomingMatchesWidget @open-prediction="openPrediction" />
        <MyStandingWidget />
      </div>

      <!-- Recent Matches -->
      <RecentMatchesWidget />

      <!-- Activity Feed -->
      <ActivityFeedWidget />

      <!-- Empty State -->
      <section v-if="groupsStore.groups.length === 0" class="flex flex-col items-center justify-center text-center py-16 px-4">
        <div class="w-20 h-20 mb-6 rounded-full bg-primary-fixed flex items-center justify-center">
          <svg class="w-10 h-10 text-on-primary-fixed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
          </svg>
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-2">Sin Ligas</h3>
        <p class="font-body-md text-body-md text-on-surface-variant mb-8 max-w-sm">
          Creá una liga nueva o unite a una existente para empezar.
        </p>
        <div class="flex gap-3">
          <button
            @click="showCreate = true"
            class="bg-primary text-on-primary px-8 py-3.5 rounded-xl font-semibold text-sm hover:opacity-90 transition-all active:scale-95 shadow-md"
          >
            Crear liga
          </button>
          <button
            @click="showJoin = true"
            class="bg-surface-container text-on-surface px-8 py-3.5 rounded-xl font-semibold text-sm hover:bg-surface-container-high transition-all active:scale-95 border border-outline-variant"
          >
            Unirse con código
          </button>
        </div>
      </section>
    </div>

    <!-- Prediction Modal -->
    <PredictionModal
      :is-open="isPredictionModalOpen"
      :match="selectedMatch"
      @close="closePrediction"
      @saved="onPredictionSaved"
    />

    <!-- Group Dialogs -->
    <GroupDialogs
      :show-create="showCreate"
      :show-join="showJoin"
      @close-create="showCreate = false"
      @close-join="showJoin = false"
      @created="groupsStore.fetchGroups()"
      @joined="groupsStore.fetchGroups()"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'
import { useMatchesStore } from '@/stores/matches'
import { usePredictionsStore } from '@/stores/predictions'
import { useActivityStore } from '@/stores/activity'
import AppLayout from '@/components/AppLayout.vue'
import UpcomingMatchesWidget from '@/components/UpcomingMatchesWidget.vue'
import MyStandingWidget from '@/components/MyStandingWidget.vue'
import ActivityFeedWidget from '@/components/ActivityFeedWidget.vue'
import RecentMatchesWidget from '@/components/RecentMatchesWidget.vue'
import PredictionModal from '@/components/PredictionModal.vue'
import GroupDialogs from '@/components/GroupDialogs.vue'

const authStore = useAuthStore()
const groupsStore = useGroupsStore()
const matchesStore = useMatchesStore()
const predictionsStore = usePredictionsStore()
const activityStore = useActivityStore()

const showCreate = ref(false)
const showJoin = ref(false)
const isPredictionModalOpen = ref(false)
const selectedMatch = ref<any>(null)

function openPrediction(matchId: number) {
  const match = matchesStore.matches.find(m => m.id === matchId)
  if (match) {
    selectedMatch.value = match
    isPredictionModalOpen.value = true
  }
}

function closePrediction() {
  isPredictionModalOpen.value = false
  selectedMatch.value = null
}

function onPredictionSaved() {
  predictionsStore.fetchMyPredictions()
  activityStore.fetchActivity(10)
}

onMounted(async () => {
  try {
    await groupsStore.fetchGroups()
    await predictionsStore.fetchMyPredictions()
  } catch (error) {
    console.error('Error loading dashboard:', error)
  }
})
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
