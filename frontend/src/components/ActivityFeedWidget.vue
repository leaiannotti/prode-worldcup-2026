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

    <!-- List: first 3 visible, rest scrollable -->
    <div v-else>
      <div class="space-y-2 overflow-y-auto" :class="activityStore.events.length > 3 ? 'max-h-[280px] pr-1' : ''">
        <div
          v-for="event in activityStore.events"
          :key="event.id"
          class="flex items-start gap-3 p-3 rounded-lg"
          :class="eventStyle(event.event_type).rowClass"
        >
          <!-- Icon -->
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
            :class="eventStyle(event.event_type).iconBg"
          >
            <!-- prediction_submitted -->
            <svg v-if="event.event_type === 'prediction_submitted'" class="w-4 h-4" :class="eventStyle(event.event_type).iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <!-- prediction_updated -->
            <svg v-else-if="event.event_type === 'prediction_updated'" class="w-4 h-4" :class="eventStyle(event.event_type).iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            <!-- score_calculated -->
            <svg v-else-if="event.event_type === 'score_calculated'" class="w-4 h-4" :class="eventStyle(event.event_type).iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
            <!-- group_created -->
            <svg v-else-if="event.event_type === 'group_created'" class="w-4 h-4" :class="eventStyle(event.event_type).iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            <!-- group_joined -->
            <svg v-else class="w-4 h-4" :class="eventStyle(event.event_type).iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>

          <!-- Text -->
          <div class="flex-1 min-w-0">
            <p class="text-sm text-on-surface leading-snug">{{ eventText(event) }}</p>
            <p class="text-[11px] text-on-surface-variant mt-0.5">{{ formatRelativeTime(event.occurred_at) }}</p>
          </div>

          <!-- Points badge for score_calculated -->
          <div v-if="event.event_type === 'score_calculated'" class="flex-shrink-0">
            <span
              class="text-xs font-bold tabular-nums px-2 py-0.5 rounded-full"
              :class="pointsBadge(event.payload?.points)"
            >
              +{{ event.payload?.points }}pts
            </span>
          </div>
        </div>
      </div>

      <!-- Scroll hint -->
      <p v-if="activityStore.events.length > 3" class="text-[10px] text-on-surface-variant/50 text-center mt-2">
        {{ activityStore.events.length - 3 }} más arriba
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useActivityStore } from '@/stores/activity'
import { formatRelativeTime } from '@/composables/useDateFormat'

const activityStore = useActivityStore()

onMounted(() => {
  activityStore.fetchActivity(10)
})

function eventStyle(type: string) {
  switch (type) {
    case 'prediction_submitted':
      return {
        rowClass: 'bg-primary-container/30',
        iconBg: 'bg-primary-container',
        iconColor: 'text-on-primary-container',
      }
    case 'prediction_updated':
      return {
        rowClass: 'bg-secondary-container/30',
        iconBg: 'bg-secondary-container',
        iconColor: 'text-on-secondary-container',
      }
    case 'score_calculated':
      return {
        rowClass: 'bg-tertiary-container/30',
        iconBg: 'bg-tertiary-container',
        iconColor: 'text-on-tertiary-container',
      }
    case 'group_created':
      return {
        rowClass: 'bg-secondary-container/30',
        iconBg: 'bg-secondary-container',
        iconColor: 'text-on-secondary-container',
      }
    case 'group_joined':
      return {
        rowClass: 'bg-secondary-container/30',
        iconBg: 'bg-secondary-container',
        iconColor: 'text-on-secondary-container',
      }
    default:
      return {
        rowClass: 'bg-surface-container-low',
        iconBg: 'bg-surface-container',
        iconColor: 'text-on-surface-variant',
      }
  }
}

function eventText(event: any): string {
  const p = event.payload || {}

  switch (event.event_type) {
    case 'prediction_submitted': {
      const match = p.home_team && p.away_team ? `${p.home_team} vs ${p.away_team}` : 'un partido'
      return `Predijiste ${p.home_score}-${p.away_score} en ${match}`
    }
    case 'prediction_updated': {
      const match = p.home_team && p.away_team ? `${p.home_team} vs ${p.away_team}` : 'un partido'
      return `Actualizaste tu predicción a ${p.home_score}-${p.away_score} en ${match}`
    }
    case 'score_calculated': {
      const match = p.home_team && p.away_team
        ? `${p.home_team} vs ${p.away_team}`
        : 'un partido'
      const typeLabel = p.score_type === 'exact'
        ? 'marcador exacto'
        : p.score_type === 'outcome'
        ? 'resultado correcto'
        : 'sin puntos'
      return `Acumulaste ${p.points} pt${p.points !== 1 ? 's' : ''} en ${match} — ${typeLabel}`
    }
    case 'group_created':
      return `Creaste la liga "${p.group_name || 'nueva'}"`
    case 'group_joined':
      return `Te uniste a la liga "${p.group_name || 'una liga'}"`
    default:
      return 'Actividad desconocida'
  }
}

function pointsBadge(points: number | undefined): string {
  if (points === 3) return 'bg-tertiary text-on-tertiary'
  if (points === 1) return 'bg-secondary text-on-secondary'
  return 'bg-surface-container text-on-surface-variant'
}


</script>
