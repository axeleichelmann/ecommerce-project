import axios from 'axios';
import { API_URL } from '../vite.config';

// Create an instance of axios with the base url
const api = axios.create({
    baseURL : API_URL
});

// Export api instance
export default api;
