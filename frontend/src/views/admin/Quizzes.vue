<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-0">
            <i class="bi bi-question-circle me-2"></i>
            Quizzes Management
          </h1>
          <p class="text-muted mb-0" v-if="currentChapter">
            Chapter: <strong>{{ currentChapter.name }}</strong> | 
            Subject: <strong>{{ currentSubject?.name }}</strong>
          </p>
          <p class="text-muted mb-0" v-else>
            All Quizzes
          </p>
        </div>
        <div>
          <button v-if="currentChapter" class="btn btn-outline-secondary me-2" @click="goBack">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Chapters
          </button>
          <button v-else class="btn btn-outline-secondary me-2" @click="goToSubjects">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Subjects
          </button>
          <button class="btn btn-primary" @click="showAddModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Create Quiz
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
            placeholder="Search quizzes..."
            v-model="searchQuery"
            @input="filterQuizzes"
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

    <!-- Quizzes Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Chapter</th>
                <th>Duration</th>
                <th>Questions</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quiz in filteredQuizzes" :key="quiz.id">
                <td>{{ quiz.id }}</td>
                <td>
                  <strong>{{ quiz.title }}</strong>
                  <br>
                  <small class="text-muted">{{ quiz.description || 'No description' }}</small>
                </td>
                <td v-if="!currentChapter">
                  <span class="badge bg-info">{{ quiz.chapter_name || 'Unknown' }}</span>
                </td>
                <td>
                  <span class="badge bg-info">{{ formatDuration(quiz.duration_minutes || quiz.duration) }}</span>
                </td>
                <td>
                  <span class="badge bg-success">{{ quiz.questions_count || 0 }} questions</span>
                </td>
                <td>
                  <span :class="getStatusBadgeClass(quiz.status)">
                    {{ getStatusText(quiz.status) }}
                  </span>
                </td>
                <td>{{ formatDate(quiz.start_date) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editQuiz(quiz)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-info" @click="viewQuestions(quiz)">
                      <i class="bi bi-list-ul"></i>
                    </button>
                    <button class="btn btn-outline-warning" @click="viewResults(quiz)">
                      <i class="bi bi-bar-chart"></i>
                    </button>
                    <button class="btn btn-outline-danger" @click="deleteQuiz(quiz)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredQuizzes.length === 0">
                <td colspan="8" class="text-center py-4">
                  <i class="bi bi-inbox fs-1 text-muted"></i>
                  <p class="text-muted mt-2">No quizzes found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Quiz Modal -->
    <div class="modal fade" :class="{ show: showAddModal || showEditModal }" 
         :style="{ display: (showAddModal || showEditModal) ? 'block' : 'none' }" 
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ showEditModal ? 'Edit Quiz' : 'Create New Quiz' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveQuiz">
            <div class="modal-body">
              <div class="row">
                <div class="col-md-8">
                  <div class="mb-3">
                    <label for="quizTitle" class="form-label">Quiz Title *</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="quizTitle"
                      v-model="quizForm.title"
                      required
                      placeholder="Enter quiz title"
                    >
                  </div>
                </div>
                <div class="col-md-4">
                  <div class="mb-3">
                    <label for="quizDuration" class="form-label">Duration (minutes) *</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      id="quizDuration"
                      v-model="quizForm.duration_minutes"
                      required
                      min="1"
                      max="180"
                      placeholder="30"
                    >
                  </div>
                </div>
              </div>
              
              <!-- Subject and Chapter Selection (only show when not in chapter-specific context) -->
              <div v-if="!chapterId">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="quizSubject" class="form-label">Subject *</label>
                      <select class="form-select" id="quizSubject" v-model="selectedSubjectId" @change="onSubjectChange" required>
                        <option value="">Select a subject</option>
                        <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                          {{ subject.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="quizChapter" class="form-label">Chapter *</label>
                      <select class="form-select" id="quizChapter" v-model="quizForm.chapter_id" required :disabled="!selectedSubjectId">
                        <option value="">Select a chapter</option>
                        <option v-for="chapter in filteredChapters" :key="chapter.id" :value="chapter.id">
                          {{ chapter.name }}
                        </option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="quizStartDate" class="form-label">Start Date *</label>
                    <input 
                      type="datetime-local" 
                      class="form-control" 
                      id="quizStartDate"
                      v-model="quizForm.start_date"
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="quizEndDate" class="form-label">End Date *</label>
                    <input 
                      type="datetime-local" 
                      class="form-control" 
                      id="quizEndDate"
                      v-model="quizForm.end_date"
                      required
                    >
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="quizDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="quizDescription"
                  v-model="quizForm.description"
                  rows="3"
                  placeholder="Enter quiz description"
                ></textarea>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="quizStatus" class="form-label">Status</label>
                    <select class="form-select" id="quizStatus" v-model="quizForm.status">
                      <option value="draft">Draft</option>
                      <option value="active">Active</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="quizPassingScore" class="form-label">Passing Score (%)</label>
                    <input 
                      type="number" 
                      class="form-control" 
                      id="quizPassingScore"
                      v-model="quizForm.passing_score"
                      min="0"
                      max="100"
                      placeholder="60"
                    >
                  </div>
                </div>
              </div>
              
              <!-- Question Management Section (only show in edit mode) -->
              <div v-if="showEditModal && quizForm.id" class="mb-3">
                <div class="card">
                  <div class="card-header">
                    <h6 class="mb-0">
                      <i class="bi bi-list-ul me-2"></i>
                      Questions Management
                    </h6>
                  </div>
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                      <span class="text-muted">Manage questions for this quiz</span>
                      <button type="button" class="btn btn-sm btn-primary" @click="addQuestion">
                        <i class="bi bi-plus-circle me-1"></i>
                        Add Question
                      </button>
                    </div>
                    
                    <!-- Questions List -->
                    <div v-if="quizQuestions.length > 0" class="mb-3">
                      <h6 class="mb-2">Current Questions ({{ quizQuestions.length }})</h6>
                      <div v-for="(question, index) in quizQuestions" :key="question.id" class="question-item border rounded p-3 mb-2">
                        <div class="d-flex justify-content-between align-items-start">
                          <div class="flex-grow-1">
                            <h6 class="mb-2">
                              <span class="badge bg-primary me-2">{{ index + 1 }}</span>
                              {{ question.question_text }}
                            </h6>
                            <div class="options-list">
                              <div v-for="(option, optIndex) in question.options" :key="optIndex" class="option-item p-2 mb-1" :class="getOptionClass(question, optIndex)">
                                <span class="option-label me-2">{{ String.fromCharCode(65 + optIndex) }}.</span>
                                {{ option }}
                                <i v-if="isCorrectAnswer(question, optIndex)" class="bi bi-check-circle-fill text-success ms-2"></i>
                              </div>
                            </div>
                          </div>
                          <div class="btn-group btn-group-sm ms-2">
                            <button class="btn btn-outline-primary" @click="editQuestion(question)">
                              <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-outline-danger" @click="deleteQuestion(question)">
                              <i class="bi bi-trash"></i>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div v-else class="alert alert-info">
                      <i class="bi bi-info-circle me-2"></i>
                      No questions added yet. Click "Add Question" to start.
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="quizRemarks" class="form-label">Remarks</label>
                <textarea 
                  class="form-control" 
                  id="quizRemarks"
                  v-model="quizForm.remarks"
                  rows="2"
                  placeholder="Additional remarks"
                ></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeModal">
                Cancel
              </button>
              <button v-if="showEditModal && quizForm.id" type="button" class="btn btn-info me-2" @click="manageQuestions">
                <i class="bi bi-list-ul me-1"></i>
                Manage Questions
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
         v-if="showAddModal || showEditModal" style="z-index: 1040;"></div>
  </div>

  <!-- Add/Edit Question Modal -->
  <div class="modal fade" :class="{ show: showQuestionModal }" 
       :style="{ display: showQuestionModal ? 'block' : 'none', 'z-index': '1055' }" 
       tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            {{ showEditQuestionModal ? 'Edit Question' : 'Add New Question' }}
          </h5>
          <button type="button" class="btn-close" @click="closeQuestionModal"></button>
        </div>
        <form @submit.prevent="saveQuestion">
          <div class="modal-body">
            <div class="mb-3">
              <label for="questionText" class="form-label">Question Text *</label>
              <textarea 
                class="form-control" 
                id="questionText"
                v-model="questionForm.question_text"
                rows="3"
                required
                placeholder="Enter your question here..."
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
                      required
                    >
                    <label class="ms-1 mb-0">Correct</label>
                  </div>
                </div>
              </div>
              
              <div class="mt-2">
                <button type="button" class="btn btn-sm btn-outline-secondary" @click="addOption" :disabled="questionForm.options.length >= 6">
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
                placeholder="Explanation for the correct answer..."
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
            <button type="button" class="btn btn-secondary" @click="closeQuestionModal">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="questionLoading">
              <span v-if="questionLoading" class="spinner-border spinner-border-sm me-2"></span>
              {{ showEditQuestionModal ? 'Update' : 'Add' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Question Modal Backdrop -->
  <div class="modal-backdrop fade" :class="{ show: showQuestionModal }" 
       v-if="showQuestionModal" style="z-index: 1050;"></div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'Quizzes',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const quizzes = ref([])
    const filteredQuizzes = ref([])
    const subjects = ref([])
    const allChapters = ref([])
    const filteredChapters = ref([])
    const currentChapter = ref(null)
    const currentSubject = ref(null)
    const selectedSubjectId = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const showQuestionModal = ref(false)
    const showEditQuestionModal = ref(false)
    const loading = ref(false)
    const questionLoading = ref(false)
    const searchQuery = ref('')
    const quizQuestions = ref([])

    const quizForm = reactive({
      id: null,
      title: '',
      description: '',
      duration_minutes: 30,
      start_date: '',
      end_date: '',
      passing_score: 60,
      max_attempts: 3,
      status: 'draft',
      remarks: '',
      chapter_id: null
    })

    const questionForm = reactive({
      id: null,
      quiz_id: null,
      question_text: '',
      options: ['', ''], // Start with 2 options
      correct_answer: '',
      explanation: '',
      points: 1
    })

    const chapterId = computed(() => route.params.chapterId)

    const fetchSubjects = async () => {
      try {
        const response = await api.get('/admin/subjects')
        subjects.value = response.data.subjects
      } catch (error) {
        store.dispatch('showError', 'Failed to load subjects')
      }
    }

    const fetchAllChapters = async () => {
      try {
        const response = await api.get('/admin/subjects')
        const allChaptersData = []
        for (const subject of response.data.subjects) {
          const chaptersResponse = await api.get(`/admin/subjects/${subject.id}/chapters`)
          for (const chapter of chaptersResponse.data.chapters) {
            allChaptersData.push({
              ...chapter,
              subject: subject
            })
          }
        }
        allChapters.value = allChaptersData
      } catch (error) {
        store.dispatch('showError', 'Failed to load chapters')
      }
    }

    const onSubjectChange = () => {
      if (selectedSubjectId.value) {
        filteredChapters.value = allChapters.value.filter(chapter => chapter.subject_id == selectedSubjectId.value)
      } else {
        filteredChapters.value = []
      }
      quizForm.chapter_id = null
    }

    const fetchQuizzes = async () => {
      try {
        if (chapterId.value) {
          // Fetch quizzes for specific chapter
          const response = await api.get(`/admin/chapters/${chapterId.value}/quizzes`)
          quizzes.value = response.data.quizzes
          filteredQuizzes.value = response.data.quizzes
        } else {
          // Fetch all quizzes with chapter and subject info
          const response = await api.get('/admin/quizzes')
          quizzes.value = response.data.quizzes
          filteredQuizzes.value = response.data.quizzes
        }
      } catch (error) {
        store.dispatch('showError', 'Failed to load quizzes')
      }
    }

    const fetchChapter = async () => {
      if (!chapterId.value) return
      
      try {
        const response = await api.get(`/admin/subjects/${currentSubject.value?.id}/chapters`)
        const chapter = response.data.chapters.find(c => c.id == chapterId.value)
        if (chapter) {
          currentChapter.value = chapter
        }
      } catch (error) {
        store.dispatch('showError', 'Failed to load chapter details')
      }
    }

    const filterQuizzes = () => {
      if (!searchQuery.value) {
        filteredQuizzes.value = quizzes.value
        return
      }
      
      const query = searchQuery.value.toLowerCase()
      filteredQuizzes.value = quizzes.value.filter(quiz =>
        quiz.title.toLowerCase().includes(query) ||
        quiz.description?.toLowerCase().includes(query)
      )
    }

    const editQuiz = (quiz) => {
      quizForm.id = quiz.id
      quizForm.title = quiz.title
      quizForm.description = quiz.description || ''
      quizForm.duration_minutes = quiz.duration_minutes || quiz.duration || 30
      quizForm.start_date = quiz.start_date ? new Date(quiz.start_date).toISOString().slice(0, 16) : ''
      quizForm.end_date = quiz.end_date ? new Date(quiz.end_date).toISOString().slice(0, 16) : ''
      quizForm.passing_score = quiz.passing_score || 60
      quizForm.max_attempts = quiz.max_attempts || 3
      quizForm.status = quiz.status
      quizForm.remarks = quiz.remarks || ''
      quizForm.chapter_id = quiz.chapter_id
      showEditModal.value = true
      
      // Fetch questions for this quiz
      setTimeout(() => {
        fetchQuizQuestions()
      }, 100)
    }

    const saveQuiz = async () => {
      loading.value = true
      try {
        // Set chapter_id if we're in a chapter-specific context
        if (chapterId.value) {
          quizForm.chapter_id = chapterId.value
        }
        
        // Validate required fields
        if (!quizForm.title || !quizForm.chapter_id || !quizForm.start_date || !quizForm.end_date) {
          store.dispatch('showError', 'Please fill in all required fields')
          loading.value = false
          return
        }
        
        // Validate dates
        const startDate = new Date(quizForm.start_date)
        const endDate = new Date(quizForm.end_date)
        if (startDate >= endDate) {
          store.dispatch('showError', 'End date must be after start date')
          loading.value = false
          return
        }
        
        // Prepare data for backend (convert field names and date formats)
        const quizData = {
          title: quizForm.title,
          description: quizForm.description,
          chapter_id: quizForm.chapter_id,
          duration_minutes: quizForm.duration_minutes,
          passing_score: quizForm.passing_score,
          max_attempts: quizForm.max_attempts,
          start_date: quizForm.start_date ? new Date(quizForm.start_date).toISOString() : null,
          end_date: quizForm.end_date ? new Date(quizForm.end_date).toISOString() : null
        }
        
        if (showEditModal.value) {
          await api.put(`/admin/quizzes/${quizForm.id}`, quizData)
          store.dispatch('showSuccess', 'Quiz updated successfully')
          closeModal()
          fetchQuizzes()
        } else {
          const response = await api.post('/admin/quizzes', quizData)
          store.dispatch('showSuccess', 'Quiz created successfully! Now add questions to complete the quiz.')
          closeModal()
          
          // Immediately redirect to question management for the new quiz
          const newQuizId = response.data.quiz.id
          router.push(`/admin/quizzes/${newQuizId}/questions`)
          return
        }
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to save quiz')
      } finally {
        loading.value = false
      }
    }

    const deleteQuiz = async (quiz) => {
      if (!confirm(`Are you sure you want to delete "${quiz.title}"? This will also delete all associated questions and scores.`)) {
        return
      }
      
      try {
        await api.delete(`/admin/quizzes/${quiz.id}`)
        store.dispatch('showSuccess', 'Quiz deleted successfully')
        fetchQuizzes()
      } catch (error) {
        store.dispatch('showError', 'Failed to delete quiz')
      }
    }

    const viewQuestions = (quiz) => {
      router.push(`/admin/quizzes/${quiz.id}/questions`)
    }

    const addQuestion = () => {
      questionForm.quiz_id = quizForm.id
      questionForm.id = null
      questionForm.question_text = ''
      questionForm.options = ['', '']
      questionForm.correct_answer = ''
      questionForm.explanation = ''
      questionForm.points = 1
      showEditQuestionModal.value = false
      showQuestionModal.value = true
    }

    const manageQuestions = () => {
      if (quizForm.id) {
        router.push(`/admin/quizzes/${quizForm.id}/questions`)
      }
    }

    // Question Management Functions
    const fetchQuizQuestions = async () => {
      if (!quizForm.id) return
      
      try {
        const response = await api.get(`/admin/quizzes/${quizForm.id}/questions`)
        quizQuestions.value = response.data.questions
      } catch (error) {
        store.dispatch('showError', 'Failed to load questions')
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
          questionForm.correct_answer = ''
        }
      }
    }

    const editQuestion = (question) => {
      questionForm.id = question.id
      questionForm.quiz_id = quizForm.id
      questionForm.question_text = question.question_text
      questionForm.options = [...question.options]
      questionForm.correct_answer = question.correct_answer
      questionForm.explanation = question.explanation || ''
      questionForm.points = question.points || 1
      showEditQuestionModal.value = true
      showQuestionModal.value = true
    }

    const saveQuestion = async () => {
      questionLoading.value = true
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
        
        if (!questionForm.correct_answer) {
          store.dispatch('showError', 'Please select the correct answer')
          return
        }

        const questionData = {
          quiz_id: quizForm.id,
          question_text: questionForm.question_text,
          options: questionForm.options,
          correct_answer: questionForm.correct_answer,
          explanation: questionForm.explanation,
          points: questionForm.points
        }

        if (showEditQuestionModal.value) {
          await api.put(`/admin/questions/${questionForm.id}`, questionData)
          store.dispatch('showSuccess', 'Question updated successfully')
        } else {
          await api.post('/admin/questions', questionData)
          store.dispatch('showSuccess', 'Question added successfully')
        }
        
        closeQuestionModal()
        fetchQuizQuestions()
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to save question')
      } finally {
        questionLoading.value = false
      }
    }

    const deleteQuestion = async (question) => {
      if (!confirm(`Are you sure you want to delete this question?`)) {
        return
      }
      
      try {
        await api.delete(`/admin/questions/${question.id}`)
        store.dispatch('showSuccess', 'Question deleted successfully')
        fetchQuizQuestions()
      } catch (error) {
        store.dispatch('showError', 'Failed to delete question')
      }
    }

    const closeQuestionModal = () => {
      showQuestionModal.value = false
      showEditQuestionModal.value = false
      questionForm.id = null
      questionForm.quiz_id = null
      questionForm.question_text = ''
      questionForm.options = ['', '']
      questionForm.correct_answer = ''
      questionForm.explanation = ''
      questionForm.points = 1
    }

    const getOptions = (question) => {
      return question.options || []
    }

    const getOptionClass = (question, optIndex) => {
      const correctAnswer = parseInt(question.correct_answer)
      if (optIndex === correctAnswer) {
        return 'bg-success text-white'
      }
      return 'bg-light'
    }

    const isCorrectAnswer = (question, optIndex) => {
      return parseInt(question.correct_answer) === optIndex
    }

    const viewResults = (quiz) => {
      // TODO: Implement quiz results view
      store.dispatch('showInfo', 'Quiz results feature coming soon')
    }

    const goBack = () => {
      router.push(`/admin/subjects/${currentSubject.value?.id}/chapters`)
    }

    const goToSubjects = () => {
      router.push('/admin/subjects')
    }

    const closeModal = () => {
      showAddModal.value = false
      showEditModal.value = false
      quizForm.id = null
      quizForm.title = ''
      quizForm.description = ''
      quizForm.duration_minutes = 30
      quizForm.start_date = ''
      quizForm.end_date = ''
      quizForm.passing_score = 60
      quizForm.max_attempts = 3
      quizForm.status = 'draft'
      quizForm.remarks = ''
      selectedSubjectId.value = '' // Reset subject selection
      
      // Also close question modal and reset question data
      closeQuestionModal()
      quizQuestions.value = []
    }

    const refreshData = () => {
      if (chapterId.value) {
        fetchChapter()
        fetchQuizzes()
      } else {
        // If not chapter-specific, fetch all quizzes
        api.get('/admin/quizzes')
          .then(response => {
            quizzes.value = response.data.quizzes
            filteredQuizzes.value = response.data.quizzes
          })
          .catch(error => {
            store.dispatch('showError', 'Failed to load all quizzes')
          })
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        draft: 'badge bg-secondary',
        active: 'badge bg-success',
        completed: 'badge bg-info'
      }
      return classes[status] || 'badge bg-secondary'
    }

    const getStatusText = (status) => {
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    onMounted(() => {
      fetchSubjects() // Always fetch subjects
      if (chapterId.value) {
        fetchChapter()
        fetchQuizzes()
      } else {
        fetchQuizzes() // Fetch all quizzes if no chapterId
        fetchAllChapters() // Fetch all chapters for the chapter selector
      }
    })

    return {
      chapterId,
      quizzes,
      filteredQuizzes,
      subjects,
      allChapters,
      filteredChapters,
      selectedSubjectId,
      currentChapter,
      currentSubject,
      searchQuery,
      showAddModal,
      showEditModal,
      loading,
      quizForm,
      onSubjectChange,
      editQuiz,
      saveQuiz,
      deleteQuiz,
      viewQuestions,
      manageQuestions,
      viewResults,
      goBack,
      goToSubjects,
      closeModal,
      refreshData,
      filterQuizzes,
      formatDate,
      formatDuration,
      getStatusBadgeClass,
      getStatusText,
      quizQuestions,
      showQuestionModal,
      showEditQuestionModal,
      questionForm,
      questionLoading,
      addOption,
      removeOption,
      editQuestion,
      saveQuestion,
      deleteQuestion,
      closeQuestionModal,
      getOptions,
      getOptionClass,
      isCorrectAnswer,
      addQuestion
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
</style>
