<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Quiz Information Card -->
        <div class="card shadow-lg">
          <div class="card-header bg-primary text-white">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h3 class="mb-0">
                  <i class="bi bi-question-circle me-2"></i>
                  {{ quiz.title }}
                </h3>
                <p class="mb-0 text-light">{{ quiz.description || 'No description available' }}</p>
              </div>
              <div class="text-end">
                <span class="badge bg-light text-dark fs-6">{{ quiz.questions_count || 0 }} Questions</span>
              </div>
            </div>
          </div>
          
          <div class="card-body">
            <!-- Quiz Details -->
            <div class="row mb-4">
              <div class="col-md-6">
                <h5 class="text-primary mb-3">
                  <i class="bi bi-info-circle me-2"></i>
                  Quiz Details
                </h5>
                <div class="quiz-details">
                  <div class="detail-item">
                    <strong>Subject:</strong> {{ quiz.subject?.name || quiz.subject_name || 'Not specified' }}
                  </div>
                  <div class="detail-item">
                    <strong>Chapter:</strong> {{ quiz.chapter?.name || quiz.chapter_name || 'Not specified' }}
                  </div>
                  <div class="detail-item">
                    <strong>Duration:</strong> {{ formatDuration(quiz.duration_minutes || quiz.duration) }}
                  </div>
                  <div class="detail-item">
                    <strong>Passing Score:</strong> {{ quiz.passing_score || 60 }}%
                  </div>
                  <div class="detail-item">
                    <strong>Max Attempts:</strong> {{ quiz.max_attempts || 'Unlimited' }}
                  </div>
                  <div class="detail-item">
                    <strong>Your Attempts:</strong> {{ quiz.attempts_made || 0 }} / {{ quiz.max_attempts || '∞' }}
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <h5 class="text-success mb-3">
                  <i class="bi bi-clock me-2"></i>
                  Time Information
                </h5>
                <div class="time-info">
                  <div class="detail-item">
                    <strong>Start Date:</strong> {{ formatDate(quiz.start_date) }}
                  </div>
                  <div class="detail-item">
                    <strong>End Date:</strong> {{ formatDate(quiz.end_date) }}
                  </div>
                  <div class="detail-item">
                    <strong>Status:</strong> 
                    <span :class="getStatusBadgeClass(quiz.status)">
                      {{ getStatusText(quiz.status) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Previous Attempts -->
            <div v-if="quiz.previous_scores && quiz.previous_scores.length > 0" class="mb-4">
              <h5 class="text-info mb-3">
                <i class="bi bi-history me-2"></i>
                Your Previous Attempts
              </h5>
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Attempt</th>
                      <th>Score</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="score in quiz.previous_scores" :key="score.attempt">
                      <td>#{{ score.attempt }}</td>
                      <td>
                        <span class="fw-bold" :class="score.passed ? 'text-success' : 'text-danger'">
                          {{ Math.round(score.percentage) }}%
                        </span>
                      </td>
                      <td>
                        <span :class="score.passed ? 'badge bg-success' : 'badge bg-danger'">
                          {{ score.passed ? 'Passed' : 'Failed' }}
                        </span>
                      </td>
                      <td>{{ formatDate(score.completed_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Instructions -->
            <div class="mb-4">
              <h5 class="text-warning mb-3">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Instructions
              </h5>
              <div class="alert alert-info">
                <ul class="mb-0">
                  <li>Read each question carefully before answering</li>
                  <li>You can navigate between questions using the navigation buttons</li>
                  <li>You can review and change your answers before submitting</li>
                  <li>Once submitted, you cannot change your answers</li>
                  <li>Your score will be calculated based on correct answers</li>
                  <li>You need {{ quiz.passing_score }}% to pass this quiz</li>
                  <li>You have {{ quiz.attempts_remaining || 0 }} attempts remaining</li>
                </ul>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
              <button 
                class="btn btn-outline-secondary me-md-2" 
                @click="goBack"
              >
                <i class="bi bi-arrow-left me-2"></i>
                Go Back
              </button>
              
              <button 
                v-if="quiz.can_attempt"
                class="btn btn-success btn-lg" 
                @click="startQuiz"
                :disabled="loading"
              >
                <span v-if="!loading">
                  <i class="bi bi-play-circle me-2"></i>
                  Start Quiz
                </span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Loading...
                </span>
              </button>
              
              <button 
                v-else
                class="btn btn-secondary btn-lg" 
                disabled
              >
                <i class="bi bi-x-circle me-2"></i>
                No Attempts Remaining
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'QuizInfo',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const quiz = ref({})
    const loading = ref(false)

    const fetchQuizInfo = async () => {
      loading.value = true
      try {
        const quizSlug = route.params.quizSlug
        console.log('Fetching quiz info for slug:', quizSlug)
        
        // Try slug first, if it's numeric, also try ID endpoint
        let response
        if (/^\d+$/.test(quizSlug)) {
          // If the parameter is purely numeric, try ID endpoint first
          try {
            response = await api.get(`/user/quizzes/${quizSlug}/info`)
          } catch (idError) {
            // If ID fails, fall back to slug endpoint
            response = await api.get(`/user/quizzes/${quizSlug}/info`)
          }
        } else {
          // If not numeric, use slug endpoint
          response = await api.get(`/user/quizzes/${quizSlug}/info`)
        }
        
        console.log('Quiz info response:', response.data)
        quiz.value = response.data
        console.log('Quiz can_attempt:', quiz.value.can_attempt)
        console.log('Quiz attempts_remaining:', quiz.value.attempts_remaining)
      } catch (error) {
        console.error('Error fetching quiz info:', error)
        store.dispatch('showError', error.response?.data?.error || 'Failed to load quiz information')
        router.push('/subjects')
      } finally {
        loading.value = false
      }
    }

    const startQuiz = () => {
      console.log('Starting quiz for slug:', route.params.quizSlug)
      console.log('Quiz data before navigation:', quiz.value)
      router.push(`/quiz/${route.params.quizSlug}/take`)
    }

    const goBack = () => {
      router.go(-1)
    }

    const formatDuration = (minutes) => {
      if (!minutes) return 'Not specified'
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      if (hours > 0) {
        return `${hours}h ${mins}m`
      }
      return `${mins} minutes`
    }

    const formatDate = (dateString) => {
      if (!dateString || dateString === 'Not specified') return 'Not specified'
      try {
        return new Date(dateString).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (error) {
        console.error('Error formatting date:', dateString, error)
        return 'Not specified'
      }
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'active': return 'badge bg-success'
        case 'upcoming': return 'badge bg-warning'
        case 'expired': return 'badge bg-danger'
        case 'inactive': return 'badge bg-secondary'
        default: return 'badge bg-secondary'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'active': return 'Active'
        case 'upcoming': return 'Upcoming'
        case 'expired': return 'Expired'
        case 'inactive': return 'Inactive'
        default: return 'Unknown'
      }
    }

    onMounted(() => {
      fetchQuizInfo()
    })

    return {
      quiz,
      loading,
      startQuiz,
      goBack,
      formatDuration,
      formatDate,
      getStatusBadgeClass,
      getStatusText
    }
  }
}
</script>

<style scoped>
.quiz-details .detail-item,
.time-info .detail-item {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
}

.detail-item strong {
  color: #495057;
  min-width: 120px;
  display: inline-block;
}

.card-header {
  border-bottom: none;
}

.alert ul {
  padding-left: 1.5rem;
}

.alert li {
  margin-bottom: 0.25rem;
}
</style>
