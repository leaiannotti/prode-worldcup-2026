<template>
  <AppLayout>
    <div class="px-gutter py-lg max-w-7xl mx-auto space-y-lg">
      <!-- Hero Section -->
      <section class="space-y-md">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-md">
          <div>
            <h1 class="font-headline-lg text-headline-lg text-primary mb-xs">Dashboard</h1>
            <p class="font-body-lg text-body-lg text-on-surface-variant">
              Welcome back, {{ authStore.user?.name }}! Manage your groups and track your performance.
            </p>
          </div>
          <div class="flex gap-sm">
            <button
              @click="showCreateGroupDialog = true"
              class="flex-1 md:flex-none bg-primary text-on-primary px-lg py-md rounded-lg font-bold hover:opacity-90 transition-all active:scale-95"
            >
              Create Group
            </button>
            <button
              @click="showJoinGroupDialog = true"
              class="flex-1 md:flex-none bg-secondary text-on-secondary px-lg py-md rounded-lg font-bold hover:opacity-90 transition-all active:scale-95"
            >
              Join Group
            </button>
          </div>
        </div>
      </section>

      <!-- Groups Grid -->
      <section v-if="groupsStore.groups.length > 0" class="space-y-md">
        <div class="flex items-center justify-between">
          <h2 class="font-headline-md text-headline-md text-primary">My Groups</h2>
          <span class="font-label-md text-label-md bg-surface-container px-sm py-xs rounded-full text-on-surface-variant">
            {{ groupsStore.groups.length }} group(s)
          </span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
          <GroupCard v-for="group in groupsStore.groups" :key="group.id" :group="group" />
        </div>
      </section>

      <!-- Empty State -->
      <section v-else class="py-xl text-center">
        <svg class="w-16 h-16 mx-auto mb-md text-on-surface-variant opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.856-1.487M15 10a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-xs">No Groups Yet</h3>
        <p class="font-body-md text-body-md text-on-surface-variant mb-lg">
          Create a new group or join an existing one to get started.
        </p>
        <button
          @click="showCreateGroupDialog = true"
          class="inline-block bg-primary text-on-primary px-lg py-md rounded-lg font-bold hover:opacity-90 transition-all"
        >
          Create Your First Group
        </button>
      </section>

      <!-- Create Group Dialog -->
      <div v-if="showCreateGroupDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-md">
        <div class="bg-surface rounded-xl p-lg max-w-md w-full space-y-md">
          <h3 class="font-headline-sm text-headline-sm text-primary">Create Group</h3>
          <input
            v-model="newGroupName"
            type="text"
            placeholder="Group name..."
            class="w-full px-md py-sm border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none"
          />
          <div class="flex gap-sm">
            <button
              @click="showCreateGroupDialog = false"
              class="flex-1 px-md py-sm border border-outline-variant rounded-lg font-bold hover:bg-surface-container transition-all"
            >
              Cancel
            </button>
            <button
              @click="handleCreateGroup"
              :disabled="isCreatingGroup || !newGroupName.trim()"
              class="flex-1 px-md py-sm bg-primary text-on-primary rounded-lg font-bold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {{ isCreatingGroup ? 'Creating...' : 'Create' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Join Group Dialog -->
      <div v-if="showJoinGroupDialog" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-md">
        <div class="bg-surface rounded-xl p-lg max-w-md w-full space-y-md">
          <h3 class="font-headline-sm text-headline-sm text-primary">Join Group</h3>
          <input
            v-model="inviteCode"
            type="text"
            placeholder="Invite code..."
            class="w-full px-md py-sm border border-outline-variant rounded-lg focus:border-primary focus:ring-2 focus:ring-secondary-container outline-none uppercase"
          />
          <div class="flex gap-sm">
            <button
              @click="showJoinGroupDialog = false"
              class="flex-1 px-md py-sm border border-outline-variant rounded-lg font-bold hover:bg-surface-container transition-all"
            >
              Cancel
            </button>
            <button
              @click="handleJoinGroup"
              :disabled="isJoiningGroup || !inviteCode.trim()"
              class="flex-1 px-md py-sm bg-secondary text-on-secondary rounded-lg font-bold hover:opacity-90 transition-all disabled:opacity-50"
            >
              {{ isJoiningGroup ? 'Joining...' : 'Join' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'
import AppLayout from '@/components/AppLayout.vue'
import GroupCard from '@/components/GroupCard.vue'

const authStore = useAuthStore()
const groupsStore = useGroupsStore()

const showCreateGroupDialog = ref(false)
const showJoinGroupDialog = ref(false)
const newGroupName = ref('')
const inviteCode = ref('')
const isCreatingGroup = ref(false)
const isJoiningGroup = ref(false)

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
    alert('Failed to create group')
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
      alert('Invalid invite code')
    } else {
      alert('Failed to join group')
    }
  } finally {
    isJoiningGroup.value = false
  }
}
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
