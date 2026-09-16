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
        name: 'Proxy Management System',
        short_name: 'PMS',
        description: 'School teacher proxy management for Mrs. Vaishali Patil',
        theme_color: '#2563eb',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          },
          {
            src: '/icons/icon-512.svg',
            sizes: '512x512',
            type: 'image/svg+xml'
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
