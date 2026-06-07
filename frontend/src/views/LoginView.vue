<template>
  <!-- Hero Background -->
  <div class="fixed inset-0 z-0">
    <img
      ref="bgImage"
      alt="Stadium background"
      src="https://lh3.googleusercontent.com/aida-public/AB6AXuAGS5lRhcrh11DY4xaqzDoCVzGSYBPUe1vBPth__RSeBe9wwUnXNoWiHZW4G6AdKW05KfViI48aUYC_2vRFjJIs8qQJlZ8Spbee475vLCybNN8aBhb0TnxFOb3Wrc2IJBTnN6FvC3dwxQxm8hI9Io4LCuKIWhmlskbR1fOQJJ-FjyqPbhXYI8U0sHEZMeqYPkmx6Zh-H68NFZvUSO_Xl951SBA0Q7VvDDQgIpdgYh9O9mIXer6ltg_7YeUnyIJ9Kc54PBIClT--GvcZ"
      class="w-full h-full object-cover scale-105"
    />
    <div class="absolute inset-0 stadium-overlay" />
  </div>

  <!-- Main Content -->
  <main class="relative z-10 flex-1 flex flex-col items-center justify-center px-5 min-h-screen">
    <!-- Branding -->
    <header class="mb-10 text-center">
      <h1 class="font-display-lg text-display-lg text-primary-fixed-dim drop-shadow-2xl uppercase italic tracking-tighter">
        PRODE 2026
      </h1>
    </header>

    <!-- Login Card -->
    <section
      ref="cardRef"
      class="w-full max-w-md glass-card rounded-lg px-8 py-10 shadow-2xl flex flex-col items-center relative overflow-hidden flag-accent-top opacity-0 translate-y-4"
    >
      <!-- Flag accent bottom (NZ red) -->
      <div class="absolute bottom-0 left-0 right-0 h-1 bg-[#CC142D]" />

      <!-- Heading -->
      <div class="mb-6 text-center">
        <h2 class="font-display-lg text-headline-lg text-primary mb-2">
          Comienza tu camino a la gloria
        </h2>
        <p class="font-body-md text-body-md text-on-surface-variant">
          Únete a la mayor competencia de predicciones del mundo.
        </p>
      </div>

      <!-- Login Actions -->
      <div class="w-full space-y-6 mt-2">
        <!-- Google OAuth Button -->
        <a
          href="/api/auth/login"
          class="w-full flex items-center justify-center gap-3 bg-white border border-outline-variant py-4 px-6 rounded-xl text-on-surface font-title-md text-base hover:bg-surface-container transition-all active:scale-95 duration-150"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Iniciar sesión con Google
        </a>

        <!-- Divider -->
        <div class="flex items-center gap-3 my-2">
          <div class="h-px flex-1 bg-outline-variant" />
          <span class="text-on-surface-variant font-label-sm text-xs uppercase tracking-widest">o accede con</span>
          <div class="h-px flex-1 bg-outline-variant" />
        </div>

        <!-- Alternative Methods -->
        <div class="grid grid-cols-2 gap-4">
          <button class="flex items-center justify-center gap-2 py-4 border border-outline-variant rounded-xl font-title-md text-base text-on-surface hover:bg-surface-container transition-all active:scale-95">
            <svg class="w-5 h-5 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Email
          </button>
          <button class="flex items-center justify-center gap-2 py-4 border border-outline-variant rounded-xl font-title-md text-base text-on-surface hover:bg-surface-container transition-all active:scale-95">
            <svg class="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 24 24">
              <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
            </svg>
            Apple
          </button>
        </div>
      </div>

      <!-- Language Selector -->
      <div class="mt-8 relative">
        <button
          type="button"
          class="flex items-center gap-2 py-2.5 px-5 bg-surface-container-low rounded-lg border border-outline-variant text-on-surface-variant font-body-md hover:bg-surface-container transition-all"
          @click="langOpen = !langOpen"
        >
          <svg class="w-5 h-5 text-primary shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
          </svg>
          <span class="flex-1 text-left">{{ currentLangLabel }}</span>
          <svg
            class="w-4 h-4 shrink-0 transition-transform duration-150"
            :class="langOpen ? 'rotate-180' : ''"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Dropdown panel -->
        <div
          v-if="langOpen"
          class="absolute bottom-full mb-1 left-0 right-0 bg-surface-container-lowest border border-outline-variant rounded-lg shadow-lg overflow-hidden z-20"
        >
          <button
            v-for="opt in langOptions"
            :key="opt.value"
            type="button"
            class="w-full text-left px-4 py-2.5 font-body-md text-on-surface hover:bg-surface-container transition-colors"
            :class="selectedLang === opt.value ? 'text-primary font-label-md bg-surface-container-low' : ''"
            @click="selectLang(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="mt-10 text-white/80 font-label-sm text-center">
      <p>© 2026 Prode World Cup Platform. Todos los derechos reservados.</p>
      <div class="flex gap-4 mt-2 justify-center">
        <a class="hover:text-primary-fixed transition-colors underline decoration-secondary" href="#">Reglas</a>
        <a class="hover:text-primary-fixed transition-colors underline decoration-secondary" href="#">Privacidad</a>
        <a class="hover:text-primary-fixed transition-colors underline decoration-secondary" href="#">Soporte</a>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const langOptions = [
  { value: 'es', label: 'Español (ES)' },
  { value: 'en', label: 'English (US)' },
  { value: 'pt', label: 'Português (BR)' },
]

const selectedLang = ref('es')
const langOpen = ref(false)
const cardRef = ref<HTMLElement | null>(null)
const bgImage = ref<HTMLImageElement | null>(null)

const currentLangLabel = computed(
  () => langOptions.find((o) => o.value === selectedLang.value)?.label ?? ''
)

function selectLang(value: string) {
  selectedLang.value = value
  langOpen.value = false
}

// Card fade-in animation
onMounted(() => {
  setTimeout(() => {
    if (cardRef.value) {
      cardRef.value.style.transition = 'opacity 1s ease-out, transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)'
      cardRef.value.style.opacity = '1'
      cardRef.value.style.transform = 'translateY(0)'
    }
  }, 150)
})

// Subtle parallax on background
if (typeof window !== 'undefined') {
  window.addEventListener('mousemove', (e) => {
    if (!bgImage.value) return
    const moveX = (e.clientX - window.innerWidth / 2) * 0.005
    const moveY = (e.clientY - window.innerHeight / 2) * 0.005
    bgImage.value.style.transform = `scale(1.05) translate(${moveX}px, ${moveY}px)`
    bgImage.value.style.transition = 'transform 0.2s ease-out'
  })
}
</script>

<style scoped>
.stadium-overlay {
  background: linear-gradient(to bottom, rgba(0, 36, 125, 0.5), rgba(0, 19, 77, 0.85));
}

.glass-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.flag-accent-top {
  border-top: 4px solid #74ACDF;
}
</style>
