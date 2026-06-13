// @vitest-environment happy-dom

/**
 * PWA service worker registration tests.
 *
 * Mocks the `virtual:pwa-register` module (provided at build time by
 * vite-plugin-pwa) so the registration code can be exercised under happy-dom
 * without actually wiring a service worker.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { registerServiceWorker } from './pwa'

const registerSWMock = vi.fn()

vi.mock('virtual:pwa-register', () => ({
  registerSW: (...args: unknown[]) => registerSWMock(...args),
}))

describe('registerServiceWorker', () => {
  beforeEach(() => {
    registerSWMock.mockReset()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('calls registerSW with immediate + onRegisterError when window is defined', () => {
    registerServiceWorker()

    expect(registerSWMock).toHaveBeenCalledTimes(1)
    const opts = registerSWMock.mock.calls[0][0] as {
      immediate?: boolean
      onRegisterError?: (e: unknown) => void
    }
    expect(opts.immediate).toBe(true)
    expect(typeof opts.onRegisterError).toBe('function')
  })

  it('does not throw when onRegisterError fires', () => {
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    registerServiceWorker()

    expect(registerSWMock).toHaveBeenCalledTimes(1)
    const opts = registerSWMock.mock.calls[0][0] as {
      onRegisterError: (e: unknown) => void
    }

    expect(() => opts.onRegisterError(new Error('boom'))).not.toThrow()
    expect(errorSpy).toHaveBeenCalledWith(
      '[pwa] service worker registration failed',
      expect.any(Error),
    )

    errorSpy.mockRestore()
  })

  it('is a no-op when window is undefined (SSR guard)', () => {
    vi.stubGlobal('window', undefined)

    expect(() => registerServiceWorker()).not.toThrow()
    expect(registerSWMock).not.toHaveBeenCalled()
  })
})
