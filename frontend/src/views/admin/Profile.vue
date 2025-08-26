<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <h1 class="mb-4">
          <i class="bi bi-person-gear me-2"></i>
          Admin Profile
        </h1>
      </div>
    </div>

    <div class="row g-4">
      <!-- Profile Information -->
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-person-circle me-2"></i>
              Account Information
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label for="fullName" class="form-label">Full Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="fullName"
                    v-model="profileForm.full_name"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label for="email" class="form-label">Email Address</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email"
                    v-model="profileForm.email"
                    required
                    disabled
                  >
                  <small class="text-muted">Email cannot be changed for admin accounts</small>
                </div>
                <div class="col-12">
                  <label for="username" class="form-label">Username</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="username"
                    v-model="profileForm.username"
                    required
                  >
                </div>
                <div class="col-12">
                  <label class="form-label">Role</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    value="Administrator"
                    disabled
                  >
                </div>
                <div class="col-12">
                  <button type="submit" class="btn btn-primary" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-check-circle me-2"></i>
                    {{ loading ? 'Updating...' : 'Update Profile' }}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        <!-- Change Password -->
        <div class="card mt-4">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-shield-lock me-2"></i>
              Change Password
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="row g-3">
                <div class="col-md-6">
                  <label for="currentPassword" class="form-label">Current Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showCurrentPassword ? 'text' : 'password'" 
                      class="form-control border-start-0 border-end-0" 
                      id="currentPassword"
                      v-model="passwordForm.current_password"
                      required
                    >
                    <button 
                      class="btn btn-light border-start-0" 
                      type="button"
                      @click="showCurrentPassword = !showCurrentPassword"
                    >
                      <i :class="`bi bi-eye${showCurrentPassword ? '-slash' : ''}`"></i>
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <label for="newPassword" class="form-label">New Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showNewPassword ? 'text' : 'password'" 
                      class="form-control border-start-0 border-end-0" 
                      id="newPassword"
                      v-model="passwordForm.new_password"
                      required
                      minlength="8"
                    >
                    <button 
                      class="btn btn-light border-start-0" 
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                    >
                      <i :class="`bi bi-eye${showNewPassword ? '-slash' : ''}`"></i>
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <label for="confirmPassword" class="form-label">Confirm New Password</label>
                  <div class="input-group">
                    <span class="input-group-text bg-light border-end-0">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showConfirmPassword ? 'text' : 'password'" 
                      class="form-control border-start-0 border-end-0" 
                      id="confirmPassword"
                      v-model="passwordForm.confirm_password"
                      required
                    >
                    <button 
                      class="btn btn-light border-start-0" 
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                    >
                      <i :class="`bi bi-eye${showConfirmPassword ? '-slash' : ''}`"></i>
                    </button>
                  </div>
                </div>
                <div class="col-12">
                  <button type="submit" class="btn btn-warning" :disabled="passwordLoading">
                    <span v-if="passwordLoading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-key me-2"></i>
                    {{ passwordLoading ? 'Changing...' : 'Change Password' }}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Account Statistics -->
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-graph-up me-2"></i>
              Account Statistics
            </h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-6">
                <div class="text-center">
                  <h4 class="text-primary mb-1">{{ stats.total_subjects || 0 }}</h4>
                  <small class="text-muted">Subjects Created</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <h4 class="text-success mb-1">{{ stats.total_quizzes || 0 }}</h4>
                  <small class="text-muted">Quizzes Created</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <h4 class="text-info mb-1">{{ stats.total_users || 0 }}</h4>
                  <small class="text-muted">Total Users</small>
                </div>
              </div>
              <div class="col-6">
                <div class="text-center">
                  <h4 class="text-warning mb-1">{{ stats.total_questions || 0 }}</h4>
                  <small class="text-muted">Questions Created</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Account Information -->
        <div class="card mt-4">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-info-circle me-2"></i>
              Account Details
            </h5>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <strong>Account Created:</strong><br>
              <small class="text-muted">{{ formatDate(profile.created_at) }}</small>
            </div>
            <div class="mb-3">
              <strong>Last Login:</strong><br>
              <small class="text-muted">{{ formatDate(profile.last_login) }}</small>
            </div>
            <div class="mb-3">
              <strong>Account Status:</strong><br>
              <span class="badge bg-success">Active</span>
            </div>
            <div class="mb-3">
              <strong>Permissions:</strong><br>
              <small class="text-muted">Full administrative access</small>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="card mt-4">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-lightning me-2"></i>
              Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="d-grid gap-2">
              <router-link to="/admin/dashboard" class="btn btn-outline-primary">
                <i class="bi bi-speedometer2 me-2"></i>
                Go to Dashboard
              </router-link>
              <router-link to="/admin/users" class="btn btn-outline-success">
                <i class="bi bi-people me-2"></i>
                Manage Users
              </router-link>
              <router-link to="/admin/subjects" class="btn btn-outline-info">
                <i class="bi bi-book me-2"></i>
                Manage Subjects
              </router-link>
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
import api from '@/services/api'

export default {
  name: 'AdminProfile',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const passwordLoading = ref(false)
    const profile = ref({})
    const stats = ref({})

    const profileForm = reactive({
      full_name: '',
      email: '',
      username: ''
    })

    const passwordForm = reactive({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })

    const showCurrentPassword = ref(false)
    const showNewPassword = ref(false)
    const showConfirmPassword = ref(false)

    const fetchProfile = async () => {
      try {
        const response = await api.get('/auth/me')
        profile.value = response.data.user
        
        // Populate form
        profileForm.full_name = profile.value.full_name || ''
        profileForm.email = profile.value.email || ''
        profileForm.username = profile.value.username || ''
      } catch (error) {
        store.dispatch('showError', 'Failed to load profile data')
      }
    }

    const fetchStats = async () => {
      try {
        const response = await api.get('/admin/dashboard/stats')
        stats.value = response.data
      } catch (error) {
        store.dispatch('showError', 'Failed to load statistics')
      }
    }

    const updateProfile = async () => {
      loading.value = true
      try {
        await api.put('/auth/profile', profileForm)
        store.dispatch('showSuccess', 'Profile updated successfully')
        await fetchProfile()
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to update profile')
      } finally {
        loading.value = false
      }
    }

    const changePassword = async () => {
      if (passwordForm.new_password !== passwordForm.confirm_password) {
        store.dispatch('showError', 'New passwords do not match')
        return
      }

      if (passwordForm.new_password.length < 8) {
        store.dispatch('showError', 'Password must be at least 8 characters long')
        return
      }

      passwordLoading.value = true
      try {
        await api.put('/auth/change-password', {
          current_password: passwordForm.current_password,
          new_password: passwordForm.new_password
        })
        store.dispatch('showSuccess', 'Password changed successfully')
        
        // Clear form
        passwordForm.current_password = ''
        passwordForm.new_password = ''
        passwordForm.confirm_password = ''
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to change password')
      } finally {
        passwordLoading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      fetchProfile()
      fetchStats()
    })

    return {
      profile,
      stats,
      profileForm,
      passwordForm,
      loading,
      passwordLoading,
      updateProfile,
      changePassword,
      formatDate,
      showCurrentPassword,
      showNewPassword,
      showConfirmPassword
    }
  }
}
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.card-header {
  border-bottom: 1px solid #e9ecef;
}

.input-group-text {
  border: 1px solid #dee2e6;
}

.form-control:focus {
  box-shadow: none;
}
</style> 