<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen && entries.length > 0"
        class="fixed inset-0 bg-black/50 z-[60] flex items-center justify-center p-4"
        @click.self="handleAcknowledge"
      >
        <div class="bg-surface rounded-2xl w-full max-w-md shadow-2xl overflow-hidden flex flex-col max-h-[85vh]">

          <!-- Header -->
          <div class="px-6 py-5 border-b border-outline-variant flex-shrink-0">
            <div class="flex items-start justify-between gap-3">
              <div>
                <h2 class="font-headline-md text-headline-md text-primary">
                  {{ activeTranslation.title }}
                </h2>
                <p class="text-xs text-on-surface-variant mt-1">
                  {{ t('whatsNew.version', { version: latestEntry.version }) }}
                </p>
              </div>
              <button
                @click="handleAcknowledge"
                class="w-8 h-8 flex items-center justify-center rounded-full hover:bg-surface-container transition-colors text-on-surface-variant flex-shrink-0 cursor-pointer"
                :aria-label="t('whatsNew.close')"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Scrollable body -->
          <div class="px-6 py-5 space-y-6 overflow-y-auto">
            <!-- New features -->
            <section v-if="activeTranslation.new.length > 0">
              <h3 class="flex items-center gap-2 font-label-md text-label-md uppercase tracking-wider text-secondary mb-3">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {{ t('whatsNew.new') }}
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(item, idx) in activeTranslation.new"
                  :key="`new-${idx}`"
                  class="flex gap-2 text-sm text-on-surface leading-relaxed"
                >
                  <span class="text-secondary flex-shrink-0 mt-1">●</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </section>

            <!-- Improvements (optional) -->
            <section v-if="activeTranslation.improved && activeTranslation.improved.length > 0">
              <h3 class="flex items-center gap-2 font-label-md text-label-md uppercase tracking-wider text-tertiary mb-3">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                {{ t('whatsNew.improved') }}
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(item, idx) in activeTranslation.improved"
                  :key="`improved-${idx}`"
                  class="flex gap-2 text-sm text-on-surface leading-relaxed"
                >
                  <span class="text-tertiary flex-shrink-0 mt-1">●</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </section>

            <!-- Bug fixes -->
            <section v-if="activeTranslation.fixed.length > 0">
              <h3 class="flex items-center gap-2 font-label-md text-label-md uppercase tracking-wider text-primary mb-3">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {{ t('whatsNew.fixed') }}
              </h3>
              <ul class="space-y-2">
                <li
                  v-for="(item, idx) in activeTranslation.fixed"
                  :key="`fixed-${idx}`"
                  class="flex gap-2 text-sm text-on-surface leading-relaxed"
                >
                  <span class="text-primary flex-shrink-0 mt-1">●</span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </section>

            <!-- If there are multiple older entries the user hasn't seen, surface
                 a compact summary so they don't feel like older releases were skipped. -->
            <section v-if="entries.length > 1" class="pt-4 border-t border-outline-variant">
              <p class="text-xs text-on-surface-variant mb-2">
                {{ t('whatsNew.previousVersions') }}
              </p>
              <ul class="space-y-1">
                <li
                  v-for="entry in entries.slice(1)"
                  :key="entry.version"
                  class="text-xs text-on-surface-variant"
                >
                  v{{ entry.version }} — {{ entry.translations[currentLocale]?.title || entry.translations.es.title }}
                </li>
              </ul>
            </section>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 border-t border-outline-variant flex-shrink-0">
            <button
              @click="handleAcknowledge"
              class="w-full py-3 bg-primary text-on-primary rounded-xl font-bold text-sm hover:opacity-90 transition-all active:scale-[0.98] cursor-pointer"
            >
              {{ t('whatsNew.acknowledge') }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChangelog } from '@/composables/useChangelog'

const { t, locale } = useI18n()
const { isOpen, entries, acknowledge } = useChangelog()

// Coerce the current i18n locale to one of the changelog languages.
// The backend guarantees both 'es' and 'en' are present in every entry,
// so this never falls through silently.
const currentLocale = computed<'es' | 'en'>(() => {
  return locale.value === 'en' ? 'en' : 'es'
})

// The "headline" entry is the newest one — its translation drives the
// modal's title and section content. Older unseen entries are surfaced
// as a compact list at the bottom.
const latestEntry = computed(() => entries.value[0])

const activeTranslation = computed(() => {
  return latestEntry.value.translations[currentLocale.value]
    || latestEntry.value.translations.es
})

function handleAcknowledge() {
  acknowledge()
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from > div {
  transform: scale(0.96);
}
.modal-leave-to > div {
  transform: scale(0.98);
}
</style>
