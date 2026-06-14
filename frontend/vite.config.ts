import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: [
        'favicon.ico',
        'favicon-16x16.png',
        'favicon-32x32.png',
        'apple-touch-icon.png',
        'messi-copa.png',
      ],
      manifest: {
        name: 'Prode Mundial 2026',
        short_name: 'Prode 2026',
        description: 'Predicciones del Mundial 2026 — predict matches and compete with your group.',
        theme_color: '#00134d',
        // Matches theme_color so the PWA splash screen does not flash white
        // when the user has dark mode enabled.
        background_color: '#00134d',
        display: 'standalone',
        start_url: '/',
        scope: '/',
        lang: 'es',
        dir: 'ltr',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: 'pwa-maskable-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico,woff,woff2}'],
        navigateFallback: '/index.html',
        navigateFallbackDenylist: [/^\/api\//],
        runtimeCaching: [
          {
            // Auth mutations and OAuth flow must never be cached — always hit
            // the network. /me is handled separately below.
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api/auth/') && url.pathname !== '/api/auth/me',
            handler: 'NetworkOnly',
            method: 'GET'
          },
          {
            // Session check: NetworkFirst with very short TTL so the app can
            // recover from brief network flakiness (subway, elevator, etc.)
            // without forcing a logout. 30s is short enough that a real logout
            // is reflected almost immediately on next navigation.
            urlPattern: ({ url }) => url.pathname === '/api/auth/me',
            handler: 'NetworkFirst',
            method: 'GET',
            options: {
              cacheName: 'auth-me-cache',
              networkTimeoutSeconds: 3,
              expiration: {
                maxEntries: 1,
                maxAgeSeconds: 30
              },
              cacheableResponse: {
                statuses: [200]
              }
            }
          },
          {
            // Other API calls: prefer fresh data, fall back to short-lived cache.
            urlPattern: ({ url }) =>
              url.pathname.startsWith('/api/') && !url.pathname.startsWith('/api/auth/'),
            handler: 'NetworkFirst',
            method: 'GET',
            options: {
              cacheName: 'api-cache',
              networkTimeoutSeconds: 5,
              expiration: {
                maxEntries: 64,
                maxAgeSeconds: 60 // short TTL: 1 minute
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      },
      devOptions: {
        enabled: false
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  preview: {
    allowedHosts: true
  }
})
