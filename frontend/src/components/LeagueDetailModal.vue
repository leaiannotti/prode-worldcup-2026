<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen && group" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="emit('close')">
        <div class="bg-surface rounded-xl w-full max-w-sm shadow-xl overflow-hidden">

          <!-- Header -->
          <div class="px-6 py-5 border-b border-outline-variant">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h3 class="font-headline-sm text-headline-sm text-primary">{{ group.name }}</h3>
                <p class="text-xs text-on-surface-variant mt-0.5">{{ group.member_count ?? 0 }} {{ t('leagueDetail.members') }}</p>
              </div>
              <button @click="emit('close')" class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors text-on-surface-variant flex-shrink-0 cursor-pointer">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div class="px-6 py-5 space-y-5">
            <!-- Invite code -->
            <div class="space-y-1.5">
              <p class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">{{ t('leagueDetail.inviteCode') }}</p>
              <div class="flex items-center gap-3 bg-surface-container-low rounded-xl px-4 py-3">
                <code class="flex-1 text-lg font-bold tracking-widest text-primary">{{ group.invite_code }}</code>
                <button
                  @click="copyCode"
                  class="flex items-center gap-1.5 text-xs font-semibold text-secondary hover:text-primary transition-colors cursor-pointer"
                >
                  <svg v-if="!copied" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <svg v-else class="w-4 h-4 text-tertiary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  {{ copied ? t('leagueDetail.copied') : t('leagueDetail.copy') }}
                </button>
              </div>
            </div>

            <!-- Prizes -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <p class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">{{ t('leagueDetail.prizes') }}</p>
                <button
                  v-if="!isEditing"
                  @click="enterEdit"
                  class="text-xs font-semibold text-secondary hover:text-primary transition-colors cursor-pointer"
                >
                  {{ t('leagueDetail.editPrizes') }}
                </button>
              </div>

              <!-- Read-only view -->
              <div v-if="!isEditing">
                <div v-if="group.prizes && group.prizes.length > 0" class="space-y-2">
                  <div
                    v-for="prize in sortedPrizes"
                    :key="prize.rank"
                    class="flex items-center gap-3 py-2"
                  >
                    <div
                      class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                      :class="rankStyle(prize.rank)"
                    >{{ prize.rank }}°</div>
                    <span class="text-sm text-on-surface">{{ prize.description }}</span>
                  </div>
                </div>
                <div v-else class="text-xs text-on-surface-variant/60 italic">{{ t('leagueDetail.noPrizes') }}</div>
              </div>

              <!-- Edit mode -->
              <div v-else class="space-y-3">
                <div class="space-y-1">
                  <label class="text-xs text-on-surface-variant">{{ t('leagueDetail.prizeRankFirst') }}</label>
                  <input
                    v-model="draftPrizes.first"
                    :disabled="isSaving"
                    type="text"
                    maxlength="200"
                    class="w-full text-sm bg-surface-container-low rounded-xl px-3 py-2 border border-outline-variant focus:border-primary focus:outline-none text-on-surface disabled:opacity-40"
                  />
                  <p class="text-[10px] text-on-surface-variant" :class="{ 'text-error': draftPrizes.first.length > 200 }">
                    {{ t('leagueDetail.charCounter', { count: draftPrizes.first.length }) }}
                  </p>
                </div>
                <div class="space-y-1">
                  <label class="text-xs text-on-surface-variant">{{ t('leagueDetail.prizeRankSecond') }}</label>
                  <input
                    v-model="draftPrizes.second"
                    :disabled="isSaving"
                    type="text"
                    maxlength="200"
                    class="w-full text-sm bg-surface-container-low rounded-xl px-3 py-2 border border-outline-variant focus:border-primary focus:outline-none text-on-surface disabled:opacity-40"
                  />
                  <p class="text-[10px] text-on-surface-variant" :class="{ 'text-error': draftPrizes.second.length > 200 }">
                    {{ t('leagueDetail.charCounter', { count: draftPrizes.second.length }) }}
                  </p>
                </div>
                <div class="space-y-1">
                  <label class="text-xs text-on-surface-variant">{{ t('leagueDetail.prizeRankThird') }}</label>
                  <input
                    v-model="draftPrizes.third"
                    :disabled="isSaving"
                    type="text"
                    maxlength="200"
                    class="w-full text-sm bg-surface-container-low rounded-xl px-3 py-2 border border-outline-variant focus:border-primary focus:outline-none text-on-surface disabled:opacity-40"
                  />
                  <p class="text-[10px] text-on-surface-variant" :class="{ 'text-error': draftPrizes.third.length > 200 }">
                    {{ t('leagueDetail.charCounter', { count: draftPrizes.third.length }) }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button
                    @click="handleSave"
                    :disabled="isSaving || !canSave"
                    class="flex-1 py-2 bg-primary text-on-primary rounded-xl font-semibold text-sm transition-all active:scale-95 disabled:opacity-40 cursor-pointer flex items-center justify-center gap-1"
                  >
                    <svg v-if="isSaving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span v-else>{{ t('leagueDetail.savePrizes') }}</span>
                  </button>
                  <button
                    @click="cancelEdit"
                    :disabled="isSaving"
                    class="flex-1 py-2 border border-outline-variant text-on-surface-variant rounded-xl font-semibold text-sm transition-colors hover:bg-surface-container disabled:opacity-40 cursor-pointer"
                  >
                    {{ t('leagueDetail.cancel') }}
                  </button>
                </div>
                <p v-if="saveError" class="text-error text-xs text-center">{{ saveError }}</p>
              </div>
            </div>

            <!-- Audit History -->
            <div class="space-y-1.5">
              <button
                @click="toggleHistory"
                class="w-full flex items-center justify-between text-xs font-semibold text-secondary hover:text-primary transition-colors cursor-pointer py-1"
              >
                <span>{{ isHistoryExpanded ? t('leagueDetail.hideHistory') : t('leagueDetail.viewHistory') }}</span>
                <svg v-if="isHistoryExpanded" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                </svg>
                <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <div v-if="isHistoryExpanded" class="space-y-2">
                <div v-if="isHistoryLoading" class="space-y-2">
                  <div v-for="i in 3" :key="i" class="h-8 bg-surface-container animate-pulse rounded-lg"></div>
                </div>
                <div v-else-if="historyError" class="text-error text-xs text-center">{{ historyError }}</div>
                <div v-else-if="historyEvents.length === 0" class="text-xs text-on-surface-variant/60 italic text-center">
                  {{ t('activity.empty') }}
                </div>
                <div v-else class="space-y-2">
                  <div
                    v-for="event in historyEvents.slice(0, 10)"
                    :key="event.id"
                    class="text-xs text-on-surface leading-snug"
                  >
                    {{ formatPrizeChangedEvent(event, t) }} — {{ formatRelativeTime(event.occurred_at) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="pt-1 space-y-2">
              <!-- Leave (non-admin) -->
              <button
                v-if="!isAdmin"
                @click="handleLeave"
                :disabled="isLeaving"
                class="w-full py-2.5 border border-error text-error rounded-xl font-semibold text-sm hover:bg-error/5 transition-all active:scale-[0.98] disabled:opacity-40 cursor-pointer"
              >
                {{ isLeaving ? t('leagueDetail.leaving') : t('leagueDetail.leave') }}
              </button>

              <p v-if="leaveError" class="text-error text-xs text-center">{{ leaveError }}</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'
import { useActivityStore } from '@/stores/activity'
import type { Group } from '@/stores/groups'
import { formatRelativeTime } from '@/composables/useDateFormat'
import { formatPrizeChangedEvent } from '@/utils/activity'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  isOpen: boolean
  group: Group | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'left'): void
  (e: 'deleted'): void
}>()

const { t } = useI18n()
const authStore = useAuthStore()
const groupsStore = useGroupsStore()
const activityStore = useActivityStore()

const copied = ref(false)
const isLeaving = ref(false)
const leaveError = ref<string | null>(null)

const isEditing = ref(false)
const isSaving = ref(false)
const saveError = ref<string | null>(null)
const draftPrizes = ref({ first: '', second: '', third: '' })

const isHistoryExpanded = ref(false)
const historyEvents = ref<any[]>([])
const isHistoryLoading = ref(false)
const historyError = ref<string | null>(null)

watch(() => props.isOpen, (v) => {
  if (v) {
    copied.value = false
    leaveError.value = null
    isEditing.value = false
    saveError.value = null
    isHistoryExpanded.value = false
    historyEvents.value = []
    historyError.value = null
  }
})

async function toggleHistory() {
  if (!props.group) return
  isHistoryExpanded.value = !isHistoryExpanded.value
  if (isHistoryExpanded.value && historyEvents.value.length === 0) {
    isHistoryLoading.value = true
    historyError.value = null
    try {
      await activityStore.fetchActivity({
        groupId: props.group.id,
        eventType: 'prize_changed',
        limit: 10,
      })
      historyEvents.value = activityStore.events
    } catch {
      historyError.value = t('activity.error')
    } finally {
      isHistoryLoading.value = false
    }
  }
}

const isOverLimit = computed(() => {
  return (
    draftPrizes.value.first.length > 200 ||
    draftPrizes.value.second.length > 200 ||
    draftPrizes.value.third.length > 200
  )
})

const isAllEmpty = computed(() => {
  return (
    !draftPrizes.value.first.trim() &&
    !draftPrizes.value.second.trim() &&
    !draftPrizes.value.third.trim()
  )
})

const canSave = computed(() => !isOverLimit.value && !isAllEmpty.value)

function enterEdit() {
  if (!props.group) return
  draftPrizes.value = {
    first: props.group.prizes?.find((p) => p.rank === 1)?.description ?? '',
    second: props.group.prizes?.find((p) => p.rank === 2)?.description ?? '',
    third: props.group.prizes?.find((p) => p.rank === 3)?.description ?? '',
  }
  isEditing.value = true
  saveError.value = null
}

function cancelEdit() {
  isEditing.value = false
  saveError.value = null
}

async function handleSave() {
  if (!props.group) return
  isSaving.value = true
  saveError.value = null
  try {
    const payload: any = {}
    const currentFirst = props.group.prizes?.find((p) => p.rank === 1)?.description ?? ''
    const currentSecond = props.group.prizes?.find((p) => p.rank === 2)?.description ?? ''
    const currentThird = props.group.prizes?.find((p) => p.rank === 3)?.description ?? ''

    if (draftPrizes.value.first.trim() !== currentFirst) payload.first = draftPrizes.value.first.trim()
    if (draftPrizes.value.second.trim() !== currentSecond) payload.second = draftPrizes.value.second.trim()
    if (draftPrizes.value.third.trim() !== currentThird) payload.third = draftPrizes.value.third.trim()

    if (Object.keys(payload).length > 0) {
      await groupsStore.patchPrizes(props.group.id, payload)
    }
    isEditing.value = false
  } catch (err: any) {
    if (err.response?.status === 403) {
      saveError.value = t('leagueDetail.errorForbidden')
    } else if (err.response?.status === 422) {
      saveError.value = t('leagueDetail.errorValidation')
    } else {
      saveError.value = t('leagueDetail.errorGeneric')
    }
  } finally {
    isSaving.value = false
  }
}

const isAdmin = computed(() => {
  // Creator is admin — compare with current user
  return (props.group as any)?.creator_id === authStore.user?.id
})

const sortedPrizes = computed(() =>
  [...(props.group?.prizes ?? [])].sort((a, b) => a.rank - b.rank)
)

function copyCode() {
  if (!props.group) return
  navigator.clipboard.writeText(props.group.invite_code)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

async function handleLeave() {
  if (!props.group || isLeaving.value) return
  isLeaving.value = true
  leaveError.value = null
  try {
    await groupsStore.leaveGroup(props.group.id)
    emit('left')
    emit('close')
  } catch {
    leaveError.value = t('leagueDetail.leaveError')
  } finally {
    isLeaving.value = false
  }
}

function rankStyle(rank: number): string {
  if (rank === 1) return 'bg-amber-400 text-amber-950'
  if (rank === 2) return 'bg-slate-300 text-slate-800'
  return 'bg-orange-300 text-orange-900'
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .bg-surface, .modal-leave-active .bg-surface { transition: transform 0.2s cubic-bezier(0.16,1,0.3,1); }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .bg-surface { transform: scale(0.96); }
</style>
