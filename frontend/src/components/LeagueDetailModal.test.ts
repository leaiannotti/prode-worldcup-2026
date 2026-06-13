// @vitest-environment happy-dom

/**
 * LeagueDetailModal component tests — prize editing.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
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
    global: { plugins: [pinia, i18n] },
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
  beforeEach(() => {
    setActivePinia(createPinia())
    const authStore = useAuthStore()
    authStore.user = { id: 'user-1', email: 'test@example.com', name: 'Test User', picture: null }
  })

  it('renders the 3 prize ranks in read-only mode by default', () => {
    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
    expect(wrapper.text()).toContain('Pizza')
    expect(wrapper.text()).toContain('Cerveza')
    expect(wrapper.findAll('input').length).toBe(0)
  })

  it('clicking "Editar premios" enables inputs', async () => {
    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    expect(inputs.length).toBe(3)
    expect(inputs[0].element.value).toBe('Pizza')
    expect(inputs[1].element.value).toBe('Cerveza')
    expect(inputs[2].element.value).toBe('')
  })

  it('char counter updates as you type', async () => {
    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('Asado')
    expect(wrapper.text()).toContain('5/200')
  })

  it('Save button disabled when input exceeds 200 chars', async () => {
    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    const inputs = wrapper.findAll('input')
    await inputs[0].setValue('x'.repeat(201))
    const saveBtn = findButtonByText(wrapper, 'Guardar')
    expect(saveBtn?.attributes('disabled')).toBeDefined()
  })

  it('Save button disabled when all inputs are empty/whitespace', async () => {
    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
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

    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
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

    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
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
    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
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

    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
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

    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    await clickSave(wrapper)

    expect(wrapper.text()).toContain('Algún premio supera los 200 caracteres')
  })

  it('surfaces generic error i18n message', async () => {
    const { apiClient } = await import('@/lib/api')
    vi.mocked(apiClient.patch).mockRejectedValueOnce(new Error('Network Error'))

    const wrapper = createWrapper({ isOpen: true, group: mockGroup })
    await enterEditMode(wrapper)
    await clickSave(wrapper)

    expect(wrapper.text()).toContain('No pudimos guardar los premios')
  })
})
