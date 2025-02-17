import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { FRONTEND_URL } from './config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Allow external access (needed for Docker & Cloud Run)
    port: 5173, // Ensure Vite runs on the correct port
    allowedHosts: [
      FRONTEND_URL // Allow Cloud Run Frontend domain
    ]
  }
})