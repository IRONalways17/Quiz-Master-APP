<template>
  <div class="auth-container">
    <div class="container">
      <div class="row justify-content-center align-items-center auth-content">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-lg border-0 fade-in">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <div class="auth-icon mb-3">
                  <img src="https://raw.githubusercontent.com/23f2003700/B/refs/heads/main/topim.png" 
                       alt="IIT Madras Logo" 
                       class="register-logo">
                </div>
                <h2 class="fw-bold text-primary">Create Account</h2>
                <p class="text-muted">Join Quiz Master and start learning!</p>
              </div>
              
              <form @submit.prevent="handleRegister">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="fullName" class="form-label fw-semibold">Full Name</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="fullName"
                      v-model="form.full_name"
                      placeholder=""
                      required
                      :disabled="loading"
                    >
                  </div>
                  
                  <div class="col-md-6 mb-3">
                    <label for="username" class="form-label fw-semibold">Username</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="username"
                      v-model="form.username"
                      placeholder=""
                      pattern="[a-zA-Z0-9_]+"
                      required
                      :disabled="loading"
                    >
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="email" class="form-label fw-semibold">Email</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email"
                    v-model="form.email"
                    placeholder=""
                    required
                    :disabled="loading"
                  >
                </div>
                
                <div class="mb-3">
                  <label for="qualification" class="form-label fw-semibold">Qualification</label>
                  <select 
                    class="form-select" 
                    id="qualification"
                    v-model="form.qualification"
                    required
                    :disabled="loading"
                  >
                    <option value="">Select your qualification</option>
                    <option value="High School">High School</option>
                    <option value="Bachelor's Degree">Bachelor's Degree</option>
                    <option value="Master's Degree">Master's Degree</option>
                    <option value="PhD">PhD</option>
                    <option value="Diploma">Diploma</option>
                    <option value="Certificate">Certificate</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                
                <div class="mb-3">
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
                      placeholder=""
                      minlength="6"
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
                  <div class="form-text">Password must be at least 6 characters long</div>
                </div>
                
                <div class="mb-4">
                  <label for="confirmPassword" class="form-label fw-semibold">Confirm Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showConfirmPassword ? 'text' : 'password'" 
                      class="form-control border-start-0 border-end-0" 
                      id="confirmPassword"
                      v-model="confirmPassword"
                      placeholder=""
                      required
                      :disabled="loading"
                      :class="{ 'is-invalid': confirmPassword && confirmPassword !== form.password }"
                    >
                    <button 
                      class="btn btn-light border-start-0" 
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                      :disabled="loading"
                    >
                      <i :class="`bi bi-eye${showConfirmPassword ? '-slash' : ''}`"></i>
                    </button>
                  </div>
                  <div class="invalid-feedback">
                    Passwords do not match
                  </div>
                </div>
                
                <button 
                  type="submit" 
                  class="btn btn-primary w-100 py-2 fw-semibold"
                  :disabled="loading || (confirmPassword && confirmPassword !== form.password)"
                >
                  <span v-if="!loading">
                    <i class="bi bi-person-plus me-2"></i>
                    Create Account
                  </span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Creating account...
                  </span>
                </button>
              </form>
              
              <div class="text-center mt-4">
                <p class="mb-0">
                  Already have an account? 
                  <router-link to="/login" class="text-primary fw-semibold text-decoration-none">
                    Login here
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
  name: 'Register',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const confirmPassword = ref('')
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)
    
    const form = reactive({
      full_name: '',
      username: '',
      email: '',
      qualification: '',
      password: ''
    })
    
    // Clear any existing stale auth state when component mounts
    onMounted(() => {
      console.log('Register page mounted, clearing any stale auth state')
      // Only clear if there's actually something to clear
      const token = store.state.auth.token
      const refreshToken = store.state.auth.refreshToken
      if (token || refreshToken) {
        console.log('Clearing stale auth tokens on register page')
        store.commit('auth/CLEAR_AUTH')
      }
    })
    
    const handleRegister = async () => {
      // Prevent double submission
      if (loading.value) {
        console.log('Registration already in progress, ignoring duplicate call')
        return
      }
      
      if (form.password !== confirmPassword.value) {
        store.dispatch('showError', 'Passwords do not match')
        return
      }
      
      loading.value = true
      try {
        console.log('Starting registration with data:', form)
        await store.dispatch('auth/register', form)
        console.log('Registration completed successfully')
      } catch (error) {
        console.error('Registration error:', error)
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      confirmPassword,
      loading,
      showPassword,
      showConfirmPassword,
      handleRegister
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

.register-logo {
  width: 50px;
  height: auto;
}

.input-group-text {
  border: 1px solid #dee2e6;
}

.form-control:focus {
  box-shadow: none;
}
</style> 