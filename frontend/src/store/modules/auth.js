import api from '@/services/api'
import router from '@/router'

const state = {
  token: localStorage.getItem('token') || null,
  refreshToken: localStorage.getItem('refreshToken') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
  role: localStorage.getItem('role') || null
}

const getters = {
  isAuthenticated: state => !!state.token,
  currentUser: state => state.user,
  userRole: state => state.role,
  isAdmin: state => state.role === 'admin',
  isUser: state => state.role === 'user'
}

const mutations = {
  SET_AUTH(state, { token, refreshToken, user, role }) {
    state.token = token
    state.refreshToken = refreshToken
    state.user = user
    state.role = role
    
    // Save to localStorage
    if (token) {
      localStorage.setItem('token', token)
      localStorage.setItem('refreshToken', refreshToken)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('role', role)
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    }
  },
  
  CLEAR_AUTH(state) {
    state.token = null
    state.refreshToken = null
    state.user = null
    state.role = null
    
    // Clear localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
    localStorage.removeItem('role')
    delete api.defaults.headers.common['Authorization']
  },
  
  UPDATE_USER(state, user) {
    state.user = user
    localStorage.setItem('user', JSON.stringify(user))
  }
}

const actions = {
  async login({ commit, dispatch }, credentials) {
    try {
      console.log('Auth store: Attempting login with credentials:', { email: credentials.email })
      
      const response = await api.post('/auth/login', credentials)
      console.log('Auth store: Login response received:', response.status)
      
      const { access_token, refresh_token, user, role } = response.data
      
      commit('SET_AUTH', {
        token: access_token,
        refreshToken: refresh_token,
        user,
        role
      })
      
      dispatch('showSuccess', 'Login successful!', { root: true })
      
      // Redirect based on role
      if (role === 'admin') {
        router.push('/admin/dashboard')
      } else {
        router.push('/dashboard')
      }
      
      return response.data
    } catch (error) {
      console.error('Auth store: Login error details:', {
        message: error.message,
        code: error.code,
        status: error.response?.status,
        data: error.response?.data,
        timeout: error.code === 'ECONNABORTED'
      })
      
      // Handle specific error types
      let errorMessage = 'Login failed'
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Login request timed out. Please check your connection and try again.'
      } else if (!error.response) {
        errorMessage = 'Network error. Please check if the server is running and try again.'
      } else if (error.response?.status === 401) {
        errorMessage = error.response?.data?.error || 'Invalid email or password'
      } else if (error.response?.status === 422) {
        errorMessage = error.response?.data?.error || 'Invalid input data'
      } else if (error.response?.status >= 500) {
        errorMessage = 'Server error. Please try again later.'
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      dispatch('showError', errorMessage, { root: true })
      throw error
    }
  },
  
  async register({ commit, dispatch }, userData) {
    try {
      const response = await api.post('/auth/register', userData)
      const { access_token, refresh_token, user } = response.data
      
      commit('SET_AUTH', {
        token: access_token,
        refreshToken: refresh_token,
        user,
        role: 'user'
      })
      
      dispatch('showSuccess', 'Registration successful!', { root: true })
      router.push('/dashboard')
      
      return response.data
    } catch (error) {
      dispatch('showError', error.response?.data?.error || 'Registration failed', { root: true })
      throw error
    }
  },
  
  async logout({ commit, dispatch }) {
    commit('CLEAR_AUTH')
    dispatch('showSuccess', 'Logged out successfully', { root: true })
    router.push('/login')
  },
  
  async refreshToken({ state, commit, dispatch }) {
    try {
      // Check if refresh token exists
      if (!state.refreshToken) {
        throw new Error('No refresh token available')
      }
      
      const response = await api.post('/auth/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${state.refreshToken}`
        }
      })
      
      const { access_token } = response.data
      
      commit('SET_AUTH', {
        token: access_token,
        refreshToken: state.refreshToken,
        user: state.user,
        role: state.role
      })
      
      console.log('Token refreshed successfully')
      return access_token
    } catch (error) {
      console.log('Token refresh failed:', error.message)
      
      // Only clear auth state, don't call full logout to avoid unnecessary operations
      commit('CLEAR_AUTH')
      
      // Only show error message if we're not on auth pages
      const currentPath = router.currentRoute.value.path
      if (currentPath !== '/login' && currentPath !== '/register' && currentPath !== '/') {
        dispatch('showError', 'Session expired. Please login again.', { root: true })
        router.push('/login')
      }
      
      throw error
    }
  },
  
  async fetchCurrentUser({ commit, dispatch }) {
    try {
      const response = await api.get('/auth/me')
      commit('UPDATE_USER', response.data.user)
      return response.data.user
    } catch (error) {
      dispatch('showError', 'Failed to fetch user data', { root: true })
      throw error
    }
  },
  
  initializeAuth({ state, commit }) {
    if (state.token) {
      // Set authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
      
      // Validate token by checking if it's expired (basic check)
      try {
        const payload = JSON.parse(atob(state.token.split('.')[1]))
        const currentTime = Date.now() / 1000
        
        if (payload.exp < currentTime) {
          console.log('Token expired during initialization, clearing auth state')
          commit('CLEAR_AUTH')
        } else {
          console.log('Valid token found, maintaining auth state')
        }
      } catch (error) {
        console.log('Invalid token format, clearing auth state')
        commit('CLEAR_AUTH')
      }
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
} 