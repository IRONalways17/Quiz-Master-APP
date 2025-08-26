<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-0">
            <i class="bi bi-list-ul me-2"></i>
            Questions Management
          </h1>
          <p class="text-muted mb-0" v-if="currentQuiz">
            Quiz: <strong>{{ currentQuiz.title }}</strong> | 
            Chapter: <strong>{{ currentChapter?.name }}</strong> | 
            Subject: <strong>{{ currentSubject?.name }}</strong>
          </p>
        </div>
        <div>
          <button class="btn btn-outline-secondary me-2" @click="goBack">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Quiz
          </button>
          <button class="btn btn-primary" @click="showAddModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Add Question
          </button>
        </div>
      </div>
    </div>

    <!-- Search and Filters -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            placeholder="Search questions..."
            v-model="searchQuery"
            @input="filterQuestions"
          >
        </div>
      </div>
      <div class="col-md-6 text-end">
        <button class="btn btn-outline-secondary me-2" @click="refreshData">
          <i class="bi bi-arrow-clockwise me-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Questions List -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <div v-for="(question, index) in filteredQuestions" :key="question.id" class="question-item mb-4">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <h5 class="mb-0">
                  <span class="badge bg-primary me-2">{{ index + 1 }}</span>
                  {{ question.question_text }}
                </h5>
                <div class="btn-group btn-group-sm">
                  <button class="btn btn-outline-primary" @click="editQuestion(question)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-outline-danger" @click="deleteQuestion(question)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </div>
              
              <div class="options-list">
                <div class="row">
                  <div class="col-md-6" v-for="(option, optIndex) in getOptions(question)" :key="optIndex">
                    <div class="option-item p-2 mb-2" :class="getOptionClass(question, optIndex)">
                      <span class="option-label me-2">{{ String.fromCharCode(65 + optIndex) }}.</span>
                      {{ option }}
                      <i v-if="isCorrectAnswer(question, optIndex)" class="bi bi-check-circle-fill text-success ms-2"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="filteredQuestions.length === 0" class="text-center py-5">
              <i class="bi bi-question-circle fs-1 text-muted"></i>
              <h4 class="text-muted mt-3">No Questions Added Yet</h4>
              <p class="text-muted">This quiz needs questions before students can take it.</p>
              <button class="btn btn-primary btn-lg" @click="showAddModal = true">
                <i class="bi bi-plus-circle me-2"></i>
                Add First Question
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Question Modal -->
    <div class="modal fade" :class="{ show: showAddModal || showEditModal }" 
         :style="{ display: (showAddModal || showEditModal) ? 'block' : 'none' }" 
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ showEditModal ? 'Edit Question' : 'Add New Question' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveQuestion">
            <div class="modal-body">
              <div class="mb-3">
                <label for="questionText" class="form-label">Question Text *</label>
                <textarea 
                  class="form-control" 
                  id="questionText"
                  v-model="questionForm.question_text"
                  required
                  rows="3"
                  placeholder="Enter the question"
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Options *</label>
                <div v-for="(option, index) in questionForm.options" :key="index" class="mb-2">
                  <div class="input-group">
                    <span class="input-group-text">{{ String.fromCharCode(65 + index) }}</span>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="questionForm.options[index]"
                      :placeholder="`Option ${String.fromCharCode(65 + index)}`"
                      required
                    >
                    <div class="input-group-text">
                      <input 
                        type="radio" 
                        :name="'correct_answer'" 
                        :value="index.toString()"
                        v-model="questionForm.correct_answer"
                        class="form-check-input"
                        required
                      >
                      <label class="ms-1 mb-0">Correct</label>
                    </div>
                  </div>
                </div>
                
                <div class="mt-2">
                  <button type="button" class="btn btn-sm btn-outline-secondary me-2" @click="addOption" :disabled="questionForm.options.length >= 6">
                    <i class="bi bi-plus-circle me-1"></i>
                    Add Option
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-danger" @click="removeOption" :disabled="questionForm.options.length <= 2">
                    <i class="bi bi-dash-circle me-1"></i>
                    Remove Option
                  </button>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="questionExplanation" class="form-label">Explanation (Optional)</label>
                <textarea 
                  class="form-control" 
                  id="questionExplanation"
                  v-model="questionForm.explanation"
                  rows="2"
                  placeholder="Explain the correct answer"
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label for="questionPoints" class="form-label">Points</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="questionPoints"
                  v-model="questionForm.points"
                  min="1"
                  max="10"
                  placeholder="1"
                >
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ showEditModal ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div class="modal-backdrop fade" :class="{ show: showAddModal || showEditModal }" 
         v-if="showAddModal || showEditModal"></div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'Questions',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const questions = ref([])
    const filteredQuestions = ref([])
    const currentQuiz = ref(null)
    const currentChapter = ref(null)
    const currentSubject = ref(null)
    const searchQuery = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const loading = ref(false)
    
    const questionForm = reactive({
      id: null,
      question_text: '',
      options: ['', '', '', ''],
      correct_answer: '0',
      explanation: '',
      points: 1,
      quiz_id: null
    })

    const quizId = computed(() => route.params.quizId)

    const fetchQuiz = async () => {
      try {
        const response = await api.get(`/admin/quizzes/${quizId.value}`)
        currentQuiz.value = response.data.quiz
        currentChapter.value = response.data.chapter
        currentSubject.value = response.data.subject
        questionForm.quiz_id = currentQuiz.value.id
      } catch (error) {
        store.dispatch('showError', 'Failed to load quiz details')
        router.push('/admin/subjects')
      }
    }

    const fetchQuestions = async () => {
      try {
        const response = await api.get(`/admin/quizzes/${quizId.value}/questions`)
        questions.value = response.data.questions
        filteredQuestions.value = questions.value
      } catch (error) {
        store.dispatch('showError', 'Failed to load questions')
      }
    }

    const filterQuestions = () => {
      if (!searchQuery.value) {
        filteredQuestions.value = questions.value
        return
      }
      
      const query = searchQuery.value.toLowerCase()
      filteredQuestions.value = questions.value.filter(question =>
        question.question_text.toLowerCase().includes(query)
      )
    }

    const editQuestion = (question) => {
      questionForm.id = question.id
      questionForm.question_text = question.question_text
      questionForm.options = [...question.options]
      questionForm.correct_answer = question.correct_answer.toString()
      questionForm.explanation = question.explanation || ''
      questionForm.points = question.points || 1
      showEditModal.value = true
    }

    const saveQuestion = async () => {
      loading.value = true
      try {
        // Validate form
        if (!questionForm.question_text.trim()) {
          store.dispatch('showError', 'Question text is required')
          return
        }
        
        if (questionForm.options.some(opt => !opt.trim())) {
          store.dispatch('showError', 'All options must be filled')
          return
        }
        
        if (!questionForm.correct_answer && questionForm.correct_answer !== '0') {
          store.dispatch('showError', 'Please select the correct answer')
          return
        }

        const questionData = {
          quiz_id: questionForm.quiz_id,
          question_text: questionForm.question_text,
          options: questionForm.options.filter(opt => opt.trim()),
          correct_answer: questionForm.correct_answer,
          explanation: questionForm.explanation,
          points: questionForm.points
        }
        
        if (showEditModal.value) {
          await api.put(`/admin/questions/${questionForm.id}`, questionData)
          store.dispatch('showSuccess', 'Question updated successfully')
        } else {
          await api.post('/admin/questions', questionData)
          store.dispatch('showSuccess', 'Question created successfully')
        }
        
        closeModal()
        fetchQuestions()
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to save question')
      } finally {
        loading.value = false
      }
    }

    const deleteQuestion = async (question) => {
      if (!confirm(`Are you sure you want to delete this question?`)) {
        return
      }
      
      try {
        await api.delete(`/admin/questions/${question.id}`)
        store.dispatch('showSuccess', 'Question deleted successfully')
        fetchQuestions()
      } catch (error) {
        store.dispatch('showError', 'Failed to delete question')
      }
    }

    const addOption = () => {
      if (questionForm.options.length < 6) {
        questionForm.options.push('')
      }
    }

    const removeOption = () => {
      if (questionForm.options.length > 2) {
        questionForm.options.pop()
        // Reset correct answer if it was the last option
        if (questionForm.correct_answer === (questionForm.options.length).toString()) {
          questionForm.correct_answer = '0'
        }
      }
    }

    const goBack = () => {
      if (currentChapter.value?.id) {
        router.push(`/admin/chapters/${currentChapter.value.id}/quizzes`)
      } else {
        router.push('/admin/quizzes')
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      showEditModal.value = false
      questionForm.id = null
      questionForm.question_text = ''
      questionForm.options = ['', '', '', '']
      questionForm.correct_answer = '0'
      questionForm.explanation = ''
      questionForm.points = 1
    }

    const refreshData = () => {
      fetchQuiz()
      fetchQuestions()
    }

    const getOptions = (question) => {
      return question.options || []
    }

    const isCorrectAnswer = (question, index) => {
      return parseInt(question.correct_answer) === index
    }

    const getOptionClass = (question, index) => {
      if (isCorrectAnswer(question, index)) {
        return 'bg-success bg-opacity-10 border border-success'
      }
      return 'bg-light'
    }

    onMounted(() => {
      if (quizId.value) {
        fetchQuiz()
        fetchQuestions()
      } else {
        router.push('/admin/subjects')
      }
    })

    return {
      questions,
      filteredQuestions,
      currentQuiz,
      currentChapter,
      currentSubject,
      searchQuery,
      showAddModal,
      showEditModal,
      loading,
      questionForm,
      editQuestion,
      saveQuestion,
      deleteQuestion,
      goBack,
      closeModal,
      refreshData,
      filterQuestions,
      getOptions,
      isCorrectAnswer,
      getOptionClass,
      addOption,
      removeOption
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

.question-item {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  background-color: #fff;
}

.question-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.options-list {
  margin-top: 1rem;
}

.option-item {
  border-radius: 6px;
  transition: all 0.2s;
}

.option-item:hover {
  background-color: #f8f9fa;
}
</style>
