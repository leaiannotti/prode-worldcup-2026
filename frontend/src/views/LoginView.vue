<template>
  <div class="fixed inset-0 z-0 overflow-hidden">
    <!-- Background Image -->
    <img
      alt="Stadium background"
      src="https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=1280&h=720&fit=crop"
      class="w-full h-full object-cover"
    />
    <!-- Stadium Overlay -->
    <div class="absolute inset-0 bg-gradient-to-b from-primary/50 to-primary-container/85" />
  </div>

  <!-- Main Content -->
  <main class="relative z-10 flex-1 flex flex-col items-center justify-center px-gutter min-h-screen">
    <!-- Branding -->
    <header class="mb-xl text-center">
      <h1 class="font-display-lg text-display-lg text-primary-fixed-dim drop-shadow-2xl uppercase italic tracking-tighter">
        PRODE 2026
      </h1>
    </header>

    <!-- Login Card -->
    <section class="w-full max-w-md rounded-lg p-lg shadow-2xl bg-white/95 backdrop-blur-sm border border-white/40 overflow-hidden relative">
      <!-- Accent Borders (Argentina flag blue) -->
      <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary to-secondary" />

      <!-- Card Content -->
      <div class="space-y-md">
        <!-- Heading -->
        <div class="text-center">
          <h2 class="font-display-lg text-headline-lg text-primary mb-xs">
            Comienza tu camino a la gloria
          </h2>
          <p class="font-body-md text-body-md text-on-surface-variant">
            Únete a la mayor competencia de predicciones del mundo.
          </p>
        </div>

        <!-- Login Actions -->
        <div class="space-y-md">
          <!-- Google OAuth Button -->
          <a
            href="/api/auth/login"
            class="w-full flex items-center justify-center gap-sm bg-white border border-outline-variant py-md px-md rounded-lg text-on-surface font-title-md hover:bg-surface-container transition-all active:scale-95 duration-150"
          >
            <svg class="w-5 h-5" viewBox="0 0 24 24">
              <image
                href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%234285F4' d='M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z'/%3E%3Cpath fill='%2334A853' d='M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z'/%3E%3Cpath fill='%23FBBC05' d='M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z'/%3E%3Cpath fill='%23EA4335' d='M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z'/%3E%3C/svg%3E"
                alt="Google"
              />
            </svg>
            Sign in with Google
          </a>

          <!-- Divider -->
          <div class="flex items-center gap-sm my-md">
            <div class="h-px flex-1 bg-outline-variant" />
            <span class="text-on-surface-variant font-label-sm text-xs uppercase tracking-widest">or continue with</span>
            <div class="h-px flex-1 bg-outline-variant" />
          </div>

          <!-- Alternative Methods -->
          <div class="grid grid-cols-2 gap-md">
            <button class="flex items-center justify-center gap-xs py-md border border-outline-variant rounded-lg font-title-md text-on-surface hover:bg-surface-container transition-all active:scale-95">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              Email
            </button>
            <button class="flex items-center justify-center gap-xs py-md border border-outline-variant rounded-lg font-title-md text-on-surface hover:bg-surface-container transition-all active:scale-95">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.05 13.5c-.91 0-1.82.33-2.5 1a5.98 5.98 0 000 8.48c1.45 1.45 3.8 1.45 5.25 0 1.45-1.45 1.45-3.8 0-5.25-.68-.67-1.59-1-2.5-1zm0 8c-.9 0-1.8-.32-2.5-1a3.5 3.5 0 010-4.95c.7-.68 1.6-1 2.5-1s1.8.32 2.5 1a3.5 3.5 0 010 4.95c-.7.68-1.6 1-2.5 1zM3.5 1h2l.54 1.32c.6 1.44 1.76 2.67 3.16 3.38.8.4 1.6.6 2.5.6s1.7-.2 2.5-.6c1.4-.71 2.56-1.94 3.16-3.38L16.44 1h2l-1 2.4C16.78 5.76 15 8.1 12.46 9.46c.46.7.72 1.52.72 2.4 0 2.66-2.16 4.82-4.82 4.82S3.54 14.52 3.54 11.86c0-.88.26-1.7.72-2.4C1.72 8.1 0 5.76 0 3.4L-1.5 1zm8.96 16.5c0-.43.35-.78.78-.78.43 0 .78.35.78.78 0 .43-.35.78-.78.78-.43 0-.78-.35-.78-.78z" />
              </svg>
              Apple
            </button>
          </div>
        </div>

        <!-- Language Selector -->
        <div class="flex items-center gap-sm py-xs px-md bg-surface-container-low rounded-lg border border-outline-variant">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h.5A2.5 2.5 0 0016 5.5V3.935m0 2m-2 5m0 0a2 2 0 012-2h.5A2.5 2.5 0 0121 7.5v.5" />
          </svg>
          <select class="bg-transparent border-none focus:ring-0 text-on-surface-variant font-body-md py-0 pr-lg cursor-pointer outline-none">
            <option selected="" value="es">Español (ES)</option>
            <option value="en">English (US)</option>
            <option value="pt">Português (BR)</option>
          </select>
        </div>
      </div>

      <!-- Accent Border (New Zealand flag red) -->
      <div class="absolute bottom-0 left-0 right-0 h-1 bg-red-600" />
    </section>

    <!-- Footer -->
    <footer class="mt-xl text-white/80 font-label-sm text-center">
      <p>© 2026 Prode World Cup Platform. All rights reserved.</p>
      <div class="flex gap-md mt-sm justify-center">
        <a class="hover:text-primary-fixed-dim transition-colors underline" href="#">Rules</a>
        <a class="hover:text-primary-fixed-dim transition-colors underline" href="#">Privacy</a>
        <a class="hover:text-primary-fixed-dim transition-colors underline" href="#">Support</a>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
// LoginView component for Google OAuth
// User is redirected here from /api/auth/login
// On OAuth callback, sets JWT cookie and redirects to dashboard
</script>

<style scoped>
/* Component uses Tailwind utility classes only */
</style>
