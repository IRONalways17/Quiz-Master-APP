<template>
  <div class="auth-container">
    <div class="container">
      <div class="row justify-content-center align-items-center auth-content">
        <div class="col-md-5 col-lg-4">
          <div class="card shadow-lg border-0 fade-in">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <div class="auth-icon mb-3">
                  <img src="https://raw.githubusercontent.com/23f2003700/B/refs/heads/main/topim.png" 
                       alt="IIT Madras Logo" 
                       class="login-logo">
                </div>
                <h2 class="fw-bold text-primary">Quiz Master V2</h2>
                <p class="text-muted">Welcome back! Please login to continue.</p>
              </div>
              
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="email" class="form-label fw-semibold">Email</label>
                  <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input 
                      type="email" 
                      class="form-control border-start-0" 
                      id="email"
                      v-model="form.email"
                      placeholder="Enter your email"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
                
                <div class="mb-4">
                  <label for="password" class="form-label fw-semibold">Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showPassword ? 'text' : 'password'" 
                      class="form-control border-start-0 border-end-0" 
                      id="password"
                      v-model="form.password"
                      placeholder="Enter your password"
                      required
                      :disabled="loading"
                    >
                    <button 
                      class="btn btn-light border-start-0" 
                      type="button"
                      @click="showPassword = !showPassword"
                      :disabled="loading"
                    >
                      <i :class="`bi bi-eye${showPassword ? '-slash' : ''}`"></i>
                    </button>
                  </div>
                </div>
                
                <button 
                  type="submit" 
                  class="btn btn-primary w-100 py-2 fw-semibold"
                  :disabled="loading"
                >
                  <span v-if="!loading">
                    <i class="bi bi-box-arrow-in-right me-2"></i>
                    Login
                  </span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Logging in...
                  </span>
                </button>
              </form>
              
              <div class="text-center mt-4">
                <p class="mb-0">
                  Don't have an account? 
                  <router-link to="/register" class="text-primary fw-semibold text-decoration-none">
                    Register here
                  </router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Login',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const showPassword = ref(false)
    
    const form = reactive({
      email: '',
      password: ''
    })
    
    // Clear any existing stale auth state when component mounts
    onMounted(() => {
      console.log('Login page mounted, clearing any stale auth state')
      // Only clear if there's actually something to clear
      const token = store.state.auth.token
      const refreshToken = store.state.auth.refreshToken
      if (token || refreshToken) {
        console.log('Clearing stale auth tokens on login page')
        store.commit('auth/CLEAR_AUTH')
      }
    })
    
    const handleLogin = async () => {
      // Prevent double submission
      if (loading.value) {
        console.log('Login already in progress, ignoring duplicate call')
        return
      }
      
      loading.value = true
      try {
        console.log('Attempting login with:', form)
        const result = await store.dispatch('auth/login', form)
        console.log('Login successful:', result)
      } catch (error) {
        console.error('Login error:', error)
        console.error('Error response:', error.response)
        console.error('Error message:', error.message)
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      loading,
      showPassword,
      handleLogin
    }
  }
}
</script>

<style scoped>
.auth-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding-top: 80px; /* Account for navbar */
}

.auth-content {
  min-height: calc(100vh - 80px);
}

.auth-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2.5rem;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  padding: 15px;
}

.login-logo {
  width: 50px;
  height: auto;
}

.input-group-text {
  border: 1px solid #dee2e6;
}

.form-control:focus {
  box-shadow: none;
}

.demo-credentials {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
}
</style> 