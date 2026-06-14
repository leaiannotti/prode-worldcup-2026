// @vitest-environment happy-dom

/**
 * LeagueDetailModal component tests — prize editing.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import LeagueDetailModal from './LeagueDetailModal.vue'
import { useAuthStore } from '@/stores/auth'

vi.mock('@/lib/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}))

const messages = {
  es: {
    leagueDetail: {
      editPrizes: 'Editar premios',
      savePrizes: 'Guardar',
      cancel: 'Cancelar',
      viewHistory: 'Ver historial',
      hideHistory: 'Ocultar historial',
      charCounter: '{count}/200',
      prizeRankFirst: '1° premio',
      prizeRankSecond: '2° premio',
      prizeRankThird: '3° premio',
      errorForbidden: 'No tenés permiso para editar los premios de esta liga.',
      errorValidation: 'Algún premio supera los 200 caracteres o quedó vacío.',
      errorGeneric: 'No pudimos guardar los premios. Probá de nuevo.',
      prizes: 'Premios',
      noPrizes: 'Sin premios configurados',
    },
    activity: {
      prizeChanged: '{user} cambió el {rank} de «{previous}» a «{new}»',
      adminMarker: '(admin)',
      someone: 'Alguien',
    },
  },
}

function createWrapper(props: any) {
  const pinia = createPinia()
  const i18n = createI18n({ legacy: false, locale: 'es', messages })
  return mount(LeagueDetailModal, {
    global: { plugins: [pinia, i18n], stubs: { Teleport: true } },
    props,
  })
}

function findButtonByText(wrapper: any, text: string) {
  const buttons = wrapper.findAll('button')
  return buttons.find((b: any) => b.text().includes(text)) || null
}

async function enterEditMode(wrapper: any) {
  const btn = findButtonByText(wrapper, 'Editar premios')
  if (!btn) throw new Error('Edit button not found')
  await btn.trigger('click')
  await flushPromises()
}

async function clickSave(wrapper: any) {
  const btn = findButtonByText(wrapper, 'Guardar')
  if (!btn) throw new Error('Save button not found')
  await btn.trigger('click')
  await flushPromises()
}

async function clickCancel(wrapper: any) {
  const btn = findButtonByText(wrapper, 'Cancelar')
  if (!btn) throw new Error('Cancel button not found')
  await btn.trigger('click')
  await flushPromises()
}

const mockGroup = {
  id: 'g1',
  name: 'Test Liga',
  invite_code: 'ABC123',
  created_at: '2024-01-01',
  creator_id: 'user-1',
  member_count: 5,
  prizes: [
    { rank: 1, description: 'Pizza' },
    { rank: 2, description: 'Cerveza' },
  ],
}

describe('LeagueDetailModal — prize editing', () => {
  let wrapper: any

  beforeEach(() => {
    setActivePinia(createPinia())
    const authStore = useAuthStore()
    authStore.user = { id: 'user-1', email: 'test@example.com', name: 'Test User', picture: null }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('renders the 3 prize ranks in read-only mode by default', () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    expect(wrapper.text()).toContain('Pizza')
    expect(wrapper.text()).toContain('Cerveza')
    expect(wrapper.findAll('input').length).toBe(0)
  })

  it('clicking "Editar premios" enables inputs', async () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBe(3)
    expect(inputs[0].element.value).toBe('Pizza')
    expect(inputs[1].element.value).toBe('Cerveza')
    expect(inputs[2].element.value).toBe('')
  })

  it('char counter updates as you type', async () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    expect(wrapper.text()).toContain('5/200')
  })

  it('Save button disabled when input exceeds 200 chars', async () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('x'.repeat(201))
    const saveBtn = findButtonByText(wrapper, 'Guardar')
    expect(saveBtn?.attributes('disabled')).toBeDefined()
  })

  it('Save button disabled when all inputs are empty/whitespace', async () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    for (const input of inputs) {
      await input.setValue('   ')
    }
    const saveBtn = findButtonByText(wrapper, 'Guardar')
    expect(saveBtn?.attributes('disabled')).toBeDefined()
  })

  it('clicking Save calls groupsStore.patchPrizes with the bulk body', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.patch).mockResolvedValueOnce({
      data: { changed: [{ rank: 1, previous: 'Pizza', new: 'Asado' }] },
    })

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    await clickSave(wrapper)

    expect(apiClient.patch).toHaveBeenCalledTimes(1)
    expect(apiClient.patch).toHaveBeenCalledWith(
      '/api/groups/g1/prizes',
      { first: 'Asado' }
    )
  })

  it('inputs become disabled during save', async () => {
    const { apiClient } = await import('@/lib/api')
    let resolvePatch: any
    vi.mocked(apiClient.patch).mockImplementationOnce(
      () => new Promise((resolve) => { resolvePatch = resolve })
    )

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')

    const saveBtn = findButtonByText(wrapper, 'Guardar')
    await saveBtn?.trigger('click')
    await flushPromises()

    for (const input of wrapper.findAll('input')) {
      expect(input.attributes('disabled')).toBeDefined()
    }

    resolvePatch({ data: { changed: [] } })
    await flushPromises()
  })

  it('Cancel reverts to original values and exits edit mode', async () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    await clickCancel(wrapper)

    expect(wrapper.findAll('input').length).toBe(0)
    expect(wrapper.text()).toContain('Pizza')
  })

  it('surfaces 403 error i18n message', async () => {
    const { apiClient } = await import('@/lib/api')
    const error = new Error('Forbidden')
    ;(error as any).response = { status: 403, data: { error: 'forbidden' } }
    vi.mocked(apiClient.patch).mockRejectedValueOnce(error)

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    await clickSave(wrapper)

    expect(wrapper.text()).toContain('No tenés permiso para editar los premios')
  })

  it('surfaces 422 error i18n message', async () => {
    const { apiClient } = await import('@/lib/api')
    const error = new Error('Unprocessable Entity')
    ;(error as any).response = { status: 422, data: { error: 'invalid_request' } }
    vi.mocked(apiClient.patch).mockRejectedValueOnce(error)

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    await clickSave(wrapper)

    expect(wrapper.text()).toContain('Algún premio supera los 200 caracteres')
  })

  it('surfaces generic error i18n message', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.patch).mockRejectedValueOnce(new Error('Network Error'))

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    await clickSave(wrapper)

    expect(wrapper.text()).toContain('No pudimos guardar los premios')
  })
})

describe('LeagueDetailModal — audit history', () => {
  let wrapper: any

  beforeEach(() => {
    setActivePinia(createPinia())
    const authStore = useAuthStore()
    authStore.user = { id: 'user-1', email: 'test@example.com', name: 'Test User', picture: null }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  function findButtonByText(wrapper: any, text: string) {
    const buttons = wrapper.findAll('button')
    return buttons.find((b: any) => b.text().includes(text)) || null
  }

  async function clickHistoryToggle(wrapper: any) {
    const btn = findButtonByText(wrapper, 'Ver historial') || findButtonByText(wrapper, 'Ocultar historial')
    if (!btn) throw new Error('History toggle button not found')
    await btn.trigger('click')
    await flushPromises()
  }

  const mockGroup = {
    id: 'g1',
    name: 'Test Liga',
    invite_code: 'ABC123',
    created_at: '2024-01-01',
    creator_id: 'user-1',
    member_count: 5,
    prizes: [
      { rank: 1, description: 'Pizza' },
      { rank: 2, description: 'Cerveza' },
    ],
  }

  const mockHistoryEvent = {
    id: '1',
    event_type: 'prize_changed',
    group_id: 'g1',
    match_id: null,
    payload: { rank: 1, previous_value: 'Pizza', new_value: 'Asado', actor_is_admin: false },
    occurred_at: '2024-01-01T00:00:00Z',
    actor_name: 'Juan',
  }

  const mockHistoryEventAdmin = {
    id: '2',
    event_type: 'prize_changed',
    group_id: 'g1',
    match_id: null,
    payload: { rank: 2, previous_value: 'Cerveza', new_value: 'Vino', actor_is_admin: true },
    occurred_at: '2024-01-02T00:00:00Z',
    actor_name: 'Lea',
  }

  it('history section is collapsed by default', () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    expect(wrapper.text()).not.toContain('Ocultar historial')
    expect(wrapper.text()).toContain('Ver historial')
  })

  it('clicking "Ver historial" expands and fetches via activityStore.fetchActivity', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: [mockHistoryEvent] },
    })

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await clickHistoryToggle(wrapper)

    expect(apiClient.get).toHaveBeenCalledTimes(1)
    expect(apiClient.get).toHaveBeenCalledWith(
      expect.stringContaining('/api/activity?')
    )
    expect(apiClient.get).toHaveBeenCalledWith(
      expect.stringContaining('event_type=prize_changed')
    )
    expect(apiClient.get).toHaveBeenCalledWith(
      expect.stringContaining('group_id=g1')
    )
  })

  it('renders audit lines with the correct format', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: [mockHistoryEvent] },
    })

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await clickHistoryToggle(wrapper)

    expect(wrapper.text()).toContain('Juan cambió el 1° premio de «Pizza» a «Asado»')
  })

  it('renders admin marker when actor_is_admin: true', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: [mockHistoryEventAdmin] },
    })

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await clickHistoryToggle(wrapper)

    expect(wrapper.text()).toContain('Lea (admin) cambió el 2° premio de «Cerveza» a «Vino»')
  })

  it('clicking "Ocultar historial" collapses the section', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { events: [] },
    })

    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await clickHistoryToggle(wrapper)
    expect(wrapper.text()).toContain('Ocultar historial')

    await clickHistoryToggle(wrapper)
    expect(wrapper.text()).toContain('Ver historial')
    expect(wrapper.text()).not.toContain('Ocultar historial')
  })
})

describe('LeagueDetailModal — deletion UI removed', () => {
  let wrapper: any

  beforeEach(() => {
    setActivePinia(createPinia())
    const authStore = useAuthStore()
    authStore.user = { id: 'user-1', email: 'test@example.com', name: 'Test User', picture: null }
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
      wrapper = null
    }
  })

  it('does not render a league deletion button for admin', () => {
    wrapper = createWrapper({ isOpen: true, group: mockGroup })
    expect(wrapper.text()).not.toContain('Eliminar liga')
    expect(wrapper.text()).not.toContain('Eliminar')
  })

  it('does not render a league deletion button for non-admin', () => {
    wrapper = createWrapper({ isOpen: true, group: { ...mockGroup, creator_id: 'other-user' } })
    expect(wrapper.text()).not.toContain('Eliminar liga')
    expect(wrapper.text()).not.toContain('Eliminar')
  })
})
