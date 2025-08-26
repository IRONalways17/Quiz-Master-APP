<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h1 class="mb-0">
          <i class="bi bi-people me-2"></i>
          Users Management
        </h1>
        <div>
          <button class="btn btn-outline-info me-2" @click="exportUsers">
            <i class="bi bi-download me-2"></i>
            Export Users
          </button>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row mb-4">
      <div class="col-md-4">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            placeholder="Search users..."
            v-model="searchQuery"
            @input="filterUsers"
          >
        </div>
      </div>
      <div class="col-md-4">
        <select class="form-select" v-model="statusFilter" @change="filterUsers">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <div class="col-md-4 text-end">
        <button class="btn btn-outline-secondary me-2" @click="refreshData">
          <i class="bi bi-arrow-clockwise me-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Email</th>
                <th>Qualification</th>
                <th>Status</th>
                <th>Last Login</th>
                <th>Quizzes Taken</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-3">
                      <i class="bi bi-person-circle fs-4"></i>
                    </div>
                    <div>
                      <strong>{{ user.full_name }}</strong>
                      <br>
                      <small class="text-muted">@{{ user.username }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ user.email }}</td>
                <td>{{ user.qualification || 'Not specified' }}</td>
                <td>
                  <span :class="getStatusBadgeClass(user.is_active)">
                    {{ user.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>{{ formatDate(user.last_login) }}</td>
                <td>
                  <span class="badge bg-info">{{ user.quizzes_taken || 0 }}</span>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="viewUser(user)">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-warning" @click="toggleUserStatus(user)">
                      <i :class="user.is_active ? 'bi bi-pause-circle' : 'bi bi-play-circle'"></i>
                    </button>
                    <button class="btn btn-outline-danger" @click="deleteUser(user)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="9" class="text-center py-4">
                  <i class="bi bi-inbox fs-1 text-muted"></i>
                  <p class="text-muted mt-2">No users found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- User Details Modal -->
    <div class="modal fade" :class="{ show: showUserModal }" 
         :style="{ display: showUserModal ? 'block' : 'none' }" 
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Details</h5>
            <button type="button" class="btn-close" @click="closeUserModal"></button>
          </div>
          <div class="modal-body" v-if="selectedUser">
            <div class="row">
              <div class="col-md-6">
                <h6>Personal Information</h6>
                <table class="table table-sm">
                  <tbody>
                    <tr>
                      <td><strong>Name:</strong></td>
                      <td>{{ selectedUser.full_name }}</td>
                    </tr>
                    <tr>
                      <td><strong>Username:</strong></td>
                      <td>{{ selectedUser.username }}</td>
                    </tr>
                    <tr>
                      <td><strong>Email:</strong></td>
                      <td>{{ selectedUser.email }}</td>
                    </tr>
                    <tr>
                      <td><strong>Qualification:</strong></td>
                      <td>{{ selectedUser.qualification || 'Not specified' }}</td>
                    </tr>
                    <tr>
                      <td><strong>Date of Birth:</strong></td>
                      <td>{{ formatDate(selectedUser.dob) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div class="col-md-6">
                <h6>Account Information</h6>
                <table class="table table-sm">
                  <tbody>
                    <tr>
                      <td><strong>Status:</strong></td>
                      <td>
                        <span :class="getStatusBadgeClass(selectedUser.is_active)">
                          {{ selectedUser.is_active ? 'Active' : 'Inactive' }}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>Joined:</strong></td>
                      <td>{{ formatDate(selectedUser.created_at) }}</td>
                    </tr>
                    <tr>
                      <td><strong>Last Login:</strong></td>
                      <td>{{ formatDate(selectedUser.last_login) }}</td>
                    </tr>
                    <tr>
                      <td><strong>Quizzes Taken:</strong></td>
                      <td>{{ selectedUser.statistics?.total_quizzes_taken || 0 }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="mt-4">
              <h6>Recent Quiz Attempts</h6>
              <div v-if="userQuizHistory.length > 0">
                <div v-for="attempt in userQuizHistory" :key="attempt.id" class="card mb-2">
                  <div class="card-body py-2">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <strong>{{ attempt.quiz_title }}</strong>
                        <br>
                        <small class="text-muted">{{ formatDate(attempt.completed_at) }}</small>
                      </div>
                      <div class="text-end">
                        <span class="badge" :class="attempt.passed ? 'bg-success' : 'bg-danger'">{{ Math.round(attempt.percentage) }}%</span>
                        <br>
                        <small class="text-muted">{{ formatTimeTaken(attempt.time_taken) }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-3">
                <i class="bi bi-inbox text-muted"></i>
                <p class="text-muted mt-2">No quiz attempts yet</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeUserModal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div class="modal-backdrop fade" :class="{ show: showUserModal }" 
         v-if="showUserModal"></div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'Users',
  setup() {
    const store = useStore()
    
    const users = ref([])
    const filteredUsers = ref([])
    const searchQuery = ref('')
    const statusFilter = ref('')
    const showUserModal = ref(false)
    const selectedUser = ref(null)
    const userQuizHistory = ref([])

    const fetchUsers = async () => {
      try {
        const response = await api.get('/admin/users')
        users.value = response.data.users
        filteredUsers.value = users.value
      } catch (error) {
        store.dispatch('showError', 'Failed to load users')
      }
    }

    const filterUsers = () => {
      let filtered = users.value
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(user =>
          user.full_name.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query) ||
          user.username.toLowerCase().includes(query)
        )
      }
      
      if (statusFilter.value) {
        filtered = filtered.filter(user => 
          statusFilter.value === 'active' ? user.is_active : !user.is_active
        )
      }
      
      filteredUsers.value = filtered
    }

    const viewUser = async (user) => {
      showUserModal.value = true
      
      try {
        // Get detailed user information
        const userResponse = await api.get(`/admin/users/${user.id}`)
        selectedUser.value = userResponse.data.user
        
        // Get user's quiz history
        const historyResponse = await api.get(`/admin/users/${user.id}/history`)
        userQuizHistory.value = historyResponse.data.history
      } catch (error) {
        selectedUser.value = user // Fallback to basic user data
        userQuizHistory.value = []
      }
    }

    const closeUserModal = () => {
      showUserModal.value = false
      selectedUser.value = null
      userQuizHistory.value = []
    }

    const toggleUserStatus = async (user) => {
      try {
        await api.put(`/admin/users/${user.id}/toggle-status`)
        store.dispatch('showSuccess', `User ${user.is_active ? 'deactivated' : 'activated'} successfully`)
        fetchUsers()
      } catch (error) {
        store.dispatch('showError', 'Failed to update user status')
      }
    }

    const deleteUser = async (user) => {
      if (!confirm(`Are you sure you want to delete "${user.full_name}"? This action cannot be undone.`)) {
        return
      }
      
      try {
        await api.delete(`/admin/users/${user.id}`)
        store.dispatch('showSuccess', 'User deleted successfully')
        fetchUsers()
      } catch (error) {
        store.dispatch('showError', 'Failed to delete user')
      }
    }
    const exportUsers = async () => {
      try {
        await api.post('/admin/users/export')
        store.dispatch('showSuccess', 'User export started. You\'ll be notified when ready.')
      } catch (error) {
        store.dispatch('showError', 'Failed to start export')
      }
    }

    const refreshData = () => {
      fetchUsers()
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Never'
      return new Date(dateString).toLocaleDateString()
    }

    const formatTimeTaken = (seconds) => {
      if (!seconds) return 'Never'
      if (seconds < 60) return `${seconds} seconds`
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      if (remainingSeconds === 0) return `${minutes} minutes`
      return `${minutes}m ${remainingSeconds}s`
    }

    const getStatusBadgeClass = (isActive) => {
      return isActive ? 'badge bg-success' : 'badge bg-secondary'
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      filteredUsers,
      searchQuery,
      statusFilter,
      showUserModal,
      selectedUser,
      userQuizHistory,
      fetchUsers,
      filterUsers,
      viewUser,
      closeUserModal,
      toggleUserStatus,
      deleteUser,
      exportUsers,
      refreshData,
      formatDate,
      formatTimeTaken,
      getStatusBadgeClass
    }
  }
}
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-backdrop {
  z-index: 1040;
}

.modal {
  z-index: 1050;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
