// @vitest-environment node

/**
 * Activity formatting utility tests.
 */
import { describe, it, expect } from 'vitest'
import { createI18n } from 'vue-i18n'
import { formatPrizeChangedEvent } from './activity'

const messages = {
  es: {
    leagueDetail: {
      prizeRankFirst: '1° premio',
      prizeRankSecond: '2° premio',
      prizeRankThird: '3° premio',
    },
    activity: {
      prizeChanged: '{user} cambió el {rank} de «{previous}» a «{new}»',
      adminMarker: '(admin)',
      someone: 'Alguien',
    },
  },
}

const i18n = createI18n({ legacy: false, locale: 'es', messages })
const t = i18n.global.t

function makeEvent(payload: any, actor_name: string | null = null) {
  return {
    id: '1',
    event_type: 'prize_changed' as const,
    group_id: 'g1',
    match_id: null,
    payload,
    occurred_at: '2024-01-01T00:00:00Z',
    actor_name,
  }
}

describe('formatPrizeChangedEvent', () => {
  it('formats a regular member change', () => {
    const event = makeEvent({ rank: 1, previous_value: 'Pizza', new_value: 'Asado', actor_is_admin: false }, 'Juan')
    expect(formatPrizeChangedEvent(event, t)).toBe('Juan cambió el 1° premio de «Pizza» a «Asado»')
  })

  it('formats an admin change with marker', () => {
    const event = makeEvent({ rank: 2, previous_value: 'Cerveza', new_value: 'Vino', actor_is_admin: true }, 'Lea')
    expect(formatPrizeChangedEvent(event, t)).toBe('Lea (admin) cambió el 2° premio de «Cerveza» a «Vino»')
  })

  it('falls back to "someone" when actor_name is missing', () => {
    const event = makeEvent({ rank: 3, previous_value: 'Medalla', new_value: 'Nada', actor_is_admin: false }, null)
    expect(formatPrizeChangedEvent(event, t)).toBe('Alguien cambió el 3° premio de «Medalla» a «Nada»')
  })
})
