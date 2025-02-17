// Import staging or production environment variable
const environment = import.meta.env.STAGING_OR_PROD;

// Define appropriate environment API url
export const API_URL =
  environment === "PROD"
    ? "https://ecommerce-api-production-50293729231.europe-west10.run.app"
    : "https://product-recs-api-50293729231.europe-west10.run.app";

export const FRONTEND_URL = 
  environment === "PROD"
    ? "web-app-frontend-production-50293729231.europe-west10.run.app"
    : "web-app-frontend-50293729231.europe-west10.run.app";

console.log(`Using API URL: ${API_URL}`);