<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12">
        <h1 class="mb-3">
          <i class="bi bi-search me-2"></i>
          Search Results
        </h1>
        
        <!-- Search Form -->
        <div class="card mb-4">
          <div class="card-body">
            <form @submit.prevent="performSearch">
              <div class="row g-3">
                <div class="col-md-8">
                  <input 
                    type="text" 
                    class="form-control form-control-lg" 
                    placeholder="Search for subjects, quizzes, users..."
                    v-model="searchQuery"
                    @input="debouncedSearch"
                  >
                </div>
                <div class="col-md-2">
                  <select class="form-select form-select-lg" v-model="searchType">
                    <option value="all">All</option>
                    <option value="subject">Subjects</option>
                    <option value="quiz">Quizzes</option>
                    <option v-if="isAdmin" value="user">Users</option>
                  </select>
                </div>
                <div class="col-md-2">
                  <button type="submit" class="btn btn-primary btn-lg w-100" :disabled="loading">
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                    <i v-else class="bi bi-search me-2"></i>
                    Search
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="hasSearched">
      <div class="row mb-4">
        <div class="col-12">
          <h4>Results for "{{ searchQuery }}" ({{ totalResults }} found)</h4>
        </div>
      </div>

      <!-- No Results Message -->
      <div v-if="totalResults === 0" class="text-center py-5">
        <i class="bi bi-search fs-1 text-muted"></i>
        <h4 class="text-muted mt-3">No results found</h4>
        <p class="text-muted">Try different keywords or check your spelling</p>
        <div class="mt-3">
          <button @click="clearSearch" class="btn btn-outline-primary">
            <i class="bi bi-arrow-left me-2"></i>
            Clear Search
          </button>
        </div>
      </div>

      <!-- Subjects Results -->
      <div v-if="searchType === 'all' || searchType === 'subject'" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="bi bi-book me-2"></i>
            Subjects ({{ subjects.length }})
          </h5>
        </div>
        <div class="card-body">
          <div v-if="subjects.length === 0" class="text-center py-4">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="text-muted mt-2">No subjects found</p>
          </div>
          <div v-else class="row g-3">
            <div v-for="subject in subjects" :key="subject.id" class="col-md-6 col-lg-4">
              <div class="card h-100">
                <div class="card-body">
                  <h6 class="card-title">{{ subject.name }}</h6>
                  <p class="card-text text-muted">{{ subject.description || 'No description' }}</p>
                  <div class="d-flex justify-content-between align-items-center">
                    <span class="badge bg-secondary">{{ subject.code }}</span>
                    <span class="badge bg-info">{{ subject.chapters_count || 0 }} chapters</span>
                  </div>
                </div>
                <div class="card-footer">
                  <router-link :to="`/admin/subjects/${subject.id}/chapters`" class="btn btn-sm btn-outline-primary">
                    View Chapters
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quizzes Results -->
      <div v-if="searchType === 'all' || searchType === 'quiz'" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="bi bi-question-circle me-2"></i>
            Quizzes ({{ quizzes.length }})
          </h5>
        </div>
        <div class="card-body">
          <div v-if="quizzes.length === 0" class="text-center py-4">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="text-muted mt-2">No quizzes found</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Subject</th>
                  <th>Chapter</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="quiz in quizzes" :key="quiz.id">
                  <td><strong>{{ quiz.title }}</strong></td>
                  <td>{{ quiz.chapter?.subject?.name || 'N/A' }}</td>
                  <td>{{ quiz.chapter?.name || 'N/A' }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(quiz.status)">
                      {{ quiz.status }}
                    </span>
                  </td>
                  <td>{{ quiz.duration_minutes }} min</td>
                  <td>
                    <router-link :to="`/admin/quizzes/${quiz.id}/questions`" class="btn btn-sm btn-outline-primary">
                      View Questions
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Users Results -->
      <div v-if="isAdmin && (searchType === 'all' || searchType === 'user')" class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">
            <i class="bi bi-people me-2"></i>
            Users ({{ users.length }})
          </h5>
        </div>
        <div class="card-body">
          <div v-if="users.length === 0" class="text-center py-4">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="text-muted mt-2">No users found</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td><strong>{{ user.full_name || user.username }}</strong></td>
                  <td>{{ user.email }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(user.is_active ? 'active' : 'inactive')">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td>{{ formatDate(user.created_at) }}</td>
                  <td>
                    <button class="btn btn-sm btn-outline-secondary" @click="viewUserDetails(user)">
                      View Details
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Initial State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-search fs-1 text-muted"></i>
      <h4 class="text-muted mt-3">Search for subjects, quizzes, or users</h4>
      <p class="text-muted">Enter your search query above to get started</p>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'Search',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const searchQuery = ref('')
    const searchType = ref('all')
    const loading = ref(false)
    const hasSearched = ref(false)
    
    const subjects = ref([])
    const quizzes = ref([])
    const users = ref([])
    
    // Check if user is admin
    const isAdmin = computed(() => store.getters['auth/userRole'] === 'admin')
    
    const totalResults = computed(() => {
      return subjects.value.length + quizzes.value.length + users.value.length
    })
    
    const performSearch = async () => {
      if (!searchQuery.value.trim()) return
      
      loading.value = true
      hasSearched.value = true
      
      try {
        console.log('Performing search with query:', searchQuery.value, 'type:', searchType.value)
        
        const response = await api.get('/search', {
          params: {
            q: searchQuery.value,
            type: searchType.value
          }
        })
        
        console.log('Search response:', response.data)
        
        // Handle the different response structure
        if (response.data.results) {
          subjects.value = response.data.results.subjects || []
          quizzes.value = response.data.results.quizzes || []
          users.value = response.data.results.users || []
        } else {
          // Fallback for direct structure
          subjects.value = response.data.subjects || []
          quizzes.value = response.data.quizzes || []
          users.value = response.data.users || []
        }
        
        console.log('Processed results:', {
          subjects: subjects.value.length,
          quizzes: quizzes.value.length,
          users: users.value.length
        })
        
      } catch (error) {
        console.error('Search error:', error)
        store.dispatch('showError', error.response?.data?.error || 'Search failed')
      } finally {
        loading.value = false
      }
    }
    
    const debouncedSearch = () => {
      clearTimeout(window.searchTimeout)
      window.searchTimeout = setTimeout(() => {
        if (searchQuery.value.trim()) {
          performSearch()
        }
      }, 500)
    }
    
    const getStatusBadgeClass = (status) => {
      const classes = {
        'active': 'badge bg-success',
        'inactive': 'badge bg-secondary',
        'upcoming': 'badge bg-warning',
        'ongoing': 'badge bg-success',
        'completed': 'badge bg-info',
        'expired': 'badge bg-danger'
      }
      return classes[status] || 'badge bg-secondary'
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }
    
    const viewUserDetails = (user) => {
      // Navigate to user details or show modal
      console.log('View user details:', user)
    }
    
    const clearSearch = () => {
      searchQuery.value = ''
      hasSearched.value = false
      subjects.value = []
      quizzes.value = []
      users.value = []
    }
    
    onMounted(() => {
      // Check if there's a search query in the URL
      if (route.query.q) {
        searchQuery.value = route.query.q
        performSearch()
      }
    })
    
    return {
      searchQuery,
      searchType,
      loading,
      hasSearched,
      subjects,
      quizzes,
      users,
      totalResults,
      isAdmin,
      performSearch,
      debouncedSearch,
      getStatusBadgeClass,
      formatDate,
      viewUserDetails,
      clearSearch
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}
</style>
