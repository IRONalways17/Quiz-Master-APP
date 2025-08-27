<template>
  <div class="container">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading quiz...</p>
    </div>

    <div v-else-if="quiz" class="quiz-container">
      <!-- Quiz Header -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h3 class="mb-0">{{ quiz.title }}</h3>
              <small>{{ quiz.description }}</small>
            </div>
            <div class="text-end">
              <div class="timer-display">
                <i class="bi bi-clock me-2"></i>
                <span class="fw-bold">{{ formatTime(timeRemaining) }}</span>
              </div>
              <div class="progress-info">
                Question {{ currentQuestionIndex + 1 }} of {{ quiz.questions.length }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Question Display -->
      <div v-if="currentQuestion" class="card">
        <div class="card-body">
          <div class="question-header mb-4">
            <h5 class="text-primary">
              Question {{ currentQuestionIndex + 1 }} of {{ quiz.questions.length }}
            </h5>
            <p class="text-muted">{{ currentQuestion.question_text }}</p>
          </div>

          <!-- Options -->
          <div class="options-container">
            <div 
              v-for="(option, index) in currentQuestion.options" 
              :key="index"
              class="option-item mb-3"
            >
              <input 
                type="radio" 
                :id="`option-${index}`"
                :name="`question-${currentQuestion.id}`"
                :value="index"
                v-model="answers[currentQuestion.id]"
                class="form-check-input"
              >
              <label 
                :for="`option-${index}`"
                class="form-check-label option-label"
              >
                {{ option }}
              </label>
            </div>
          </div>

          <!-- Navigation -->
          <div class="navigation-buttons mt-4">
            <div class="d-flex justify-content-between">
              <button 
                class="btn btn-outline-secondary"
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
              >
                <i class="bi bi-arrow-left me-2"></i>
                Previous
              </button>

              <div class="question-indicators">
                <button 
                  v-for="(question, index) in quiz.questions"
                  :key="index"
                  class="btn btn-sm me-1"
                  :class="getQuestionButtonClass(index)"
                  @click="goToQuestion(index)"
                >
                  {{ index + 1 }}
                </button>
              </div>

              <button 
                v-if="currentQuestionIndex < quiz.questions.length - 1"
                class="btn btn-outline-primary"
                @click="nextQuestion"
              >
                Next
                <i class="bi bi-arrow-right ms-2"></i>
              </button>

              <button 
                v-else
                class="btn btn-success"
                @click="submitQuiz"
                :disabled="submitting"
              >
                <span v-if="!submitting">
                  <i class="bi bi-check-circle me-2"></i>
                  Submit Quiz
                </span>
                <span v-else>
                  <span class="spinner-border spinner-border-sm me-2"></span>
                  Submitting...
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Quiz Summary Modal -->
      <div class="modal fade" id="quizSummaryModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Quiz Summary</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="summary-stats mb-4">
                <div class="row text-center">
                  <div class="col-md-4">
                    <h4 class="text-primary">{{ answeredCount }}</h4>
                    <small class="text-muted">Questions Answered</small>
                  </div>
                  <div class="col-md-4">
                    <h4 class="text-warning">{{ unansweredCount }}</h4>
                    <small class="text-muted">Questions Unanswered</small>
                  </div>
                  <div class="col-md-4">
                    <h4 class="text-info">{{ quiz.questions.length }}</h4>
                    <small class="text-muted">Total Questions</small>
                  </div>
                </div>
              </div>

              <div class="question-summary">
                <h6>Question Status:</h6>
                <div class="row">
                  <div 
                    v-for="(question, index) in quiz.questions"
                    :key="index"
                    class="col-md-2 mb-2"
                  >
                    <button 
                      class="btn btn-sm w-100"
                      :class="getSummaryButtonClass(index)"
                      @click="goToQuestion(index)"
                      data-bs-dismiss="modal"
                    >
                      {{ index + 1 }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Continue Quiz
              </button>
              <button 
                type="button" 
                class="btn btn-success"
                @click="submitQuiz"
                :disabled="submitting"
              >
                Submit Quiz
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-5">
      <i class="bi bi-exclamation-triangle text-warning fs-1"></i>
      <h4 class="mt-3">Quiz Not Found</h4>
      <p class="text-muted">The quiz you're looking for doesn't exist or is not available.</p>
      <router-link to="/subjects" class="btn btn-primary">
        <i class="bi bi-arrow-left me-2"></i>
        Back to Subjects
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'TakeQuiz',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const quiz = ref(null)
    const loading = ref(true)
    const submitting = ref(false)
    const currentQuestionIndex = ref(0)
    const answers = ref({})
    const timeRemaining = ref(0)
    const timer = ref(null)

    const currentQuestion = computed(() => {
      if (!quiz.value || !quiz.value.questions) return null
      return quiz.value.questions[currentQuestionIndex.value]
    })

    const answeredCount = computed(() => {
      return Object.keys(answers.value).length
    })

    const unansweredCount = computed(() => {
      return quiz.value?.questions?.length - answeredCount.value || 0
    })

    const fetchQuiz = async () => {
      try {
        console.log('Fetching quiz for slug:', route.params.quizSlug)
        const response = await api.get(`/user/quizzes/${route.params.quizSlug}/take`)
        console.log('Quiz API Response:', response.data)
        quiz.value = response.data
        console.log('Quiz data:', quiz.value)
        console.log('Questions count:', quiz.value?.questions?.length)
        timeRemaining.value = quiz.value.duration_minutes * 60
        startTimer()
      } catch (error) {
        console.error('Error fetching quiz:', error)
        console.error('Error response:', error.response?.data)
        store.dispatch('showError', error.response?.data?.error || 'Failed to load quiz')
        router.push('/subjects')
      } finally {
        loading.value = false
      }
    }

    const startTimer = () => {
      timer.value = setInterval(() => {
        if (timeRemaining.value > 0) {
          timeRemaining.value--
        } else {
          submitQuiz()
        }
      }, 1000)
    }

    const stopTimer = () => {
      if (timer.value) {
        clearInterval(timer.value)
        timer.value = null
      }
    }

    const formatTime = (seconds) => {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
    }

    const nextQuestion = () => {
      if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
        currentQuestionIndex.value++
      }
    }

    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }

    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
    }

    const getQuestionButtonClass = (index) => {
      if (index === currentQuestionIndex.value) {
        return 'btn-primary'
      }
      if (answers.value[quiz.value.questions[index]?.id] !== undefined && answers.value[quiz.value.questions[index]?.id] !== null) {
        return 'btn-success'
      }
      return 'btn-outline-secondary'
    }

    const getSummaryButtonClass = (index) => {
      if (answers.value[quiz.value.questions[index]?.id] !== undefined && answers.value[quiz.value.questions[index]?.id] !== null) {
        return 'btn-success'
      }
      return 'btn-outline-secondary'
    }

    const submitQuiz = async () => {
      if (submitting.value) return

      // Check if all questions are answered
      const unansweredQuestions = quiz.value.questions.filter(q => answers.value[q.id] === undefined || answers.value[q.id] === null)
      if (unansweredQuestions.length > 0) {
        const confirmed = confirm(`You have ${unansweredQuestions.length} unanswered questions. Are you sure you want to submit?`)
        if (!confirmed) return
      }

      submitting.value = true
      try {
        const response = await api.post(`/user/quizzes/${route.params.quizSlug}/submit`, {
          answers: answers.value,
          time_taken: quiz.value.duration_minutes * 60 - timeRemaining.value
        })
        
        stopTimer()
        store.dispatch('showSuccess', 'Quiz submitted successfully!')
        router.push(`/quiz/${route.params.quizSlug}/result`)
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to submit quiz')
      } finally {
        submitting.value = false
      }
    }

    onMounted(() => {
      fetchQuiz()
    })

    onUnmounted(() => {
      stopTimer()
    })

    return {
      quiz,
      loading,
      submitting,
      currentQuestion,
      currentQuestionIndex,
      answers,
      timeRemaining,
      answeredCount,
      unansweredCount,
      nextQuestion,
      previousQuestion,
      goToQuestion,
      submitQuiz,
      formatTime,
      getQuestionButtonClass,
      getSummaryButtonClass
    }
  }
}
</script>

<style scoped>
.quiz-container {
  max-width: 800px;
  margin: 0 auto;
}

.timer-display {
  font-size: 1.2rem;
}

.progress-info {
  font-size: 0.9rem;
  opacity: 0.8;
}

.question-header {
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 1rem;
}

.options-container {
  margin: 2rem 0;
}

.option-item {
  border: 1px solid #dee2e6;
  border-radius: 0.5rem;
  padding: 1rem;
  transition: all 0.2s;
}

.option-item:hover {
  border-color: #0d6efd;
  background-color: #f8f9fa;
}

.option-label {
  cursor: pointer;
  margin-left: 0.5rem;
  font-size: 1rem;
}

.navigation-buttons {
  border-top: 1px solid #dee2e6;
  padding-top: 1rem;
}

.question-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.question-indicators .btn {
  min-width: 2.5rem;
}

@media (max-width: 768px) {
  .navigation-buttons .d-flex {
    flex-direction: column;
    gap: 1rem;
  }
  
  .question-indicators {
    justify-content: center;
  }
}
</style>
