<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 class="mb-2">Leaderboard</h1>
            <p class="text-muted mb-0">See top performers across all quizzes</p>
          </div>
          <div>
            <select v-model="selectedSubject" class="form-select" @change="fetchLeaderboard">
              <option value="">Global Leaderboard</option>
              <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                {{ subject.name }} Leaderboard
              </option>
            </select>
          </div>
        </div>

        <!-- Stats Summary -->
        <div class="row mb-4">
          <div class="col-md-4">
            <div class="card bg-primary text-white">
              <div class="card-body text-center">
                <h5 class="card-title">Total Participants</h5>
                <h3 class="mb-0">{{ leaderboard.length }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card bg-success text-white">
              <div class="card-body text-center">
                <h5 class="card-title">Your Rank</h5>
                <h3 class="mb-0">{{ userRank || 'N/A' }}</h3>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card bg-info text-white">
              <div class="card-body text-center">
                <h5 class="card-title">Your Average</h5>
                <h3 class="mb-0">{{ userAverage || 0 }}%</h3>
              </div>
            </div>
          </div>
        </div>

        <!-- Leaderboard Table -->
        <div class="card">
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="leaderboard.length === 0" class="text-center py-4">
              <i class="bi bi-trophy display-1 text-muted"></i>
              <h4 class="mt-3">No leaderboard data</h4>
              <p class="text-muted">No one has taken quizzes yet.</p>
            </div>

            <div v-else>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th width="80">Rank</th>
                      <th>User</th>
                      <th>Total Attempts</th>
                      <th>Average Score</th>
                      <th>Passed Attempts</th>
                      <th>Pass Rate</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(entry, index) in leaderboard" 
                      :key="index"
                      :class="{ 'table-warning': entry.is_current_user }"
                    >
                      <td>
                        <div class="d-flex align-items-center">
                          <span 
                            v-if="entry.rank <= 3" 
                            class="me-2"
                            :class="getRankIcon(entry.rank)"
                          ></span>
                          <span class="badge bg-secondary">{{ entry.rank }}</span>
                        </div>
                      </td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="avatar me-3">
                            <i class="bi bi-person-circle fs-4"></i>
                          </div>
                          <div>
                            <strong>{{ entry.full_name }}</strong>
                            <br>
                            <small class="text-muted">{{ entry.email }}</small>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span class="badge bg-primary">{{ entry.total_attempts }}</span>
                      </td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="progress me-2" style="width: 60px; height: 8px;">
                            <div 
                              class="progress-bar" 
                              :class="getScoreColor(entry.average_score)"
                              :style="{ width: Math.min(entry.average_score, 100) + '%' }"
                            ></div>
                          </div>
                          <span class="fw-bold">{{ entry.average_score }}%</span>
                        </div>
                      </td>
                      <td>
                        <span class="badge bg-success">{{ entry.passed_attempts }}</span>
                      </td>
                      <td>
                        <span class="badge" :class="getPassRateColor(entry.pass_rate)">
                          {{ entry.pass_rate }}%
                        </span>
                      </td>
                      <td>
                        <button 
                          v-if="entry.is_current_user"
                          class="btn btn-sm btn-outline-primary"
                          @click="viewMyScores"
                        >
                          <i class="bi bi-eye me-1"></i>
                          My Scores
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Legend -->
              <div class="mt-3">
                <small class="text-muted">
                  <i class="bi bi-trophy-fill text-warning me-1"></i> Top 3 performers
                  <span class="ms-3">
                    <i class="bi bi-person-circle text-primary me-1"></i> Your position
                  </span>
                </small>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Tips -->
        <div class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-lightbulb me-2"></i>
              Tips to Improve Your Ranking
            </h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <ul class="list-unstyled">
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Take quizzes regularly to build consistency
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Review your mistakes and learn from them
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Focus on subjects where you need improvement
                  </li>
                </ul>
              </div>
              <div class="col-md-6">
                <ul class="list-unstyled">
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Practice time management during quizzes
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Read questions carefully before answering
                  </li>
                  <li class="mb-2">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    Don't rush - accuracy is more important than speed
                  </li>
                </ul>
              </div>
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
import { useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'Leaderboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    const leaderboard = ref([])
    const subjects = ref([])
    const selectedSubject = ref('')
    const loading = ref(false)
    const userRank = ref(null)
    const userAverage = ref(null)

    const fetchLeaderboard = async () => {
      loading.value = true
      try {
        let response
        if (selectedSubject.value) {
          response = await api.get(`/user/leaderboard/subject/${selectedSubject.value}`)
        } else {
          response = await api.get('/user/leaderboard')
        }
        
        leaderboard.value = response.data.leaderboard.map((entry, index) => ({
          ...entry,
          is_current_user: entry.email === store.state.auth.user?.email
        }))
        
        // Find current user's rank and average
        const currentUser = leaderboard.value.find(entry => entry.is_current_user)
        if (currentUser) {
          userRank.value = currentUser.rank
          userAverage.value = currentUser.average_score
        }
      } catch (error) {
        console.error('Error fetching leaderboard:', error)
        store.dispatch('showError', 'Failed to load leaderboard')
      } finally {
        loading.value = false
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

    const getRankIcon = (rank) => {
      switch (rank) {
        case 1: return 'bi-trophy-fill text-warning'
        case 2: return 'bi-award-fill text-secondary'
        case 3: return 'bi-award-fill text-bronze'
        default: return ''
      }
    }

    const getScoreColor = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 80) return 'bg-info'
      if (score >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const getPassRateColor = (rate) => {
      if (rate >= 90) return 'bg-success'
      if (rate >= 80) return 'bg-info'
      if (rate >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const viewMyScores = () => {
      router.push('/scores')
    }

    onMounted(() => {
      fetchLeaderboard()
      fetchSubjects()
    })

    return {
      leaderboard,
      subjects,
      selectedSubject,
      loading,
      userRank,
      userAverage,
      fetchLeaderboard,
      getRankIcon,
      getScoreColor,
      getPassRateColor,
      viewMyScores
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

.progress {
  background-color: #e9ecef;
}

.avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 50%;
}

.text-bronze {
  color: #cd7f32 !important;
}

.table-warning {
  background-color: rgba(255, 193, 7, 0.1) !important;
}
</style>
