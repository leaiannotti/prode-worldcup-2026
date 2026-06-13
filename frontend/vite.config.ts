import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'path'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'Prode Mundial 2026',
        short_name: 'Prode 2026',
        description: 'Predicciones del Mundial 2026 — predict matches and compete with your group.',
        theme_color: '#00134d',
        background_color: '#f8f9fa',
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
            // Auth endpoints must never be cached — always hit the network.
            urlPattern: ({ url }) => url.pathname.startsWith('/api/auth/'),
            handler: 'NetworkOnly',
            method: 'GET'
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
  }
})
