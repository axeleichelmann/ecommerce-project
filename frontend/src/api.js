import axios from 'axios';

// Create an instance of axios with the base url
const api = axios.create({
    baseURL : "https://product-recs-api-50293729231.europe-west10.run.app"
});


// Export api instance
export default api;
