<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-0">
            <i class="bi bi-list-ul me-2"></i>
            Chapters Management
          </h1>
          <p class="text-muted mb-0" v-if="currentSubject">
            Subject: <strong>{{ currentSubject.name }}</strong>
          </p>
        </div>
        <div>
          <button class="btn btn-outline-secondary me-2" @click="goBack">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Subjects
          </button>
          <button class="btn btn-primary" @click="showAddModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Add Chapter
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
            placeholder="Search chapters..."
            v-model="searchQuery"
            @input="filterChapters"
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

    <!-- Chapters Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Quizzes</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="chapter in filteredChapters" :key="chapter.id">
                <td>{{ chapter.id }}</td>
                <td>
                  <strong>{{ chapter.name }}</strong>
                </td>
                <td>{{ chapter.description || 'No description' }}</td>
                <td>
                  <span class="badge bg-success">{{ chapter.quizzes_count || 0 }} quizzes</span>
                </td>
                <td>{{ formatDate(chapter.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editChapter(chapter)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-danger" @click="deleteChapter(chapter)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredChapters.length === 0">
                <td colspan="6" class="text-center py-4">
                  <i class="bi bi-inbox fs-1 text-muted"></i>
                  <p class="text-muted mt-2">No chapters found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Chapter Modal -->
    <div class="modal fade" :class="{ show: showAddModal || showEditModal }" 
         :style="{ display: (showAddModal || showEditModal) ? 'block' : 'none' }" 
         tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ showEditModal ? 'Edit Chapter' : 'Add New Chapter' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveChapter">
            <div class="modal-body">
              <div class="mb-3">
                <label for="chapterName" class="form-label">Chapter Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="chapterName"
                  v-model="chapterForm.name"
                  required
                  placeholder="Enter chapter name"
                >
              </div>
              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="chapterDescription"
                  v-model="chapterForm.description"
                  rows="3"
                  placeholder="Enter chapter description"
                ></textarea>
              </div>
              <div class="mb-3" v-if="currentSubject">
                <label class="form-label">Subject</label>
                <input 
                  type="text" 
                  class="form-control" 
                  :value="currentSubject.name"
                  disabled
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
  name: 'Chapters',
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    const chapters = ref([])
    const filteredChapters = ref([])
    const currentSubject = ref(null)
    const searchQuery = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const loading = ref(false)
    
    const chapterForm = reactive({
      id: null,
      name: '',
      description: '',
      subject_id: null
    })

    const subjectId = computed(() => route.params.subjectId)

    const fetchSubject = async () => {
      try {
        const response = await api.get(`/admin/subjects/${subjectId.value}`)
        currentSubject.value = response.data.subject
        chapterForm.subject_id = currentSubject.value.id
      } catch (error) {
        store.dispatch('showError', 'Failed to load subject details')
        router.push('/admin/subjects')
      }
    }

    const fetchChapters = async () => {
      try {
        const response = await api.get(`/admin/subjects/${subjectId.value}/chapters`)
        chapters.value = response.data.chapters
        filteredChapters.value = chapters.value
      } catch (error) {
        store.dispatch('showError', 'Failed to load chapters')
      }
    }

    const filterChapters = () => {
      if (!searchQuery.value) {
        filteredChapters.value = chapters.value
        return
      }
      
      const query = searchQuery.value.toLowerCase()
      filteredChapters.value = chapters.value.filter(chapter =>
        chapter.name.toLowerCase().includes(query) ||
        chapter.description?.toLowerCase().includes(query)
      )
    }

    const editChapter = (chapter) => {
      chapterForm.id = chapter.id
      chapterForm.name = chapter.name
      chapterForm.description = chapter.description || ''
      showEditModal.value = true
    }

    const saveChapter = async () => {
      loading.value = true
      try {
        if (showEditModal.value) {
          await api.put(`/admin/chapters/${chapterForm.id}`, chapterForm)
          store.dispatch('showSuccess', 'Chapter updated successfully')
        } else {
          await api.post('/admin/chapters', chapterForm)
          store.dispatch('showSuccess', 'Chapter created successfully')
        }
        
        closeModal()
        fetchChapters()
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to save chapter')
      } finally {
        loading.value = false
      }
    }

    const deleteChapter = async (chapter) => {
      if (!confirm(`Are you sure you want to delete "${chapter.name}"? This will also delete all associated quizzes.`)) {
        return
      }
      
      try {
        await api.delete(`/admin/chapters/${chapter.id}`)
        store.dispatch('showSuccess', 'Chapter deleted successfully')
        fetchChapters()
      } catch (error) {
        store.dispatch('showError', 'Failed to delete chapter')
      }
    }

    const viewQuizzes = (chapter) => {
      router.push(`/admin/chapters/${chapter.id}/quizzes`)
    }

    const goBack = () => {
      router.push('/admin/subjects')
    }

    const closeModal = () => {
      showAddModal.value = false
      showEditModal.value = false
      chapterForm.id = null
      chapterForm.name = ''
      chapterForm.description = ''
    }

    const refreshData = () => {
      fetchSubject()
      fetchChapters()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      if (subjectId.value) {
        fetchSubject()
        fetchChapters()
      } else {
        router.push('/admin/subjects')
      }
    })

    return {
      chapters,
      filteredChapters,
      currentSubject,
      searchQuery,
      showAddModal,
      showEditModal,
      loading,
      chapterForm,
      editChapter,
      saveChapter,
      deleteChapter,
      viewQuizzes,
      goBack,
      closeModal,
      refreshData,
      filterChapters,
      formatDate
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
