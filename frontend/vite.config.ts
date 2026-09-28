import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import path from 'path';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Presento',
        short_name: 'Presento',
        description: 'School teacher proxy management for Mrs. Vaishali Patil',
        theme_color: '#13285f',
        background_color: '#fbf8f1',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        runtimeCaching: [
          { urlPattern: /^\/api\/timetable/, handler: 'StaleWhileRevalidate' },
          { urlPattern: /^\/api\/teachers/, handler: 'NetworkFirst' },
        ]
      }
    }),
  ],
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  // host: true binds to 0.0.0.0 so a phone on the same WiFi can reach this
  // dev server via the laptop's LAN IP, not just localhost.
  server: { host: true, port: 5173, proxy: { '/api': 'http://localhost:8000' } },
});
