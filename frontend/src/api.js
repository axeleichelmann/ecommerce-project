import axios from 'axios';

// Create an instance of axios with the base url
const api = axios.create({
    baseURL : "http://0.0.0.0:8000"
});


// Export api instance
export default api;
