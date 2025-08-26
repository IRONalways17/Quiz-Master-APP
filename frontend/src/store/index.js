import { createStore } from 'vuex'
import auth from './modules/auth'
import api from '@/services/api'

export default createStore({
  state: {
    toasts: [],
    loading: false
  },
  
  mutations: {
    ADD_TOAST(state, toast) {
      const id = Date.now()
      state.toasts.push({
        id,
        ...toast
      })
      
      // Auto remove after 5 seconds
      setTimeout(() => {
        state.toasts = state.toasts.filter(t => t.id !== id)
      }, 5000)
    },
    
    REMOVE_TOAST(state, id) {
      state.toasts = state.toasts.filter(t => t.id !== id)
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    }
  },
  
  actions: {
    showToast({ commit }, { title, message, type = 'info' }) {
      commit('ADD_TOAST', { title, message, type })
    },
    
    showSuccess({ dispatch }, message) {
      dispatch('showToast', {
        title: 'Success',
        message,
        type: 'success'
      })
    },
    
    showError({ dispatch }, message) {
      dispatch('showToast', {
        title: 'Error',
        message,
        type: 'error'
      })
    },
    
    showWarning({ dispatch }, message) {
      dispatch('showToast', {
        title: 'Warning',
        message,
        type: 'warning'
      })
    }
  },
  
  modules: {
    auth
  }
}) 