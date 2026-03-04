import axios from 'axios'
import router from '@/core/router'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  withCredentials: true,
})

// Флаг, чтобы не зациклиться
let isRefreshing = false
let failedQueue: any[] = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve()
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Если это уже запрос на refresh или login - не обрабатываем
    if (originalRequest.url?.includes('/auth/refresh') || 
        originalRequest.url?.includes('/auth/login') ||
        originalRequest.url?.includes('/auth/register')) {
      return Promise.reject(error)
    }

    // Если 401 и еще не пробовали обновить
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      if (isRefreshing) {
        // Если уже обновляем - ставим в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then(() => {
            return apiClient(originalRequest)
          })
          .catch((err) => {
            return Promise.reject(err)
          })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Пробуем обновить токен
        await axios.post('http://localhost:8000/auth/refresh', {}, {
          withCredentials: true
        })
        
        processQueue(null)
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        // Редирект на логин
        router.push('/login')
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)