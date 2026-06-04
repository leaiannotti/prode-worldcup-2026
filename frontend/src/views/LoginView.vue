<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
      <h1 class="text-3xl font-bold text-center text-gray-900 mb-2">
        Prode World Cup 2026
      </h1>
      <p class="text-center text-gray-600 mb-8">
        Predict scores and compete with your friends
      </p>

      <div class="space-y-4">
        <!-- Google OAuth button -->
        <a
          href="/api/auth/login"
          class="
            w-full flex items-center justify-center gap-3
            bg-white border border-gray-300 rounded-lg px-4 py-3
            font-semibold text-gray-700 hover:bg-gray-50
            transition-colors
          "
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <image
              href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234285F4' d='M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z'/%3E%3Cpath fill='%2334A853' d='M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z'/%3E%3Cpath fill='%23FBBC05' d='M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z'/%3E%3Cpath fill='%23EA4335' d='M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z'/%3E%3C/svg%3E"
              alt="Google"
            />
          </svg>
          Sign in with Google
        </a>
      </div>

      <p class="text-center text-gray-500 text-sm mt-8">
        By signing in, you agree to our Terms of Service and Privacy Policy
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
// LoginView component for Google OAuth
// User is redirected here from /api/auth/login
// On OAuth callback, sets JWT cookie and redirects to dashboard
</script>
