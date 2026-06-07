<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-7xl mx-auto space-y-6">
      <!-- Hero Section -->
      <section class="space-y-4">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 class="font-headline-lg text-headline-lg text-primary mb-1">Dashboard</h1>
            <p class="font-body-lg text-body-lg text-on-surface-variant">
              Bienvenido, {{ authStore.user?.name }}! Gestiona tus grupos y seguí tu rendimiento.
            </p>
          </div>
          <div class="flex gap-2">
            <button
              @click="showCreateGroupDialog = true"
              class="flex-1 md:flex-none bg-primary text-on-primary px-6 py-4 rounded-lg font-bold hover:opacity-90 transition-all active:scale-95"
            >
              Crear Grupo
            </button>
            <button
              @click="showJoinGroupDialog = true"
              class="flex-1 md:flex-none bg-secondary text-on-secondary px-6 py-4 rounded-lg font-bold hover:opacity-90 transition-all active:scale-95"
            >
              Unirse a Grupo
            </button>
          </div>
        </div>
      </section>

      <!-- Widgets Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <UpcomingMatchesWidget @open-distribution="openDistribution" />
        <MyStandingWidget />
      </div>

      <!-- Activity Feed -->
      <ActivityFeedWidget />

      <!-- Groups Grid -->
      <section v-if="groupsStore.groups.length > 0" class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="font-headline-md text-headline-md text-primary">Mis Grupos</h2>
          <span class="font-label-md text-label-md bg-surface-container px-2 py-1 rounded-full text-on-surface-variant">
            {{ groupsStore.groups.length }} grupo(s)
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <GroupCard v-for="group in groupsStore.groups" :key="group.id" :group="group" />
        </div>
      </section>

      <!-- Empty State -->
      <section v-else class="fixed inset-0 pt-16 flex flex-col items-center justify-center text-center">
        <div class="w-20 h-20 mb-6 rounded-full bg-primary-fixed flex items-center justify-center">
          <svg class="w-10 h-10 text-on-primary-fixed" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
          </svg>
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-2">Sin Grupos</h3>
        <p class="font-body-md text-body-md text-on-surface-variant mb-8 max-w-sm">
          Creá un grupo nuevo o unite a uno existente para empezar.
        </p>
        <button
          @click="showCreateGroupDialog = true"
          class="bg-primary text-on-primary text-base leading-6 px-8 py-3.5 rounded-xl font-semibold hover:opacity-90 transition-all active:scale-95 shadow-md"
        >
          Crear Tu Primer Grupo
        </button>
      </section>

      <!-- Create Group Dialog -->
      <div v-if="showCreateGroupDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-surface rounded-xl p-6 max-w-md w-full space-y-4">
          <h3 class="font-headline-sm text-headline-sm text-primary">Crear Grupo</h3>
          <input
            v-model="newGroupName"
            type="text"
            placeholder="Nombre del grupo..."
            class="w-full px-4 py-2 border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none"
          />
          <div class="flex gap-2">
            <button
              @click="showCreateGroupDialog = false"
              class="flex-1 px-4 py-2 border border-outline-variant rounded-lg font-bold hover:bg-surface-container transition-all"
            >
              Cancelar
            </button>
            <button
              @click="handleCreateGroup"
              :disabled="isCreatingGroup || !newGroupName.trim()"
              class="flex-1 px-4 py-2 bg-primary text-on-primary rounded-lg font-bold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {{ isCreatingGroup ? 'Creando...' : 'Crear' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Join Group Dialog -->
      <div v-if="showJoinGroupDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div class="bg-surface rounded-xl p-6 max-w-md w-full space-y-4">
          <h3 class="font-headline-sm text-headline-sm text-primary">Unirse a Grupo</h3>
          <input
            v-model="inviteCode"
            type="text"
            placeholder="Código de invitación..."
            class="w-full px-4 py-2 border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none uppercase"
          />
          <div class="flex gap-2">
            <button
              @click="showJoinGroupDialog = false"
              class="flex-1 px-4 py-2 border border-outline-variant rounded-lg font-bold hover:bg-surface-container transition-all"
            >
              Cancelar
            </button>
            <button
              @click="handleJoinGroup"
              :disabled="isJoiningGroup || !inviteCode.trim()"
              class="flex-1 px-4 py-2 bg-secondary text-on-secondary rounded-lg font-bold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {{ isJoiningGroup ? 'Uniendo...' : 'Unirse' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Match Distribution Modal -->
    <MatchDistributionModal
      :is-open="isDistributionModalOpen"
      :match-id="selectedMatchId"
      :match="selectedMatch"
      @close="closeDistribution"
    />
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'
import { useMatchesStore } from '@/stores/matches'
import AppLayout from '@/components/AppLayout.vue'
import GroupCard from '@/components/GroupCard.vue'
import UpcomingMatchesWidget from '@/components/UpcomingMatchesWidget.vue'
import MyStandingWidget from '@/components/MyStandingWidget.vue'
import ActivityFeedWidget from '@/components/ActivityFeedWidget.vue'
import MatchDistributionModal from '@/components/MatchDistributionModal.vue'

const authStore = useAuthStore()
const groupsStore = useGroupsStore()
const matchesStore = useMatchesStore()

const showCreateGroupDialog = ref(false)
const showJoinGroupDialog = ref(false)
const newGroupName = ref('')
const inviteCode = ref('')
const isCreatingGroup = ref(false)
const isJoiningGroup = ref(false)

const isDistributionModalOpen = ref(false)
const selectedMatchId = ref<number | null>(null)
const selectedMatch = ref<any>(null)

function openDistribution(matchId: number) {
  const match = matchesStore.matches.find(m => m.id === matchId)
  if (match) {
    selectedMatch.value = match
    selectedMatchId.value = matchId
    isDistributionModalOpen.value = true
  }
}

function closeDistribution() {
  isDistributionModalOpen.value = false
  selectedMatchId.value = null
  selectedMatch.value = null
}

onMounted(async () => {
  try {
    await groupsStore.fetchGroups()
  } catch (error) {
    console.error('Error loading groups:', error)
  }
})

async function handleCreateGroup() {
  if (!newGroupName.value.trim()) return

  isCreatingGroup.value = true
  try {
    await groupsStore.createGroup(newGroupName.value)
    newGroupName.value = ''
    showCreateGroupDialog.value = false
  } catch (error) {
    console.error('Error creating group:', error)
    alert('Error al crear grupo')
  } finally {
    isCreatingGroup.value = false
  }
}

async function handleJoinGroup() {
  if (!inviteCode.value.trim()) return

  isJoiningGroup.value = true
  try {
    await groupsStore.joinGroup(inviteCode.value)
    inviteCode.value = ''
    showJoinGroupDialog.value = false
  } catch (error: any) {
    console.error('Error joining group:', error)
    if (error.response?.status === 404) {
      alert('Código de invitación inválido')
    } else {
      alert('Error al unirse al grupo')
    }
  } finally {
    isJoiningGroup.value = false
  }
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
