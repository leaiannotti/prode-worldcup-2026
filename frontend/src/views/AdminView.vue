<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-7xl mx-auto space-y-6">

      <!-- Header -->
      <section class="flex items-center justify-between">
        <div>
          <h1 class="font-headline-lg text-headline-lg text-primary">Admin Panel</h1>
          <p class="font-body-md text-on-surface-variant mt-0.5">Gestión del Mundial 2026</p>
        </div>
        <span class="text-xs font-label-sm bg-tertiary-container text-on-tertiary-container px-3 py-1 rounded-full uppercase tracking-wider">
          Solo vos
        </span>
      </section>

      <!-- Stats badges -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div v-for="stat in stats" :key="stat.label"
          class="bg-surface-container-highest border border-outline-variant rounded-2xl p-5 flex flex-col gap-2 relative overflow-hidden">
          <div class="absolute -right-3 -top-3 w-20 h-20 rounded-full opacity-5" :style="{ background: stat.color }"></div>
          <span class="font-label-sm text-label-sm text-on-surface-variant uppercase">{{ stat.label }}</span>
          <span class="font-headline-lg text-headline-lg" :style="{ color: stat.color }">
            {{ stat.loading ? '...' : stat.value.toLocaleString() }}
          </span>
        </div>
      </div>

      <!-- Gestión de partidos -->
      <section class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="font-headline-md text-headline-md text-primary">Gestión de Partidos</h2>
          <div class="flex items-center gap-2">
            <button @click="filterStatus = ''"
              class="text-xs px-3 py-1 rounded-full border transition-colors"
              :class="filterStatus === '' ? 'bg-primary text-on-primary border-primary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container'">
              Todos
            </button>
            <button @click="filterStatus = 'scheduled'"
              class="text-xs px-3 py-1 rounded-full border transition-colors"
              :class="filterStatus === 'scheduled' ? 'bg-secondary text-on-secondary border-secondary' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container'">
              Próximos
            </button>
            <button @click="filterStatus = 'finished'"
              class="text-xs px-3 py-1 rounded-full border transition-colors"
              :class="filterStatus === 'finished' ? 'bg-surface-container-highest text-on-surface border-outline' : 'border-outline-variant text-on-surface-variant hover:bg-surface-container'">
              Finalizados
            </button>
          </div>
        </div>

        <div class="bg-surface-container-lowest rounded-2xl border border-outline-variant overflow-hidden">
          <div v-if="matchesLoading" class="p-6 space-y-3">
            <div v-for="i in 5" :key="i" class="h-12 bg-surface-container animate-pulse rounded-lg"></div>
          </div>
          <div v-else class="overflow-x-auto max-h-[420px] overflow-y-auto">
            <table class="w-full text-left">
              <thead>
                <tr class="bg-surface-container-low border-b border-outline-variant">
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase">Partido</th>
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase">Grupo</th>
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase">Fecha</th>
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase">Estado</th>
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase text-center">Resultado</th>
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase text-center">Preds</th>
                  <th class="px-4 py-3 font-label-sm text-label-sm text-on-surface-variant uppercase text-right">Acción</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-outline-variant">
                <tr v-for="match in filteredMatches" :key="match.id" class="hover:bg-surface-container-low transition-colors">
                  <!-- Teams -->
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                      <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" class="w-6 h-4 object-cover rounded-sm border border-outline-variant/40" />
                      <span class="font-label-md text-sm text-on-surface">{{ match.home_team.code }}</span>
                      <span class="text-xs text-on-surface-variant">vs</span>
                      <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" class="w-6 h-4 object-cover rounded-sm border border-outline-variant/40" />
                      <span class="font-label-md text-sm text-on-surface">{{ match.away_team.code }}</span>
                    </div>
                  </td>
                  <!-- Group -->
                  <td class="px-4 py-3 text-sm text-on-surface-variant">Grupo {{ match.group }}</td>
                  <!-- Kickoff -->
                  <td class="px-4 py-3 text-xs text-on-surface-variant font-label-sm">{{ formatKickoff(match.kickoff_at) }}</td>
                  <!-- Status -->
                  <td class="px-4 py-3">
                    <span class="text-xs px-2 py-0.5 rounded-full font-bold"
                      :class="{
                        'bg-secondary-container text-on-secondary-container': match.status === 'scheduled',
                        'bg-surface-container-highest text-on-surface': match.status === 'finished',
                        'bg-tertiary-container text-on-tertiary-container': match.status === 'in_progress',
                      }">
                      {{ statusLabel(match.status) }}
                    </span>
                  </td>
                  <!-- Score -->
                  <td class="px-4 py-3 text-center font-label-sm text-sm">
                    <span v-if="match.home_score !== null" class="font-bold text-on-surface">
                      {{ match.home_score }} - {{ match.away_score }}
                    </span>
                    <span v-else class="text-on-surface-variant">—</span>
                  </td>
                  <!-- Prediction count -->
                  <td class="px-4 py-3 text-center text-sm text-on-surface-variant">{{ match.prediction_count }}</td>
                  <!-- Action -->
                  <td class="px-4 py-3 text-right">
                    <button
                      @click="openResultModal(match)"
                      class="text-xs px-3 py-1.5 rounded-lg font-label-md transition-all active:scale-95"
                      :class="match.status === 'finished'
                        ? 'bg-surface-container border border-outline-variant text-on-surface-variant hover:bg-surface-container-high'
                        : 'bg-primary text-on-primary hover:opacity-90'">
                      {{ match.status === 'finished' ? 'Editar' : 'Cargar resultado' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <!-- Audit log -->
      <section class="space-y-3">
        <div class="flex items-center justify-between">
          <h2 class="font-headline-md text-headline-md text-primary">System Audit Log</h2>
          <button @click="fetchAuditLog"
            class="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg bg-surface-container border border-outline-variant text-on-surface-variant hover:bg-surface-container-high transition-colors">
            <svg class="w-3.5 h-3.5" :class="auditLoading ? 'animate-spin' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refrescar
          </button>
        </div>

        <div class="bg-primary rounded-2xl border border-outline-variant p-5">
          <div v-if="auditLoading" class="space-y-2">
            <div v-for="i in 4" :key="i" class="h-12 bg-primary-container animate-pulse rounded-lg"></div>
          </div>
          <div v-else-if="auditEvents.length === 0" class="text-center py-8 text-on-primary-container opacity-60 font-body-md text-sm">
            No hay eventos aún.
          </div>
          <div v-else class="space-y-2 max-h-[420px] overflow-y-auto pr-1">
            <div v-for="event in auditEvents" :key="event.id"
              class="bg-primary-container rounded-lg px-4 py-3 flex items-start gap-3 border-l-4"
              :class="eventBorderColor(event.event_type)">
              <div class="flex-1 min-w-0">
                <p class="text-white text-sm font-bold truncate">
                  <span class="opacity-70">{{ event.user_name }}</span>
                  {{ ' · ' + eventLabel(event.event_type) }}
                </p>
                <p class="text-on-primary-container text-xs mt-0.5 opacity-70">{{ formatRelative(event.occurred_at) }}</p>
              </div>
              <span class="text-[10px] font-label-sm text-on-primary-container opacity-50 flex-shrink-0 mt-0.5 uppercase">{{ event.event_type }}</span>
            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- Modal cargar resultado -->
    <Transition name="modal">
      <div v-if="resultModal.open" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="closeResultModal" />

        <div class="relative z-10 w-full max-w-md bg-surface rounded-3xl shadow-2xl overflow-hidden">

          <!-- Header con banderas -->
          <div class="px-6 pt-6 pb-8 text-center relative" style="background: #00134d;">
            <button @click="closeResultModal"
              class="absolute right-4 top-4 text-white/60 hover:text-white transition-colors">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
            <p class="text-white/60 font-label-sm text-xs uppercase tracking-widest mb-3">Cargar resultado</p>
            <div class="flex items-center justify-center gap-4">
              <div class="flex flex-col items-center gap-1.5">
                <img v-if="resultModal.match?.home_team.flag_url"
                  :src="resultModal.match.home_team.flag_url"
                  class="w-10 h-7 object-cover rounded shadow-lg" />
                <span class="text-white font-headline-sm text-sm font-bold">{{ resultModal.match?.home_team.code }}</span>
              </div>
              <span class="text-white/40 font-display-lg text-2xl">vs</span>
              <div class="flex flex-col items-center gap-1.5">
                <img v-if="resultModal.match?.away_team.flag_url"
                  :src="resultModal.match.away_team.flag_url"
                  class="w-10 h-7 object-cover rounded shadow-lg" />
                <span class="text-white font-headline-sm text-sm font-bold">{{ resultModal.match?.away_team.code }}</span>
              </div>
            </div>
          </div>

          <!-- Score inputs -->
          <div class="px-6 py-6">
            <div class="flex items-center justify-center gap-3 mb-6">
              <!-- Home score -->
              <div class="flex flex-col items-center gap-2">
                <span class="text-xs font-label-sm text-on-surface-variant uppercase tracking-wider">{{ resultModal.match?.home_team.code }}</span>
                <div class="flex items-center gap-1">
                  <button @click="resultModal.homeScore = Math.max(0, resultModal.homeScore - 1)"
                    class="w-8 h-8 rounded-full bg-surface-container hover:bg-surface-container-high border border-outline-variant text-on-surface font-bold transition-all active:scale-90 touch-manipulation">
                    −
                  </button>
                  <div class="w-16 h-16 flex items-center justify-center bg-primary/5 border-2 border-primary/20 rounded-2xl">
                    <span class="font-display-lg text-4xl text-primary font-bold leading-none">{{ resultModal.homeScore }}</span>
                  </div>
                  <button @click="resultModal.homeScore++"
                    class="w-8 h-8 rounded-full bg-surface-container hover:bg-surface-container-high border border-outline-variant text-on-surface font-bold transition-all active:scale-90 touch-manipulation">
                    +
                  </button>
                </div>
              </div>

              <span class="font-display-lg text-3xl text-on-surface-variant/30 mt-5">—</span>

              <!-- Away score -->
              <div class="flex flex-col items-center gap-2">
                <span class="text-xs font-label-sm text-on-surface-variant uppercase tracking-wider">{{ resultModal.match?.away_team.code }}</span>
                <div class="flex items-center gap-1">
                  <button @click="resultModal.awayScore = Math.max(0, resultModal.awayScore - 1)"
                    class="w-8 h-8 rounded-full bg-surface-container hover:bg-surface-container-high border border-outline-variant text-on-surface font-bold transition-all active:scale-90 touch-manipulation">
                    −
                  </button>
                  <div class="w-16 h-16 flex items-center justify-center bg-secondary/5 border-2 border-secondary/20 rounded-2xl">
                    <span class="font-display-lg text-4xl text-secondary font-bold leading-none">{{ resultModal.awayScore }}</span>
                  </div>
                  <button @click="resultModal.awayScore++"
                    class="w-8 h-8 rounded-full bg-surface-container hover:bg-surface-container-high border border-outline-variant text-on-surface font-bold transition-all active:scale-90 touch-manipulation">
                    +
                  </button>
                </div>
              </div>
            </div>

            <!-- Success / Error -->
            <div v-if="resultModal.success"
              class="mb-4 px-4 py-3 bg-secondary-container rounded-xl text-on-secondary-container text-sm font-bold text-center">
              ✓ Guardado — {{ resultModal.scoresCalculated }} puntos calculados
            </div>
            <p v-if="resultModal.error" class="mb-4 text-center text-xs text-error">{{ resultModal.error }}</p>

            <!-- Actions -->
            <div class="flex gap-3">
              <button @click="closeResultModal"
                class="flex-1 py-3 rounded-2xl border border-outline-variant text-on-surface-variant font-label-md text-sm hover:bg-surface-container transition-colors">
                Cancelar
              </button>
              <button @click="submitResult"
                :disabled="resultModal.saving"
                class="flex-1 py-3 rounded-2xl bg-primary text-on-primary font-label-md text-sm font-bold hover:opacity-90 transition-all active:scale-95 disabled:opacity-60">
                {{ resultModal.saving ? 'Guardando...' : 'Confirmar resultado' }}
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>

  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import { formatRelativeTime } from '@/composables/useDateFormat'

const apiBase = import.meta.env.VITE_API_URL ?? ''

// ── Stats ─────────────────────────────────────────────────────────────────────
const stats = ref([
  { label: 'Usuarios', value: 0, color: 'var(--color-primary)', loading: true },
  { label: 'Predicciones', value: 0, color: 'var(--color-secondary)', loading: true },
  { label: 'Ligas', value: 0, color: 'var(--color-tertiary)', loading: true },
])

async function fetchStats() {
  const res = await fetch(`${apiBase}/api/admin/stats`, { credentials: 'include' })
  if (!res.ok) return
  const data = await res.json()
  stats.value[0].value = data.users
  stats.value[1].value = data.predictions
  stats.value[2].value = data.groups
  stats.value.forEach(s => s.loading = false)
}

// ── Matches ────────────────────────────────────────────────────────────────────
interface AdminMatch {
  id: number
  home_team: { code: string; name: string; flag_url: string }
  away_team: { code: string; name: string; flag_url: string }
  group: string
  kickoff_at: string
  status: string
  home_score: number | null
  away_score: number | null
  prediction_count: number
}

const matches = ref<AdminMatch[]>([])
const matchesLoading = ref(true)
const filterStatus = ref('')

const filteredMatches = computed(() =>
  filterStatus.value ? matches.value.filter(m => m.status === filterStatus.value) : matches.value
)

async function fetchMatches() {
  matchesLoading.value = true
  const res = await fetch(`${apiBase}/api/admin/matches`, { credentials: 'include' })
  if (res.ok) matches.value = await res.json()
  matchesLoading.value = false
}

function statusLabel(status: string) {
  if (status === 'scheduled') return 'Próximo'
  if (status === 'finished') return 'Finalizado'
  if (status === 'in_progress') return 'En curso'
  return status
}

function formatKickoff(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// ── Result modal ───────────────────────────────────────────────────────────────
const resultModal = ref({
  open: false,
  match: null as AdminMatch | null,
  homeScore: 0,
  awayScore: 0,
  saving: false,
  error: '',
  success: false,
  scoresCalculated: 0,
})

function openResultModal(match: AdminMatch) {
  resultModal.value = {
    open: true,
    match,
    homeScore: match.home_score ?? 0,
    awayScore: match.away_score ?? 0,
    saving: false,
    error: '',
    success: false,
    scoresCalculated: 0,
  }
}

function closeResultModal() {
  resultModal.value.open = false
  if (resultModal.value.success) fetchMatches()
}

async function submitResult() {
  const m = resultModal.value
  if (!m.match) return
  if (m.homeScore < 0 || m.awayScore < 0) {
    m.error = 'Los marcadores no pueden ser negativos.'
    return
  }
  m.saving = true
  m.error = ''
  m.success = false

  const res = await fetch(`${apiBase}/api/admin/matches/${m.match.id}/result`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ home_score: m.homeScore, away_score: m.awayScore }),
  })

  m.saving = false
  if (res.ok) {
    const data = await res.json()
    m.success = true
    m.scoresCalculated = data.scores_calculated
    fetchStats()
  } else {
    m.error = 'Error al guardar. Intentá de nuevo.'
  }
}

// ── Audit log ─────────────────────────────────────────────────────────────────
interface AuditEvent {
  id: string
  user_name: string
  user_email: string
  event_type: string
  payload: any
  occurred_at: string
}

const auditEvents = ref<AuditEvent[]>([])
const auditLoading = ref(false)

async function fetchAuditLog() {
  auditLoading.value = true
  const res = await fetch(`${apiBase}/api/admin/audit-log?limit=50`, { credentials: 'include' })
  if (res.ok) auditEvents.value = await res.json()
  auditLoading.value = false
}

function eventLabel(type: string): string {
  const labels: Record<string, string> = {
    prediction_submitted: 'hizo una predicción',
    prediction_updated: 'actualizó su predicción',
    score_calculated: 'recibió puntos',
    group_created: 'creó una liga',
    group_joined: 'se unió a una liga',
  }
  return labels[type] ?? type
}

function eventBorderColor(type: string): string {
  if (type === 'prediction_submitted') return 'border-secondary-fixed'
  if (type === 'prediction_updated') return 'border-primary-fixed'
  if (type === 'score_calculated') return 'border-tertiary-fixed'
  if (type.includes('group')) return 'border-secondary-fixed-dim'
  return 'border-outline'
}

function formatRelative(iso: string) {
  return formatRelativeTime(iso)
}

// ── Init ───────────────────────────────────────────────────────────────────────
onMounted(() => {
  fetchStats()
  fetchMatches()
  fetchAuditLog()
})
</script>

<style scoped>
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}
</style>
