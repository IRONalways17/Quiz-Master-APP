<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 class="mb-2">My Scores</h1>
            <p class="text-muted mb-0">View your quiz performance and history</p>
          </div>
          <div>
            <button 
              @click="exportScores" 
              :disabled="exporting"
              class="btn btn-success me-2"
            >
              <i class="bi bi-download me-2"></i>
              {{ exporting ? 'Exporting...' : 'Export CSV' }}
            </button>
          </div>
        </div>

        <!-- Stats Cards -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <h5 class="card-title">Total Attempts</h5>
                <h3 class="mb-0">{{ stats.total_attempts || 0 }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <h5 class="card-title">Passed</h5>
                <h3 class="mb-0">{{ stats.passed_attempts || 0 }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body">
                <h5 class="card-title">Average Score</h5>
                <h3 class="mb-0">{{ stats.average_score || 0 }}%</h3>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body">
                <h5 class="card-title">Pass Rate</h5>
                <h3 class="mb-0">{{ stats.pass_rate || 0 }}%</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row">
              <div class="col-md-3">
                <label class="form-label">Subject</label>
                <select v-model="filters.subject" class="form-select" @change="applyFilters">
                  <option value="">All Subjects</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Status</label>
                <select v-model="filters.status" class="form-select" @change="applyFilters">
                  <option value="">All</option>
                  <option value="passed">Passed</option>
                  <option value="failed">Failed</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Date Range</label>
                <select v-model="filters.dateRange" class="form-select" @change="applyFilters">
                  <option value="">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">This Week</option>
                  <option value="month">This Month</option>
                </select>
              </div>
              <div class="col-md-3">
                <label class="form-label">Sort By</label>
                <select v-model="filters.sortBy" class="form-select" @change="applyFilters">
                  <option value="date">Date (Newest)</option>
                  <option value="score">Score (High to Low)</option>
                  <option value="quiz">Quiz Name</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Scores Table -->
        <div class="card">
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="scores.length === 0" class="text-center py-4">
              <i class="bi bi-clipboard-x display-1 text-muted"></i>
              <h4 class="mt-3">No scores found</h4>
              <p class="text-muted">You haven't taken any quizzes yet.</p>
              <router-link to="/subjects" class="btn btn-primary">
                <i class="bi bi-play-circle me-2"></i>
                Start Taking Quizzes
              </router-link>
            </div>

            <div v-else>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Quiz</th>
                      <th>Subject</th>
                      <th>Score</th>
                      <th>Status</th>
                      <th>Attempt</th>
                      <th>Time</th>
                      <th>Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="score in scores" :key="score.id">
                      <td>
                        <strong>{{ score.quiz_title }}</strong>
                        <br>
                        <small class="text-muted">{{ score.chapter_name }}</small>
                      </td>
                      <td>{{ score.subject_name }}</td>
                      <td>
                        <span class="badge bg-primary">{{ score.score }}/{{ score.max_score }}</span>
                        <br>
                        <small class="text-muted">{{ score.percentage }}%</small>
                      </td>
                      <td>
                        <span 
                          :class="score.passed ? 'badge bg-success' : 'badge bg-danger'"
                        >
                          {{ score.passed ? 'Passed' : 'Failed' }}
                        </span>
                      </td>
                      <td>
                        <span class="badge bg-secondary">Attempt {{ score.attempt_number }}</span>
                      </td>
                      <td>
                        <small class="text-muted">
                          {{ formatTime(score.time_taken_seconds) }}
                        </small>
                      </td>
                      <td>
                        <small class="text-muted">
                          {{ formatDate(score.created_at) }}
                        </small>
                      </td>
                      <td>
                        <router-link 
                          :to="`/scores/${score.id}`"
                          class="btn btn-sm btn-outline-primary"
                        >
                          <i class="bi bi-eye"></i>
                        </router-link>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination -->
              <nav v-if="totalPages > 1" aria-label="Scores pagination">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">
                      Previous
                    </a>
                  </li>
                  <li 
                    v-for="page in visiblePages" 
                    :key="page"
                    class="page-item"
                    :class="{ active: page === currentPage }"
                  >
                    <a class="page-link" href="#" @click.prevent="changePage(page)">
                      {{ page }}
                    </a>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">
                      Next
                    </a>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'Scores',
  setup() {
    const store = useStore()
    const scores = ref([])
    const stats = ref({})
    const subjects = ref([])
    const loading = ref(false)
    const exporting = ref(false)
    const currentPage = ref(1)
    const totalPages = ref(1)
    const totalScores = ref(0)

    const filters = ref({
      subject: '',
      status: '',
      dateRange: '',
      sortBy: 'date'
    })

    const fetchScores = async () => {
      loading.value = true
      try {
        const params = {
          page: currentPage.value,
          per_page: 20,
          ...filters.value
        }
        
        const response = await api.get('/user/scores', { params })
        scores.value = response.data.scores
        totalPages.value = response.data.pages
        totalScores.value = response.data.total
      } catch (error) {
        console.error('Error fetching scores:', error)
        store.dispatch('showError', 'Failed to load scores')
      } finally {
        loading.value = false
      }
    }

    const fetchStats = async () => {
      try {
        const response = await api.get('/user/dashboard/stats')
        stats.value = response.data
      } catch (error) {
        console.error('Error fetching stats:', error)
      }
    }

    const fetchSubjects = async () => {
      try {
        const response = await api.get('/user/subjects')
        subjects.value = response.data.subjects
      } catch (error) {
        console.error('Error fetching subjects:', error)
      }
    }

    const exportScores = async () => {
      exporting.value = true
      try {
        const response = await api.post('/user/export/scores')
        store.dispatch('showSuccess', 'Export started! You will receive a notification when ready.')
        
        // Poll for status
        const taskId = response.data.task_id
        const pollStatus = async () => {
          try {
            const statusResponse = await api.get(`/user/export/status/${taskId}`)
            if (statusResponse.data.status === 'completed') {
              store.dispatch('showSuccess', 'Export completed! Check your email for the download link.')
              exporting.value = false
            } else if (statusResponse.data.status === 'failed') {
              store.dispatch('showError', 'Export failed: ' + statusResponse.data.error)
              exporting.value = false
            } else {
              // Continue polling
              setTimeout(pollStatus, 2000)
            }
          } catch (error) {
            console.error('Error checking export status:', error)
            exporting.value = false
          }
        }
        
        setTimeout(pollStatus, 2000)
      } catch (error) {
        console.error('Error starting export:', error)
        store.dispatch('showError', 'Failed to start export')
        exporting.value = false
      }
    }

    const applyFilters = () => {
      currentPage.value = 1
      fetchScores()
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
        fetchScores()
      }
    }

    const formatTime = (seconds) => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    onMounted(() => {
      fetchScores()
      fetchStats()
      fetchSubjects()
    })

    return {
      scores,
      stats,
      subjects,
      loading,
      exporting,
      currentPage,
      totalPages,
      filters,
      visiblePages,
      fetchScores,
      exportScores,
      applyFilters,
      changePage,
      formatTime,
      formatDate
    }
  }
}
</script>

<style scoped>
.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.badge {
  font-size: 0.75em;
}
</style>
