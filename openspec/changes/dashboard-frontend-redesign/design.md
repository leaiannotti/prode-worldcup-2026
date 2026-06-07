# Design: Dashboard Frontend Redesign

## Implementation Order

1. Stores (base layer — no UI dependencies)
2. Widgets (dependen de stores)
3. Dashboard Layout (integra widgets)
4. Match Distribution Modal (standalone, triggered by widgets)

---

## 1. Stores

### New: `scores.ts` (My Standing)

```typescript
// frontend/src/stores/scores.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface MyStandingItem {
  group_id: string
  group_name: string
  rank: number
  total_points: number
  member_count: number
}

export const useScoresStore = defineStore('scores', () => {
  const myStanding = ref<MyStandingItem[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMyStanding(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get('/api/scores/my-standing')
      myStanding.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Failed to load standing'
      console.error('Error fetching my standing:', err)
    } finally {
      isLoading.value = false
    }
  }

  return { myStanding, isLoading, error, fetchMyStanding }
})
```

### New: `activity.ts` (Activity Feed)

```typescript
// frontend/src/stores/activity.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/lib/api'

export interface ActivityEvent {
  id: string
  event_type: 'group_joined' | 'prediction_submitted'
  group_id: string | null
  match_id: number | null
  payload: Record<string, any>
  occurred_at: string
}

export const useActivityStore = defineStore('activity', () => {
  const events = ref<ActivityEvent[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchActivity(limit: number = 10): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const response = await apiClient.get(`/api/activity?limit=${limit}`)
      events.value = response.data.events
    } catch (err: any) {
      error.value = err.message || 'Failed to load activity'
      console.error('Error fetching activity:', err)
    } finally {
      isLoading.value = false
    }
  }

  return { events, isLoading, error, fetchActivity }
})
```

### Extend: `matches.ts` (Add status + limit filters)

```typescript
// Add to frontend/src/stores/matches.ts

export interface MatchFilters {
  group?: string
  date?: string
  status?: 'upcoming' | 'scheduled' | 'in_progress' | 'finished'
  limit?: number
}

// Update fetchMatches:
async function fetchMatches(filters?: MatchFilters): Promise<void> {
  try {
    const params = new URLSearchParams()
    if (filters?.group) params.append('group', filters.group)
    if (filters?.date) params.append('date', filters.date)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.limit) params.append('limit', String(filters.limit))

    const queryString = params.toString()
    const url = queryString ? `/api/matches?${queryString}` : '/api/matches'
    const response = await apiClient.get(url)
    matches.value = response.data
  } catch (error) {
    console.error('Error fetching matches:', error)
    throw error
  }
}
```

---

## 2. Widgets

### UpcomingMatchesWidget.vue

```vue
<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Próximos Partidos</h2>
    
    <!-- Loading -->
    <div v-if="matchesStore.isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-16 bg-surface-container animate-pulse rounded-lg"></div>
    </div>
    
    <!-- Error -->
    <div v-else-if="matchesStore.error" class="text-error font-body-md">
      Error al cargar partidos
    </div>
    
    <!-- Empty -->
    <div v-else-if="upcomingMatches.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No hay partidos próximos
    </div>
    
    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="match in upcomingMatches"
        :key="match.id"
        @click="openDistribution(match.id)"
        class="flex items-center gap-3 p-3 bg-surface-container-low rounded-lg hover:bg-surface-container transition-colors cursor-pointer"
      >
        <!-- Home Team -->
        <div class="flex items-center gap-2 flex-1">
          <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" class="w-8 h-6 object-cover rounded" />
          <span class="font-body-md text-on-surface font-medium">{{ match.home_team.name }}</span>
        </div>
        
        <!-- VS -->
        <span class="font-label-md text-on-surface-variant">VS</span>
        
        <!-- Away Team -->
        <div class="flex items-center gap-2 flex-1 justify-end">
          <span class="font-body-md text-on-surface font-medium">{{ match.away_team.name }}</span>
          <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" class="w-8 h-6 object-cover rounded" />
        </div>
        
        <!-- Date -->
        <span class="font-label-sm text-on-surface-variant ml-2">{{ formatDate(match.kickoff_utc) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useMatchesStore } from '@/stores/matches'

const matchesStore = useMatchesStore()

const upcomingMatches = computed(() => matchesStore.matches)

onMounted(() => {
  matchesStore.fetchMatches({ status: 'upcoming', limit: 5 })
})

function openDistribution(matchId: number) {
  emit('open-distribution', matchId)
}

function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const emit = defineEmits<{
  (e: 'open-distribution', matchId: number): void
}>()
</script>
```

### MyStandingWidget.vue

```vue
<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Mi Posición</h2>
    
    <!-- Loading -->
    <div v-if="scoresStore.isLoading" class="space-y-3">
      <div v-for="i in 2" :key="i" class="h-14 bg-surface-container animate-pulse rounded-lg"></div>
    </div>
    
    <!-- Error -->
    <div v-else-if="scoresStore.error" class="text-error font-body-md">
      Error al cargar posición
    </div>
    
    <!-- Empty -->
    <div v-else-if="scoresStore.myStanding.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No perteneces a ningún grupo aún
    </div>
    
    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="item in scoresStore.myStanding"
        :key="item.group_id"
        class="flex items-center justify-between p-3 bg-surface-container-low rounded-lg"
      >
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold"
               :class="rankColor(item.rank)">
            {{ item.rank }}
          </div>
          <div>
            <p class="font-body-md text-on-surface font-medium">{{ item.group_name }}</p>
            <p class="font-label-sm text-on-surface-variant">{{ item.member_count }} miembros</p>
          </div>
        </div>
        <div class="text-right">
          <p class="font-headline-sm text-primary font-bold">{{ item.total_points }} pts</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useScoresStore } from '@/stores/scores'

const scoresStore = useScoresStore()

onMounted(() => {
  scoresStore.fetchMyStanding()
})

function rankColor(rank: number): string {
  if (rank === 1) return 'bg-tertiary text-on-tertiary'
  if (rank === 2) return 'bg-secondary text-on-secondary'
  if (rank === 3) return 'bg-primary text-on-primary'
  return 'bg-surface-container text-on-surface'
}
</script>
```

### ActivityFeedWidget.vue

```vue
<template>
  <div class="bg-surface-container-lowest rounded-xl p-5 border border-outline-variant">
    <h2 class="font-headline-md text-headline-md text-primary mb-4">Actividad Reciente</h2>
    
    <!-- Loading -->
    <div v-if="activityStore.isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-12 bg-surface-container animate-pulse rounded-lg"></div>
    </div>
    
    <!-- Error -->
    <div v-else-if="activityStore.error" class="text-error font-body-md">
      Error al cargar actividad
    </div>
    
    <!-- Empty -->
    <div v-else-if="activityStore.events.length === 0" class="text-on-surface-variant font-body-md text-center py-4">
      No hay actividad reciente
    </div>
    
    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="event in activityStore.events"
        :key="event.id"
        class="flex items-start gap-3 p-3 bg-surface-container-low rounded-lg"
      >
        <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
             :class="eventIcon(event.event_type).bgClass">
          <svg class="w-4 h-4" :class="eventIcon(event.event_type).iconClass" fill="currentColor" viewBox="0 0 20 20">
            <path v-if="event.event_type === 'group_joined'" d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
            <path v-else d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6zM10 18a3 3 0 01-3-3h6a3 3 0 01-3 3z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="font-body-md text-on-surface">{{ eventDescription(event) }}</p>
          <p class="font-label-sm text-on-surface-variant">{{ formatRelativeTime(event.occurred_at) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useActivityStore } from '@/stores/activity'

const activityStore = useActivityStore()

onMounted(() => {
  activityStore.fetchActivity(10)
})

function eventIcon(type: string) {
  if (type === 'group_joined') {
    return { bgClass: 'bg-secondary-container', iconClass: 'text-on-secondary-container' }
  }
  return { bgClass: 'bg-primary-container', iconClass: 'text-on-primary-container' }
}

function eventDescription(event: any): string {
  if (event.event_type === 'group_joined') {
    return `Te uniste a ${event.payload?.group_name || 'un grupo'}`
  }
  if (event.event_type === 'prediction_submitted') {
    return `Predijiste ${event.payload?.home_score}-${event.payload?.away_score} para un partido`
  }
  return 'Actividad desconocida'
}

function formatRelativeTime(isoDate: string): string {
  const date = new Date(isoDate)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Hace un momento'
  if (diffMins < 60) return `Hace ${diffMins} minutos`
  if (diffHours < 24) return `Hace ${diffHours} horas`
  if (diffDays < 7) return `Hace ${diffDays} días`
  return date.toLocaleDateString('es-AR')
}
</script>
```

---

## 3. Match Distribution Modal

### MatchDistributionModal.vue

```vue
<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
    <div class="bg-surface rounded-xl p-6 max-w-md w-full space-y-4">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h3 class="font-headline-sm text-headline-sm text-primary">Distribución de Predicciones</h3>
        <button @click="close" class="text-on-surface-variant hover:text-on-surface">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <!-- Match Info -->
      <div v-if="match" class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <img v-if="match.home_team.flag_url" :src="match.home_team.flag_url" class="w-8 h-6 rounded" />
          <span class="font-body-md font-medium">{{ match.home_team.name }}</span>
        </div>
        <span class="font-label-md text-on-surface-variant">VS</span>
        <div class="flex items-center gap-2">
          <span class="font-body-md font-medium">{{ match.away_team.name }}</span>
          <img v-if="match.away_team.flag_url" :src="match.away_team.flag_url" class="w-8 h-6 rounded" />
        </div>
      </div>
      
      <!-- Loading -->
      <div v-if="isLoading" class="h-32 bg-surface-container animate-pulse rounded-lg"></div>
      
      <!-- Pre-deadline -->
      <div v-else-if="distribution && !distribution.available" class="text-center py-6">
        <p class="font-body-md text-on-surface-variant">
          Las predicciones se mostrarán después del cierre
        </p>
        <p class="font-label-sm text-on-surface-variant mt-1">
          Cierre: {{ formatDate(match?.deadline_utc) }}
        </p>
      </div>
      
      <!-- Distribution -->
      <div v-else-if="distribution && distribution.available" class="space-y-4">
        <p class="font-label-md text-on-surface-variant text-center">
          {{ distribution.total_predictions }} predicciones
        </p>
        
        <!-- Home Win -->
        <div class="space-y-1">
          <div class="flex justify-between font-body-md">
            <span>Victoria {{ match?.home_team.name }}</span>
            <span class="font-bold">{{ distribution.home_win_pct }}%</span>
          </div>
          <div class="h-4 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-primary transition-all" :style="{ width: distribution.home_win_pct + '%' }"></div>
          </div>
        </div>
        
        <!-- Draw -->
        <div class="space-y-1">
          <div class="flex justify-between font-body-md">
            <span>Empate</span>
            <span class="font-bold">{{ distribution.draw_pct }}%</span>
          </div>
          <div class="h-4 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-secondary transition-all" :style="{ width: distribution.draw_pct + '%' }"></div>
          </div>
        </div>
        
        <!-- Away Win -->
        <div class="space-y-1">
          <div class="flex justify-between font-body-md">
            <span>Victoria {{ match?.away_team.name }}</span>
            <span class="font-bold">{{ distribution.away_win_pct }}%</span>
          </div>
          <div class="h-4 bg-surface-container rounded-full overflow-hidden">
            <div class="h-full bg-tertiary transition-all" :style="{ width: distribution.away_win_pct + '%' }"></div>
          </div>
        </div>
      </div>
      
      <!-- Error -->
      <div v-else-if="error" class="text-error font-body-md text-center">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { apiClient } from '@/lib/api'

interface Distribution {
  available: boolean
  match_id: number
  home_win_pct: number
  draw_pct: number
  away_win_pct: number
  total_predictions: number
  reason?: string
}

const props = defineProps<{
  isOpen: boolean
  matchId: number | null
  match: any
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const distribution = ref<Distribution | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

watch(() => props.isOpen, async (open) => {
  if (open && props.matchId) {
    await loadDistribution(props.matchId)
  }
})

async function loadDistribution(matchId: number) {
  isLoading.value = true
  error.value = null
  try {
    const response = await apiClient.get(`/api/matches/${matchId}/distribution`)
    distribution.value = response.data
  } catch (err: any) {
    error.value = err.message || 'Error al cargar distribución'
  } finally {
    isLoading.value = false
  }
}

function close() {
  distribution.value = null
  error.value = null
  emit('close')
}

function formatDate(isoDate: string | undefined): string {
  if (!isoDate) return ''
  return new Date(isoDate).toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
```

---

## 4. Dashboard Layout

### DashboardView.vue Changes

```vue
<template>
  <AppLayout>
    <div class="px-5 py-6 max-w-7xl mx-auto space-y-6">
      <!-- Header Section -->
      <section class="space-y-4">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 class="font-headline-lg text-headline-lg text-primary mb-1">Dashboard</h1>
            <p class="font-body-lg text-body-lg text-on-surface-variant">
              Bienvenido, {{ authStore.user?.name }}! Gestiona tus grupos y seguí tu rendimiento.
            </p>
          </div>
          <div class="flex gap-2">
            <button @click="showCreateGroupDialog = true" class="...">Crear Grupo</button>
            <button @click="showJoinGroupDialog = true" class="...">Unirse a Grupo</button>
          </div>
        </div>
      </section>

      <!-- Widgets Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Upcoming Matches -->
        <UpcomingMatchesWidget @open-distribution="openDistribution" />
        
        <!-- My Standing -->
        <MyStandingWidget />
      </div>
      
      <!-- Activity Feed -->
      <div class="lg:grid-cols-1">
        <ActivityFeedWidget />
      </div>

      <!-- Groups Section (existing) -->
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

      <!-- Empty State (existing) -->
      <section v-else class="...">
        <!-- ... -->
      </section>

      <!-- Dialogs (existing) -->
      <!-- ... -->
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
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useGroupsStore } from '@/stores/groups'
import { useMatchesStore } from '@/stores/matches'
import AppLayout from '@/components/AppLayout.vue'
import GroupCard from '@/components/GroupCard.vue'
import UpcomingMatchesWidget from '@/components/UpcomingMatchesWidget.vue'
import MyStandingWidget from '@/components/MyStandingWidget.vue'
import ActivityFeedWidget from '@/components/ActivityFeedWidget.vue'
import MatchDistributionModal from '@/components/MatchDistributionModal.vue'

// ... existing state ...

const matchesStore = useMatchesStore()
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

// ... existing handlers ...
</script>
```

---

## File Changes

| File | Change |
|------|--------|
| `frontend/src/stores/scores.ts` | New store for my-standing |
| `frontend/src/stores/activity.ts` | New store for activity feed |
| `frontend/src/stores/matches.ts` | Add status + limit filters |
| `frontend/src/components/UpcomingMatchesWidget.vue` | New widget |
| `frontend/src/components/MyStandingWidget.vue` | New widget |
| `frontend/src/components/ActivityFeedWidget.vue` | New widget |
| `frontend/src/components/MatchDistributionModal.vue` | New modal |
| `frontend/src/views/DashboardView.vue` | Redesign layout + integrate widgets |

---

## Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Mobile layout overflow | Low | Use responsive grid, test on 375px |
| Too many API calls on mount | Low | Parallel fetch, no blocking |
| Match distribution modal breaks on small screens | Low | Max-width constraints, scrollable content |
| Spanish text hardcoded | Low | Acceptable for MVP; i18n later |

## Design Decisions

1. **Widgets are independent** — Each widget fetches its own data, no shared loading state. If one fails, others work.
2. **Modal over inline** — Distribution is a modal to avoid cluttering the dashboard. Keeps focus on overview.
3. **Skeleton loaders** — Use `animate-pulse` for loading states instead of spinners. Better perceived performance.
4. **Spanish text** — All UI copy in Spanish as established in the project.
