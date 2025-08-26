<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h1 class="mb-0">
          <i class="bi bi-book me-2"></i>
          Subjects Management
        </h1>
        <button class="btn btn-primary" @click="showAddModal = true">
          <i class="bi bi-plus-circle me-2"></i>
          Add Subject
        </button>
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
            placeholder="Search subjects..."
            v-model="searchQuery"
            @input="filterSubjects"
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

    <!-- Subjects Table -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Code</th>
                <th>Description</th>
                <th>Chapters</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subject in filteredSubjects" :key="subject.id">
                <td>{{ subject.id }}</td>
                <td>
                  <strong>{{ subject.name }}</strong>
                </td>
                <td>
                  <span class="badge bg-secondary">{{ subject.code }}</span>
                </td>
                <td>{{ subject.description || 'No description' }}</td>
                <td>
                  <span class="badge bg-info">{{ subject.chapters_count || 0 }} chapters</span>
                </td>
                <td>{{ formatDate(subject.created_at) }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" @click="editSubject(subject)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-outline-success" @click="viewChapters(subject)">
                      <i class="bi bi-list-ul"></i>
                    </button>
                    <button class="btn btn-outline-danger" @click="deleteSubject(subject)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredSubjects.length === 0">
                <td colspan="7" class="text-center py-4">
                  <i class="bi bi-inbox fs-1 text-muted"></i>
                  <p class="text-muted mt-2">No subjects found</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Subject Modal -->
    <div class="modal fade" :class="{ show: showAddModal || showEditModal }" 
         :style="{ display: (showAddModal || showEditModal) ? 'block' : 'none' }" 
         tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ showEditModal ? 'Edit Subject' : 'Add New Subject' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveSubject">
            <div class="modal-body">
              <div class="mb-3">
                <label for="subjectName" class="form-label">Subject Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="subjectName"
                  v-model="subjectForm.name"
                  required
                  placeholder="Enter subject name"
                >
              </div>
              <div class="mb-3">
                <label for="subjectCode" class="form-label">Subject Code *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="subjectCode"
                  v-model="subjectForm.code"
                  required
                  placeholder="Enter subject code (e.g., MATH101, PHYS101)"
                  maxlength="20"
                >
                <div class="form-text">Unique code for the subject (max 20 characters)</div>
              </div>
              <div class="mb-3">
                <label for="subjectDescription" class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  id="subjectDescription"
                  v-model="subjectForm.description"
                  rows="3"
                  placeholder="Enter subject description"
                ></textarea>
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
import { ref, reactive, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'Subjects',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const subjects = ref([])
    const filteredSubjects = ref([])
    const searchQuery = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const loading = ref(false)
    
    const subjectForm = reactive({
      id: null,
      name: '',
      code: '',
      description: ''
    })

    const fetchSubjects = async () => {
      try {
        const response = await api.get('/admin/subjects')
        subjects.value = response.data.subjects
        filteredSubjects.value = subjects.value
      } catch (error) {
        store.dispatch('showError', 'Failed to load subjects')
      }
    }

    const filterSubjects = () => {
      if (!searchQuery.value) {
        filteredSubjects.value = subjects.value
        return
      }
      
      const query = searchQuery.value.toLowerCase()
      filteredSubjects.value = subjects.value.filter(subject =>
        subject.name.toLowerCase().includes(query) ||
        subject.code.toLowerCase().includes(query) ||
        subject.description?.toLowerCase().includes(query)
      )
    }

    const editSubject = (subject) => {
      subjectForm.id = subject.id
      subjectForm.name = subject.name
      subjectForm.code = subject.code
      subjectForm.description = subject.description || ''
      showEditModal.value = true
    }

    const saveSubject = async () => {
      loading.value = true
      try {
        if (showEditModal.value) {
          await api.put(`/admin/subjects/${subjectForm.id}`, subjectForm)
          store.dispatch('showSuccess', 'Subject updated successfully')
        } else {
          await api.post('/admin/subjects', subjectForm)
          store.dispatch('showSuccess', 'Subject created successfully')
        }
        
        closeModal()
        fetchSubjects()
      } catch (error) {
        store.dispatch('showError', error.response?.data?.error || 'Failed to save subject')
      } finally {
        loading.value = false
      }
    }

    const deleteSubject = async (subject) => {
      if (!confirm(`Are you sure you want to delete "${subject.name}"? This will also delete all associated chapters and quizzes.`)) {
        return
      }
      
      try {
        await api.delete(`/admin/subjects/${subject.id}`)
        store.dispatch('showSuccess', 'Subject deleted successfully')
        fetchSubjects()
      } catch (error) {
        store.dispatch('showError', 'Failed to delete subject')
      }
    }

    const viewChapters = (subject) => {
      router.push(`/admin/subjects/${subject.id}/chapters`)
    }

    const closeModal = () => {
      showAddModal.value = false
      showEditModal.value = false
      subjectForm.id = null
      subjectForm.name = ''
      subjectForm.code = ''
      subjectForm.description = ''
    }

    const refreshData = () => {
      fetchSubjects()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      fetchSubjects()
    })

    return {
      subjects,
      filteredSubjects,
      searchQuery,
      showAddModal,
      showEditModal,
      loading,
      subjectForm,
      editSubject,
      saveSubject,
      deleteSubject,
      viewChapters,
      closeModal,
      refreshData,
      filterSubjects,
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
