import axios from 'axios';

// Import staging or production environment variable
const environment = import.meta.env.STAGING_OR_PROD;

// Define appropriate environment API url
const API_URL =
  environment === "PROD"
    ? "https://ecommerce-api-production-50293729231.europe-west10.run.app"
    : "https://product-recs-api-50293729231.europe-west10.run.app";

console.log(`Using API URL: ${API_URL}`);



// Create an instance of axios with the base url
const api = axios.create({
    baseURL : API_URL
});


// Export api instance
export default api;
