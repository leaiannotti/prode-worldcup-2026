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
                <p class="text-xs text-on-surface-variant mt-0.5">{{ group.member_count ?? 0 }} miembros</p>
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
              <p class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">Código de invitación</p>
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
                  {{ copied ? '¡Copiado!' : 'Copiar' }}
                </button>
              </div>
            </div>

            <!-- Prizes -->
            <div v-if="group.prizes && group.prizes.length > 0" class="space-y-1.5">
              <p class="text-xs font-medium text-on-surface-variant uppercase tracking-wide">Premios</p>
              <div class="space-y-2">
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
            </div>
            <div v-else class="text-xs text-on-surface-variant/60 italic">Sin premios configurados</div>

            <!-- Actions -->
            <div class="pt-1 space-y-2">
              <button
                v-if="!isAdmin"
                @click="handleLeave"
                :disabled="isLeaving"
                class="w-full py-2.5 border border-error text-error rounded-xl font-semibold text-sm hover:bg-error/5 transition-all active:scale-[0.98] disabled:opacity-40 cursor-pointer"
              >
                {{ isLeaving ? 'Abandonando...' : 'Abandonar liga' }}
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
import type { Group } from '@/stores/groups'

const props = defineProps<{
  isOpen: boolean
  group: Group | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'left'): void
}>()

const authStore = useAuthStore()
const groupsStore = useGroupsStore()

const copied = ref(false)
const isLeaving = ref(false)
const leaveError = ref<string | null>(null)

watch(() => props.isOpen, (v) => {
  if (v) { copied.value = false; leaveError.value = null }
})

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
    leaveError.value = 'Error al abandonar. Intentá de nuevo.'
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
