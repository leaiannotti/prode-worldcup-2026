import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/groups/:id',
    name: 'GroupDetail',
    component: () => import('../views/GroupDetailView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/groups/:id/leaderboard',
    name: 'Leaderboard',
    component: () => import('../views/LeaderboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/matches',
    name: 'Matches',
    component: () => import('../views/MatchesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/predictions',
    name: 'Predictions',
    component: () => import('../views/PredictionsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/grupos',
    name: 'Grupos',
    component: () => import('../views/GruposView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Route guard for auth check
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth) {
    // Check if user is authenticated by fetching /api/auth/me
    if (!authStore.isAuthenticated) {
      const isAuthenticated = await authStore.fetchMe()
      if (!isAuthenticated) {
        // Not authenticated, redirect to login
        next({ name: 'Login' })
        return
      }
    }
  }

  next()
})

export default router
