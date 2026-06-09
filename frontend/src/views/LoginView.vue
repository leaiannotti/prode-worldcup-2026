<template>
  <!-- Hero Background -->
  <div class="fixed inset-0 z-0">
    <img
      ref="bgImage"
      alt="Stadium background"
      src="/hero-argentina.jpg"
      class="w-full h-full object-cover scale-105"
    />
    <div class="absolute inset-0 stadium-overlay" />
  </div>

  <!-- Main Content -->
  <main class="relative z-10 flex-1 flex flex-col items-center justify-center px-5 min-h-screen">
    <!-- Branding -->
    <header class="mb-10 text-center">
      <h1 class="font-display-lg text-display-lg text-primary-fixed-dim drop-shadow-2xl uppercase tracking-wider">
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
        <h2 class="font-display-lg text-headline-lg mb-2" style="color: #00134d">
            {{ t('login.tagline') }}
          </h2>
          <p class="font-body-md text-body-md" style="color: #444652">
            {{ t('login.subtitle') }}
          </p>
      </div>

      <!-- Login Actions -->
      <div class="w-full space-y-6 mt-2">
        <!-- Google OAuth Button -->
        <a
          href="/api/auth/login"
          class="w-full flex items-center justify-center gap-3 bg-white border border-gray-200 py-4 px-6 rounded-xl font-title-md text-base transition-all active:scale-95 duration-150 group"
          style="color: #191c1d; box-shadow: 0 1px 3px rgba(0,0,0,0.08);"
          onmouseover="this.style.boxShadow='0 4px 12px rgba(0,19,77,0.15)'; this.style.borderColor='#b7c4ff'"
          onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.08)'; this.style.borderColor='#e5e7eb'"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {{ t('login.withGoogle') }}
        </a>

        <!-- Divider -->
        <div class="flex items-center gap-3 my-2">
          <div class="h-px flex-1 bg-outline-variant" />
          <span class="font-label-sm text-xs uppercase tracking-widest" style="color: #444652">{{ t('login.orWith') }}</span>
          <div class="h-px flex-1 bg-outline-variant" />
        </div>

        <!-- Email form tabs -->
        <div>
          <!-- Tab switcher -->
          <div class="flex rounded-lg overflow-hidden border border-outline-variant mb-4">
            <button
              type="button"
              class="flex-1 py-2 font-label-md text-sm transition-colors"
              :class="emailTab === 'login' ? 'bg-primary text-on-primary' : 'bg-surface text-on-surface-variant hover:bg-surface-container'"
              @click="emailTab = 'login'"
            >{{ t('login.signIn') }}</button>
            <button
              type="button"
              class="flex-1 py-2 font-label-md text-sm transition-colors"
              :class="emailTab === 'register' ? 'bg-primary text-on-primary' : 'bg-surface text-on-surface-variant hover:bg-surface-container'"
              @click="emailTab = 'register'"
            >{{ t('login.signUp') }}</button>
          </div>

          <form class="space-y-3" @submit.prevent="submitEmailForm">
            <!-- Name field (register only) -->
            <input
              v-if="emailTab === 'register'"
              v-model="emailForm.name"
              type="text"
              :placeholder="t('login.namePlaceholder')"
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 font-body-md text-sm outline-none focus:border-primary transition-colors"
              style="color: #191c1d; background: white;"
            />
            <input
              v-model="emailForm.email"
              type="email"
              :placeholder="t('login.emailPlaceholder')"
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 font-body-md text-sm outline-none focus:border-primary transition-colors"
              style="color: #191c1d; background: white;"
            />
            <input
              v-model="emailForm.password"
              type="password"
              :placeholder="t('login.passwordPlaceholder')"
              required
              class="w-full px-4 py-3 rounded-xl border border-gray-200 font-body-md text-sm outline-none focus:border-primary transition-colors"
              style="color: #191c1d; background: white;"
            />

            <p v-if="emailError" class="text-xs font-body-md" style="color: #ba1a1a">{{ emailError }}</p>

            <button
              type="submit"
              :disabled="emailLoading"
              class="w-full py-3 rounded-xl font-label-md text-sm text-white transition-all active:scale-95 disabled:opacity-60"
              style="background: #00134d;"
            >
              {{ emailLoading ? t('login.loading') : (emailTab === 'login' ? t('login.signIn') : t('login.signUp')) }}
            </button>
          </form>
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
            :class="locale === opt.value ? 'text-primary font-label-md bg-surface-container-low' : ''"
            @click="selectLang(opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="mt-10 text-white/80 font-label-sm text-center">
      <p>{{ t('login.footer') }}</p>
      <div class="flex gap-4 mt-2 justify-center">
        <a class="hover:text-primary-fixed transition-colors underline decoration-secondary" href="#">{{ t('login.rules') }}</a>
        <a class="hover:text-primary-fixed transition-colors underline decoration-secondary" href="#">{{ t('login.privacy') }}</a>
        <a class="hover:text-primary-fixed transition-colors underline decoration-secondary" href="#">{{ t('login.support') }}</a>
      </div>
    </footer>
  </main>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { setLocale } from '@/i18n'

const { t, locale } = useI18n()
const router = useRouter()

const langOptions = [
  { value: 'es', label: 'Español (ES)' },
  { value: 'en', label: 'English (US)' },
]

const langOpen = ref(false)
const cardRef = ref<HTMLElement | null>(null)
const bgImage = ref<HTMLImageElement | null>(null)

// Email form state
const emailTab = ref<'login' | 'register'>('login')
const emailLoading = ref(false)
const emailError = ref('')
const emailForm = ref({ name: '', email: '', password: '' })

const errorMessages: Record<string, string> = {
  email_already_registered: 'Ese email ya está registrado.',
  invalid_credentials: 'Email o contraseña incorrectos.',
  invalid_request: 'Datos inválidos. Revisá el formulario.',
}

async function submitEmailForm() {
  emailError.value = ''
  emailLoading.value = true
  try {
    const url = emailTab.value === 'login' ? '/api/auth/login-email' : '/api/auth/register'
    const body: Record<string, string> = {
      email: emailForm.value.email,
      password: emailForm.value.password,
    }
    if (emailTab.value === 'register') body.name = emailForm.value.name

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body),
    })

    if (res.ok) {
      router.push('/dashboard')
    } else {
      const data = await res.json().catch(() => ({}))
      emailError.value = errorMessages[data.error] ?? 'Ocurrió un error. Intentá de nuevo.'
    }
  } catch {
    emailError.value = 'No se pudo conectar. Revisá tu conexión.'
  } finally {
    emailLoading.value = false
  }
}

const currentLangLabel = computed(
  () => langOptions.find((o) => o.value === locale.value)?.label ?? ''
)

function selectLang(value: string) {
  setLocale(value as 'es' | 'en')
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
  background: linear-gradient(to bottom, rgba(0, 53, 128, 0.45), rgba(0, 19, 77, 0.88));
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
