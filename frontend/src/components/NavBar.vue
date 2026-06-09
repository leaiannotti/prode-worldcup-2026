<template>
  <!-- Top bar -->
  <header class="fixed top-0 z-50 w-full bg-surface shadow-sm h-16 border-b border-outline-variant">
    <div class="flex justify-between items-center w-full px-4 h-full max-w-7xl mx-auto">

      <!-- Logo + Desktop Nav -->
      <div class="flex items-center gap-2">
        <RouterLink to="/dashboard" class="flex items-center gap-2">
          <svg class="w-6 h-6 text-primary flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 2c1.29 0 2.52.27 3.64.75L12 8.5 8.36 4.75C9.48 4.27 10.71 4 12 4zm-5.3 1.93l3.8 3.8-1.86 5.72-5.4 1.74C3.09 16.14 3 15.08 3 14c0-3.26 1.67-6.14 4.2-7.87zM4.57 18.5l5.12-1.65 3.54 3.54C12.82 20.46 12.41 21 12 21c-2.97 0-5.61-1.3-7.43-3.5zm9.76 2.88l-3.54-3.54 1.86-5.72 5.4-1.74C18.91 11.86 19 12.92 19 14c0 3.26-1.67 6.14-4.2 7.87l-.47-.49zm1.96-14.45L12 10.5l-3.8-3.8C9.26 5.63 10.59 5 12 5s2.74.63 3.8 1.7l.49-.77z"/>
          </svg>
          <span class="font-display-lg text-headline-lg font-black text-primary uppercase tracking-tighter hidden sm:block">
            PRODE 2026
          </span>
        </RouterLink>

        <nav class="hidden md:flex gap-1 ml-4">
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            class="px-3 py-1.5 rounded-lg text-sm font-medium text-on-surface-variant hover:text-primary hover:bg-surface-container transition-all"
            active-class="text-primary bg-primary-container/30"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
      </div>

      <!-- Right section -->
      <div class="flex items-center gap-1">

        <!-- Points badge -->
        <button
          v-if="authStore.user && totalPoints !== null"
          @click="pointsDrawerOpen = true"
          class="hidden sm:flex items-center gap-1.5 bg-primary text-on-primary px-3 py-1.5 rounded-full text-xs font-bold hover:opacity-90 transition-all active:scale-95 cursor-pointer"
        >
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
          <span class="tabular-nums">{{ totalPoints }} pts</span>
        </button>

        <!-- Dark mode toggle -->
        <button
          @click="themeStore.toggle()"
          class="p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors cursor-pointer"
          :title="themeStore.isDark ? t('nav.lightMode') : t('nav.darkMode')"
        >
          <!-- Sun (show in dark mode to switch to light) -->
          <svg v-if="themeStore.isDark" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 6.343l-.707-.707m12.728 12.728l-.707-.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <!-- Moon (show in light mode to switch to dark) -->
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
          </svg>
        </button>

        <!-- Notifications -->
        <div class="relative" ref="notifRef">
          <button
            @click="toggleNotif"
            class="relative p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors cursor-pointer"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span v-if="activityStore.events.length > 0" class="absolute top-1.5 right-1.5 w-2 h-2 bg-error rounded-full"></span>
          </button>

          <!-- Activity dropdown -->
          <Transition name="dropdown">
            <div
              v-if="notifOpen"
              class="absolute right-0 top-full mt-2 w-[min(320px,calc(100vw-2rem))] bg-surface rounded-xl border border-outline-variant shadow-lg overflow-hidden z-50"
            >
              <div class="px-4 py-3 border-b border-outline-variant flex items-center justify-between">
                <p class="text-sm font-semibold text-on-surface">{{ t('nav.recentActivity') }}</p>
                <button @click="notifOpen = false" class="text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <div v-if="activityStore.isLoading" class="p-4 space-y-2">
                <div v-for="i in 3" :key="i" class="h-10 bg-surface-container animate-pulse rounded-lg"></div>
              </div>

              <div v-else-if="activityStore.events.length === 0" class="px-4 py-6 text-center text-sm text-on-surface-variant">
                 {{ t('nav.noActivity') }}
               </div>

              <div v-else class="divide-y divide-outline-variant max-h-72 overflow-y-auto">
                <div
                  v-for="event in activityStore.events.slice(0, 5)"
                  :key="event.id"
                  class="flex items-start gap-3 px-4 py-3"
                >
                  <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5" :class="iconBg(event.event_type)">
                    <svg v-if="event.event_type === 'prediction_submitted' || event.event_type === 'prediction_updated'" class="w-3 h-3" :class="iconColor(event.event_type)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                    <svg v-else-if="event.event_type === 'score_calculated'" class="w-3 h-3" :class="iconColor(event.event_type)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                    <svg v-else class="w-3 h-3" :class="iconColor(event.event_type)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs text-on-surface leading-snug">{{ eventText(event) }}</p>
                    <p class="text-[10px] text-on-surface-variant mt-0.5">{{ formatRelativeTime(event.occurred_at) }}</p>
                  </div>
                  <span v-if="event.event_type === 'score_calculated'"
                    class="flex-shrink-0 text-[10px] font-bold px-1.5 py-0.5 rounded-full tabular-nums"
                    :class="event.payload?.points === 3 ? 'bg-tertiary-container text-on-tertiary-container' : event.payload?.points === 1 ? 'bg-secondary-container text-on-secondary-container' : 'bg-surface-container text-on-surface-variant'"
                  >+{{ event.payload?.points }}pts</span>
                </div>
              </div>
            </div>
          </Transition>
        </div>

        <!-- Language toggle -->
        <button
          @click="switchLocale"
          class="hidden sm:flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-bold text-on-surface-variant hover:bg-surface-container transition-colors cursor-pointer"
          :title="locale === 'es' ? 'Switch to English' : 'Cambiar a Español'"
        >
          {{ locale === 'es' ? 'EN' : 'ES' }}
        </button>

        <!-- Avatar -->
        <div v-if="authStore.user" class="w-8 h-8 rounded-full overflow-hidden border-2 border-primary flex-shrink-0">
          <img
            v-if="authStore.user.picture && !avatarError"
            :src="authStore.user.picture"
            :alt="authStore.user.name"
            class="w-full h-full object-cover"
            @error="avatarError = true"
          />
          <div v-else class="w-full h-full bg-primary flex items-center justify-center">
            <span class="text-on-primary text-[10px] font-bold">{{ initials(authStore.user.name) }}</span>
          </div>
        </div>

        <!-- Logout (desktop only) -->
        <button
          @click="handleLogout"
          class="hidden md:flex p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors cursor-pointer"
          :title="t('nav.logoutFull')"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
        </button>
      </div>
    </div>
  </header>

  <!-- Bottom navigation — mobile only -->
  <nav class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface border-t border-outline-variant pb-safe">
    <div class="flex items-stretch h-16">
      <RouterLink
        v-for="link in navLinks"
        :key="link.to"
        :to="link.to"
        class="flex-1 flex flex-col items-center justify-center gap-0.5 text-on-surface-variant transition-colors"
        active-class="text-primary"
      >
        <!-- Dashboard icon -->
        <svg v-if="link.to === '/dashboard'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <!-- Partidos icon -->
        <svg v-else-if="link.to === '/matches'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <!-- Ligas icon -->
        <svg v-else-if="link.to === '/grupos'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span class="text-[10px] font-medium">{{ link.label }}</span>
      </RouterLink>

      <!-- Logout on mobile bottom nav -->
      <button
        @click="handleLogout"
        class="flex-1 flex flex-col items-center justify-center gap-0.5 text-on-surface-variant transition-colors cursor-pointer"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span class="text-[10px] font-medium">{{ t('nav.logout') }}</span>
      </button>
    </div>
  </nav>

  <!-- Points Drawer -->
  <PointsDrawer
    :is-open="pointsDrawerOpen"
    :total-points="totalPoints"
    @close="pointsDrawerOpen = false"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useScoresStore } from '@/stores/scores'
import { useActivityStore } from '@/stores/activity'
import { useThemeStore } from '@/stores/theme'
import PointsDrawer from '@/components/PointsDrawer.vue'
import { formatRelativeTime } from '@/composables/useDateFormat'
import { useI18n } from 'vue-i18n'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()

const authStore = useAuthStore()
const scoresStore = useScoresStore()
const activityStore = useActivityStore()
const themeStore = useThemeStore()
const router = useRouter()

const navLinks = computed(() => [
  { to: '/dashboard', label: t('nav.dashboard') },
  { to: '/matches', label: t('nav.matches') },
  { to: '/grupos', label: t('nav.leagues') },
])

function switchLocale() {
  const next = locale.value === 'es' ? 'en' : 'es'
  setLocale(next as 'es' | 'en')
}

const notifOpen = ref(false)
const notifRef = ref<HTMLElement | null>(null)
const pointsDrawerOpen = ref(false)
const avatarError = ref(false)

function initials(name: string): string {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}

const totalPoints = computed(() => scoresStore.myTotalPoints)

onMounted(async () => {
  await Promise.all([
    scoresStore.fetchMyTotal(),
    activityStore.fetchActivity(10),
  ])
  document.addEventListener('click', onClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})

function toggleNotif() {
  notifOpen.value = !notifOpen.value
}

function onClickOutside(e: MouseEvent) {
  if (notifRef.value && !notifRef.value.contains(e.target as Node)) {
    notifOpen.value = false
  }
}

function iconBg(type: string): string {
  if (type === 'prediction_submitted' || type === 'prediction_updated') return 'bg-primary-container'
  if (type === 'score_calculated') return 'bg-tertiary-container'
  return 'bg-secondary-container'
}

function iconColor(type: string): string {
  if (type === 'prediction_submitted' || type === 'prediction_updated') return 'text-on-primary-container'
  if (type === 'score_calculated') return 'text-on-tertiary-container'
  return 'text-on-secondary-container'
}

function eventText(event: any): string {
  const p = event.payload || {}
  const match = p.home_team && p.away_team ? `${p.home_team} vs ${p.away_team}` : t('activity.aMatch')
  switch (event.event_type) {
    case 'prediction_submitted':
      return t('activity.predictionSubmitted', { score: `${p.home_score}-${p.away_score}`, match })
    case 'prediction_updated':
      return t('activity.predictionUpdated', { score: `${p.home_score}-${p.away_score}`, match })
    case 'score_calculated': {
      const plural = p.points !== 1 ? 's' : ''
      return t('activity.scoreCalculated', { points: p.points, plural, match, type: '' }).replace(' — ', '')
    }
    case 'group_created': return t('activity.groupCreated', { name: p.group_name || t('activity.aLeague') })
    case 'group_joined': return t('activity.groupJoined', { name: p.group_name || t('activity.aLeague') })
    default: return t('activity.unknown')
  }
}

async function handleLogout() {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Safe area for notch phones */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>
