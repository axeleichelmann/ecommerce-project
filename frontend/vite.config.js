import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();
const environment = process.env.STAGING_OR_PROD;

// Define appropriate environment API url
export const API_URL =
  environment === "PROD"
    ? "https://ecommerce-api-production-50293729231.europe-west10.run.app"
    : "https://product-recs-api-50293729231.europe-west10.run.app";
console.log(`Using API URL: ${API_URL}`);


// Define allowed hosts for frontend URL
const FRONTEND_URL = 
  environment === "PROD"
    ? "web-app-frontend-production-50293729231.europe-west10.run.app"
    : "web-app-frontend-50293729231.europe-west10.run.app";

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