<template>
  <div class="container">
    <div class="row">
      <div class="col-12">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h1 class="mb-2">Score Details</h1>
            <p class="text-muted mb-0">Detailed score breakdown and analysis</p>
          </div>
          <div>
            <router-link to="/scores" class="btn btn-outline-secondary">
              <i class="bi bi-arrow-left me-2"></i>
              Back to Scores
            </router-link>
          </div>
        </div>

        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="!score" class="text-center py-4">
          <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
          <h4 class="mt-3">Score not found</h4>
          <p class="text-muted">The requested score could not be found.</p>
          <router-link to="/scores" class="btn btn-primary">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Scores
          </router-link>
        </div>

        <div v-else>
          <!-- Score Summary -->
          <div class="row mb-4">
            <div class="col-md-3">
              <div class="card bg-primary text-white">
                <div class="card-body text-center">
                  <h5 class="card-title">Score</h5>
                  <h3 class="mb-0">{{ score.score }}/{{ score.max_score }}</h3>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card" :class="score.passed ? 'bg-success' : 'bg-danger'">
                <div class="card-body text-center text-white">
                  <h5 class="card-title">Percentage</h5>
                  <h3 class="mb-0">{{ score.percentage }}%</h3>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card bg-info text-white">
                <div class="card-body text-center">
                  <h5 class="card-title">Status</h5>
                  <h3 class="mb-0">{{ score.passed ? 'Passed' : 'Failed' }}</h3>
                </div>
              </div>
            </div>
            <div class="col-md-3">
              <div class="card bg-warning text-white">
                <div class="card-body text-center">
                  <h5 class="card-title">Attempt</h5>
                  <h3 class="mb-0">#{{ score.attempt_number }}</h3>
                </div>
              </div>
            </div>
          </div>

          <!-- Quiz Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>
                Quiz Information
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6">
                  <p><strong>Quiz:</strong> {{ score.quiz_title }}</p>
                  <p><strong>Subject:</strong> {{ score.subject_name }}</p>
                  <p><strong>Chapter:</strong> {{ score.chapter_name }}</p>
                </div>
                <div class="col-md-6">
                  <p><strong>Date:</strong> {{ formatDate(score.created_at) }}</p>
                  <p><strong>Time Taken:</strong> {{ formatTime(score.time_taken_seconds) }}</p>
                  <p><strong>Passing Score:</strong> {{ score.passing_score }}%</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Performance Analysis -->
          <div class="row mb-4">
            <div class="col-md-6">
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">
                    <i class="bi bi-graph-up me-2"></i>
                    Performance Analysis
                  </h5>
                </div>
                <div class="card-body">
                  <div class="mb-3">
                    <label class="form-label">Overall Performance</label>
                    <div class="progress mb-2">
                      <div 
                        class="progress-bar" 
                        :class="getScoreColor(score.percentage)"
                        :style="{ width: score.percentage + '%' }"
                      ></div>
                    </div>
                    <small class="text-muted">{{ score.percentage }}% achieved</small>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Time Efficiency</label>
                    <div class="d-flex justify-content-between">
                      <span>Time taken: {{ formatTime(score.time_taken_seconds) }}</span>
                      <span v-if="score.duration_minutes">
                        Available: {{ score.duration_minutes }} minutes
                      </span>
                    </div>
                  </div>

                  <div v-if="score.remarks" class="mb-3">
                    <label class="form-label">Remarks</label>
                    <p class="text-muted mb-0">{{ score.remarks }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-md-6">
              <div class="card">
                <div class="card-header">
                  <h5 class="mb-0">
                    <i class="bi bi-clock-history me-2"></i>
                    Previous Attempts
                  </h5>
                </div>
                <div class="card-body">
                  <div v-if="previousAttempts.length === 0" class="text-center py-3">
                    <i class="bi bi-emoji-smile text-muted"></i>
                    <p class="text-muted mb-0">This is your first attempt!</p>
                  </div>
                  <div v-else>
                    <div 
                      v-for="attempt in previousAttempts" 
                      :key="attempt.id"
                      class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded"
                    >
                      <div>
                        <strong>Attempt {{ attempt.attempt_number }}</strong>
                        <br>
                        <small class="text-muted">{{ formatDate(attempt.created_at) }}</small>
                      </div>
                      <div class="text-end">
                        <span class="badge" :class="attempt.passed ? 'bg-success' : 'bg-danger'">
                          {{ attempt.percentage }}%
                        </span>
                        <br>
                        <small class="text-muted">{{ attempt.score }}/{{ attempt.max_score }}</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Answer Details -->
          <div v-if="score.answers" class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-list-check me-2"></i>
                Answer Details
              </h5>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table">
                  <thead>
                    <tr>
                      <th>Question</th>
                      <th>Your Answer</th>
                      <th>Correct Answer</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(answer, questionId) in score.answers" :key="questionId">
                      <td>
                        <strong>Question {{ questionId }}</strong>
                        <br>
                        <small class="text-muted">{{ getQuestionText(questionId) }}</small>
                      </td>
                      <td>
                        <span class="badge bg-secondary">{{ convertToLetter(answer) }}</span>
                      </td>
                      <td>
                        <span class="badge bg-success">{{ getCorrectAnswer(questionId) }}</span>
                      </td>
                      <td>
                        <span 
                          :class="convertToLetter(answer) === getCorrectAnswer(questionId) ? 'badge bg-success' : 'badge bg-danger'"
                        >
                          {{ convertToLetter(answer) === getCorrectAnswer(questionId) ? 'Correct' : 'Incorrect' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Improvement Tips -->
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-lightbulb me-2"></i>
                Improvement Tips
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6">
                  <h6>What went well:</h6>
                  <ul>
                    <li v-if="score.percentage >= 80">Excellent performance! Keep up the good work.</li>
                    <li v-if="score.percentage >= 60">Good understanding of the material.</li>
                    <li v-if="score.time_taken_seconds < score.duration_minutes * 60 * 0.8">
                      Efficient time management.
                    </li>
                  </ul>
                </div>
                <div class="col-md-6">
                  <h6>Areas for improvement:</h6>
                  <ul>
                    <li v-if="score.percentage < 80">Review the material and retake the quiz.</li>
                    <li v-if="score.time_taken_seconds > score.duration_minutes * 60 * 0.9">
                      Work on time management skills.
                    </li>
                    <li>Focus on questions you answered incorrectly.</li>
                    <li>Practice similar questions to build confidence.</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'ScoreDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    const score = ref(null)
    const previousAttempts = ref([])
    const loading = ref(false)

    const fetchScoreDetail = async () => {
      loading.value = true
      try {
        const response = await api.get(`/user/scores/${route.params.scoreId}`)
        score.value = response.data.score
        previousAttempts.value = response.data.previous_attempts || []
      } catch (error) {
        console.error('Error fetching score details:', error)
        store.dispatch('showError', 'Failed to load score details')
        router.push('/scores')
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatTime = (seconds) => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }

    const getScoreColor = (percentage) => {
      if (percentage >= 90) return 'bg-success'
      if (percentage >= 80) return 'bg-info'
      if (percentage >= 70) return 'bg-warning'
      return 'bg-danger'
    }

    const getQuestionText = (questionId) => {
      // Get question text from the score data
      if (score.value && score.value.question_texts) {
        const text = score.value.question_texts[questionId]
        return text ? text.substring(0, 100) + (text.length > 100 ? '...' : '') : `Question ${questionId}`
      }
      return `Question ${questionId}`
    }

    const getCorrectAnswer = (questionId) => {
      // Get correct answer from the score data
      if (score.value && score.value.correct_answers) {
        return score.value.correct_answers[questionId] || 'N/A'
      }
      return 'N/A'
    }

    const convertToLetter = (numericAnswer) => {
      // Convert numeric answer (0, 1, 2, 3) to letter (A, B, C, D)
      const answerMap = {
        '0': 'A',
        '1': 'B', 
        '2': 'C',
        '3': 'D'
      }
      return answerMap[numericAnswer] || numericAnswer
    }

    onMounted(() => {
      fetchScoreDetail()
    })

    return {
      score,
      previousAttempts,
      loading,
      formatDate,
      formatTime,
      getScoreColor,
      getQuestionText,
      getCorrectAnswer,
      convertToLetter
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
  height: 8px;
}
</style>
