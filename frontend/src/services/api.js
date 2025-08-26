import axios from 'axios'
import store from '@/store'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    const token = store.state.auth.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    if (config.showLoading !== false) {
      store.commit('SET_LOADING', true)
    }
    
    return config
  },
  error => {
    store.commit('SET_LOADING', false)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    store.commit('SET_LOADING', false)
    return response
  },
  async error => {
    store.commit('SET_LOADING', false)
    
    // Handle timeout
    if (error.code === 'ECONNABORTED') {
      store.dispatch('showError', 'Request timeout. Please try again.')
      return Promise.reject(error)
    }
    
    // Handle network errors
    if (!error.response) {
      store.dispatch('showError', 'Network error. Please check your connection.')
      return Promise.reject(error)
    }
    
    const originalRequest = error.config
    
    // Handle 401 Unauthorized - try token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const currentPath = router.currentRoute.value.path
      const isAuthPage = ['/login', '/register', '/'].includes(currentPath)
      const isAuthenticated = store.getters['auth/isAuthenticated']
      
      if (isAuthPage || !isAuthenticated) {
        if (store.state.auth.token || store.state.auth.refreshToken) {
          store.commit('auth/CLEAR_AUTH')
        }
        return Promise.reject(error)
      }
      
      try {
        const newToken = await store.dispatch('auth/refreshToken')
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        store.commit('auth/CLEAR_AUTH')
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    
    // Handle other errors
    let errorMessage = 'An unexpected error occurred'
    
    if (error.response?.status === 403) {
      errorMessage = 'Access denied'
    } else if (error.response?.status === 404) {
      errorMessage = 'Resource not found'
    } else if (error.response?.status === 422) {
      errorMessage = error.response?.data?.error || 'Invalid input data'
    } else if (error.response?.status >= 500) {
      errorMessage = 'Server error. Please try again later'
    } else if (error.response?.data?.error) {
      errorMessage = error.response.data.error
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    }
    
    // Show error message
    const currentPath = router.currentRoute.value.path
    const isAuthPage = ['/login', '/register', '/'].includes(currentPath)
    
    if (!isAuthPage || error.response?.status !== 401) {
      store.dispatch('showError', errorMessage)
    }
    
    return Promise.reject(error)
  }
)

export default api 