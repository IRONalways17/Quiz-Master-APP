<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-lg-8">
        <!-- Result Card -->
        <div class="card shadow-lg">
          <div class="card-header" :class="resultHeaderClass">
            <div class="text-center">
              <i :class="resultIcon" class="fs-1 mb-3"></i>
              <h2 class="mb-2">{{ resultTitle }}</h2>
              <p class="mb-0">{{ resultMessage }}</p>
            </div>
          </div>
          
          <div class="card-body">
            <!-- Score Summary -->
            <div class="row mb-4">
              <div class="col-md-6">
                <div class="score-card text-center p-4">
                  <h3 class="text-primary mb-2">{{ (score.percentage || 0).toFixed(2) }}%</h3>
                  <p class="text-muted mb-0">Your Score</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="score-card text-center p-4">
                  <h3 class="text-info mb-2">{{ score.score || 0 }}/{{ score.max_score || 0 }}</h3>
                  <p class="text-muted mb-0">Correct Answers</p>
                </div>
              </div>
            </div>

            <!-- Quiz Details -->
            <div class="quiz-details mb-4">
              <h5 class="text-primary mb-3">
                <i class="bi bi-info-circle me-2"></i>
                Quiz Details
              </h5>
              <div class="row">
                <div class="col-md-6">
                  <div class="detail-item">
                    <strong>Quiz:</strong> {{ quiz.title }}
                  </div>
                  <div class="detail-item">
                    <strong>Subject:</strong> {{ quiz.subject_name }}
                  </div>
                  <div class="detail-item">
                    <strong>Chapter:</strong> {{ quiz.chapter_name }}
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="detail-item">
                    <strong>Attempt:</strong> #{{ score.attempt_number }}
                  </div>
                  <div class="detail-item">
                    <strong>Time Taken:</strong> {{ formatTime(score.time_taken_seconds) }}
                  </div>
                  <div class="detail-item">
                    <strong>Passing Score:</strong> {{ quiz.passing_score }}%
                  </div>
                </div>
              </div>
            </div>

            <!-- Performance Analysis -->
            <div class="performance-analysis mb-4">
              <h5 class="text-success mb-3">
                <i class="bi bi-graph-up me-2"></i>
                Performance Analysis
              </h5>
              <div class="progress mb-3">
                <div 
                  class="progress-bar" 
                  :class="progressBarClass"
                  :style="{ width: (score.percentage || 0).toFixed(2) + '%' }"
                >
                  {{ (score.percentage || 0).toFixed(2) }}%
                </div>
              </div>
              <div class="row text-center">
                <div class="col-md-4">
                  <div class="stat-item">
                    <h6 class="text-success">{{ score.score || 0 }}</h6>
                    <small class="text-muted">Correct</small>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="stat-item">
                    <h6 class="text-danger">{{ (score.max_score || 0) - (score.score || 0) }}</h6>
                    <small class="text-muted">Incorrect</small>
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="stat-item">
                    <h6 class="text-info">{{ score.max_score || 0 }}</h6>
                    <small class="text-muted">Total</small>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="d-grid gap-2 d-md-flex justify-content-md-center">
              <router-link to="/subjects" class="btn btn-outline-primary">
                <i class="bi bi-book me-2"></i>
                Take Another Quiz
              </router-link>
              
              <router-link to="/scores" class="btn btn-outline-info">
                <i class="bi bi-bar-chart me-2"></i>
                View All Scores
              </router-link>
              
              <router-link to="/dashboard" class="btn btn-outline-success">
                <i class="bi bi-speedometer2 me-2"></i>
                Go to Dashboard
              </router-link>
            </div>
          </div>
        </div>

        <!-- Previous Attempts -->
        <div v-if="previousAttempts.length > 0" class="card mt-4">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-history me-2"></i>
              Your Previous Attempts
            </h5>
          </div>
          <div class="card-body">
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
                  <tr v-for="attempt in previousAttempts" :key="attempt.id">
                    <td>#{{ attempt.attempt_number }}</td>
                    <td>
                      <span class="fw-bold" :class="attempt.passed ? 'text-success' : 'text-danger'">
                        {{ attempt.percentage }}%
                      </span>
                    </td>
                    <td>
                      <span :class="attempt.passed ? 'badge bg-success' : 'badge bg-danger'">
                        {{ attempt.passed ? 'Passed' : 'Failed' }}
                      </span>
                    </td>
                    <td>{{ formatDate(attempt.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'QuizResult',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const quiz = ref({})
    const score = ref({})
    const previousAttempts = ref([])
    const loading = ref(true)

    const resultTitle = computed(() => {
      if (score.value.passed) {
        return 'Congratulations!'
      }
      return 'Quiz Completed'
    })

    const resultMessage = computed(() => {
      if (score.value.passed) {
        return 'You have successfully passed this quiz!'
      }
      return 'Keep practicing to improve your score.'
    })

    const resultHeaderClass = computed(() => {
      return score.value.passed ? 'bg-success text-white' : 'bg-warning text-dark'
    })

    const resultIcon = computed(() => {
      return score.value.passed ? 'bi bi-check-circle' : 'bi bi-exclamation-triangle'
    })

    const progressBarClass = computed(() => {
      const percentage = score.value.percentage || 0
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-warning'
      return 'bg-danger'
    })

    const fetchQuizResult = async () => {
      try {
        const response = await api.get(`/user/quizzes/${route.params.quizSlug}/result`)
        quiz.value = response.data.quiz
        score.value = response.data.score
        previousAttempts.value = response.data.previous_attempts || []
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to load quiz result')
        router.push('/subjects')
      } finally {
        loading.value = false
      }
    }

    const formatTime = (seconds) => {
      if (!seconds) return '0:00'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      fetchQuizResult()
    })

    return {
      quiz,
      score,
      previousAttempts,
      loading,
      resultTitle,
      resultMessage,
      resultHeaderClass,
      resultIcon,
      progressBarClass,
      formatTime,
      formatDate
    }
  }
}
</script>

<style scoped>
.score-card {
  background: #f8f9fa;
  border-radius: 0.5rem;
  border: 1px solid #dee2e6;
}

.detail-item {
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
}

.detail-item strong {
  color: #495057;
  min-width: 120px;
  display: inline-block;
}

.stat-item {
  padding: 0.5rem;
}

.progress {
  height: 2rem;
}

.progress-bar {
  line-height: 2rem;
  font-weight: bold;
}
</style>
