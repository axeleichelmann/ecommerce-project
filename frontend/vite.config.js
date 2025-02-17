import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0", // Allow external access (needed for Docker & Cloud Run)
    port: 5173, // Ensure Vite runs on the correct port
    allowedHosts: [  // Allow Cloud Run Frontend domain
      "web-app-frontend-production-50293729231.europe-west10.run.app",
      "web-app-frontend-50293729231.europe-west10.run.app" 
    ]
  }
})