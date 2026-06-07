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
