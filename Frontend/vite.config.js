import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite";


export default defineConfig({
plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // open: true,
    proxy: {
      '/api': {
        target: 'https://naija-bay-backend.onrender.com',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      "@": "/src",
    }
  }
})