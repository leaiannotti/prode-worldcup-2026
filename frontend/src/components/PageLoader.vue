<template>
  <Transition name="loader">
    <div
      v-if="show"
      class="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
      style="background: rgba(255,255,255,0.15); backdrop-filter: blur(18px);"
    >
      <div class="relative flex flex-col items-center gap-5">
        <!-- Messi image with bounce animation -->
        <div class="loader-bounce">
          <img
            src="/messi-copa.png"
            :alt="t('common.loadingImage')"
            class="w-64 h-64 object-contain drop-shadow-2xl"
          />
        </div>

        <!-- Mensaje aleatorio -->
        <Transition name="msg" mode="out-in">
          <p
            :key="currentMessage"
            class="text-center px-8"
            style="
              font-family: 'Bebas Neue', sans-serif;
              font-size: clamp(1.6rem, 5vw, 2.4rem);
              color: #00134d;
              letter-spacing: 0.03em;
              line-height: 1.1;
            "
          >
            {{ currentMessage }}
          </p>
        </Transition>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps<{ show: boolean }>()

const messages = [
  'Besando la copa...',
  'Llevando para allá al bobo...',
  'Ganándole de vuelta a los mexicanos...',
  'Siendo comido por el Dibu...',
  'Poniéndose el manto sagrado...',
  'Haciendo llorar a Mbappé...',
  'Dedicándosela al Diego...',
  'Saltando en el vestuario...',
  'Volviendo a Qatar mentalmente...',
  'Escuchando MUCHAAAAACHOS...',
  'Abrazando a la Scaloneta...',
]

const currentMessage = ref('')

function pickRandom() {
  const pool = messages.filter(m => m !== currentMessage.value)
  currentMessage.value = pool[Math.floor(Math.random() * pool.length)]
}

let interval: ReturnType<typeof setInterval> | null = null

watch(() => props.show, (val) => {
  if (val) {
    pickRandom()
    interval = setInterval(pickRandom, 1800)
  } else {
    if (interval) clearInterval(interval)
  }
})
</script>

<style scoped>
.msg-enter-active,
.msg-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.msg-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.msg-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.loader-bounce {
  animation: bounce 0.8s ease-in-out infinite alternate;
}

@keyframes bounce {
  from { transform: translateY(0px); }
  to   { transform: translateY(-16px); }
}


.loader-enter-active,
.loader-leave-active {
  transition: opacity 0.25s ease;
}
.loader-enter-from,
.loader-leave-to {
  opacity: 0;
}
</style>
