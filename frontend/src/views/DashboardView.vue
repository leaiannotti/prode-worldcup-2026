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
        <MyStandingWidget @create-league="showCreate = true" @join-league="showJoin = true" />
      </div>

      <!-- Recent Matches -->
      <RecentMatchesWidget />

      <!-- Activity Feed -->
      <ActivityFeedWidget />


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
