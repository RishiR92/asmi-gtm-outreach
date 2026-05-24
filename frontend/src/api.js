import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error?.response?.data?.detail || error.message || 'Unknown error'
    return Promise.reject(new Error(detail))
  }
)

export default api
