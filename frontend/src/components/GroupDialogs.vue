<template>
  <Teleport to="body">
    <!-- Create League Dialog -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="emit('close-create')">
      <div class="bg-surface text-on-surface rounded-xl border border-outline-variant p-6 max-w-md w-full shadow-xl space-y-5">
        <h3 class="font-headline-sm text-headline-sm text-primary">{{ t('groupDialog.createTitle') }}</h3>

        <!-- Name -->
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">{{ t('groupDialog.leagueName') }}</label>
          <input
            v-model="newGroupName"
            type="text"
            :placeholder="t('groupDialog.leagueNamePlaceholder')"
            class="w-full px-4 py-2.5 bg-surface-container-low text-on-surface border border-outline-variant rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none text-sm placeholder:text-on-surface-variant/50"
            @keyup.enter="handleCreate"
          />
        </div>

        <!-- Prizes -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <label class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">{{ t('groupDialog.prizes') }}</label>
            <div class="flex items-center gap-1">
              <button
                v-for="n in [0, 1, 2, 3]"
                :key="n"
                @click="prizeCount = n"
                class="w-7 h-7 rounded-full text-xs font-bold transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary cursor-pointer"
                :class="prizeCount === n ? 'bg-primary text-on-primary' : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'"
              >
                {{ n }}
              </button>
            </div>
          </div>

          <TransitionGroup name="prize-list">
            <div v-for="i in prizeCount" :key="i" class="flex items-center gap-3">
              <div
                class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 shadow-sm"
                :class="rankStyle(i)"
              >{{ i }}°</div>
              <input
                v-model="prizes[i - 1]"
                type="text"
                :placeholder="rankPlaceholder(i)"
                class="flex-1 px-3 py-2 bg-surface-container-low text-on-surface border border-outline-variant rounded-lg text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors placeholder:text-on-surface-variant/50"
              />
            </div>
          </TransitionGroup>
        </div>

        <p v-if="createError" class="text-error text-sm">{{ createError }}</p>

        <div class="flex gap-2">
          <button @click="emit('close-create')" class="flex-1 px-4 py-2.5 bg-surface-container-low text-on-surface border border-outline-variant rounded-lg font-semibold text-sm hover:bg-surface-container transition-all cursor-pointer">
            {{ t('groupDialog.cancel') }}
          </button>
          <button
            @click="handleCreate"
            :disabled="isCreating || !newGroupName.trim()"
            class="flex-1 px-4 py-2.5 bg-primary text-on-primary rounded-lg font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-40 cursor-pointer"
          >
            {{ isCreating ? t('groupDialog.creating') : t('groupDialog.create') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Join League Dialog -->
    <div v-if="showJoin" class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4" @click.self="emit('close-join')">
      <div class="bg-surface text-on-surface rounded-xl border border-outline-variant p-6 max-w-md w-full shadow-xl space-y-4">
        <h3 class="font-headline-sm text-headline-sm text-primary">{{ t('groupDialog.joinTitle') }}</h3>
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">{{ t('groupDialog.inviteCode') }}</label>
          <input
            v-model="inviteCode"
            type="text"
            placeholder="ABC123"
            autocomplete="off"
            autocapitalize="characters"
            spellcheck="false"
            class="w-full px-4 py-2.5 bg-surface-container-low text-on-surface border border-outline-variant rounded-lg focus:border-primary focus:ring-1 focus:ring-primary outline-none uppercase text-sm tracking-widest placeholder:text-on-surface-variant/50"
            @input="inviteCode = ($event.target as HTMLInputElement).value.toUpperCase()"
            @keyup.enter="handleJoin"
          />
        </div>
        <p v-if="joinError" class="text-error text-sm">{{ joinError }}</p>
        <div class="flex gap-2">
          <button @click="emit('close-join')" class="flex-1 px-4 py-2.5 bg-surface-container-low text-on-surface border border-outline-variant rounded-lg font-semibold text-sm hover:bg-surface-container transition-all cursor-pointer">
            {{ t('groupDialog.cancel') }}
          </button>
          <button
            @click="handleJoin"
            :disabled="isJoining || !inviteCode.trim()"
            class="flex-1 px-4 py-2.5 bg-secondary text-on-secondary rounded-lg font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-40 cursor-pointer"
          >
            {{ isJoining ? t('groupDialog.joining') : t('groupDialog.joinBtn') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import type { Prize } from '@/stores/groups'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  showCreate: boolean
  showJoin: boolean
}>()

const emit = defineEmits<{
  (e: 'close-create'): void
  (e: 'close-join'): void
  (e: 'created'): void
  (e: 'joined'): void
}>()

const { t } = useI18n()
const groupsStore = useGroupsStore()

const newGroupName = ref('')
const prizeCount = ref(0)
const prizes = ref(['', '', ''])
const isCreating = ref(false)
const createError = ref<string | null>(null)

const inviteCode = ref('')
const isJoining = ref(false)
const joinError = ref<string | null>(null)

watch(() => props.showCreate, (v) => {
  if (v) {
    newGroupName.value = ''
    prizeCount.value = 0
    prizes.value = ['', '', '']
    createError.value = null
  }
})
watch(() => props.showJoin, (v) => {
  if (v) { inviteCode.value = ''; joinError.value = null }
})

async function handleCreate() {
  if (!newGroupName.value.trim() || isCreating.value) return
  isCreating.value = true
  createError.value = null
  try {
    const prizeList: Prize[] = prizes.value
      .slice(0, prizeCount.value)
      .map((desc, i) => ({ rank: i + 1, description: desc.trim() }))
      .filter(p => p.description)

    await groupsStore.createGroup(newGroupName.value.trim(), prizeList.length ? prizeList : undefined)
    emit('created')
    emit('close-create')
  } catch {
    createError.value = t('groupDialog.createError')
  } finally {
    isCreating.value = false
  }
}

async function handleJoin() {
  const code = inviteCode.value.trim().toUpperCase()
  if (!code || isJoining.value) return
  isJoining.value = true
  joinError.value = null
  try {
    await groupsStore.joinGroup(code)
    emit('joined')
    emit('close-join')
  } catch (err: any) {
    joinError.value = err.response?.status === 404 ? t('groupDialog.invalidCode') : t('groupDialog.joinError')
  } finally {
    isJoining.value = false
  }
}

function rankStyle(rank: number): string {
  if (rank === 1) return 'bg-amber-400 text-amber-950'
  if (rank === 2) return 'bg-slate-300 text-slate-800'
  return 'bg-orange-300 text-orange-900'
}

function rankPlaceholder(rank: number): string {
  if (rank === 1) return t('groupDialog.prize1Placeholder')
  if (rank === 2) return t('groupDialog.prize2Placeholder')
  return t('groupDialog.prize3Placeholder')
}
</script>

<style scoped>
.prize-list-enter-active,
.prize-list-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.prize-list-enter-from,
.prize-list-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
