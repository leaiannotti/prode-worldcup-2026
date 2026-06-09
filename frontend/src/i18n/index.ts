import { createI18n } from 'vue-i18n'
import es from './es.json'
import en from './en.json'

const savedLocale = localStorage.getItem('locale') || 'es'

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'es',
  messages: { es, en },
})

export function setLocale(locale: 'es' | 'en') {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  document.documentElement.lang = locale
}
