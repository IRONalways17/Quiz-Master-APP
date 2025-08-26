<template>
  <div class="container-fluid">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="mb-0">
              <i class="bi bi-bell me-2"></i>
              Reminders
            </h1>
            <p class="text-muted mb-0">Manage your notifications and reminders</p>
          </div>
          <div>
            <button class="btn btn-outline-secondary me-2" @click="refreshReminders">
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh
            </button>
            <button 
              v-if="unreadCount > 0"
              class="btn btn-warning" 
              @click="markAllAsRead"
              :disabled="loading"
            >
              <i class="bi bi-check-all me-1"></i>
              Mark All as Read
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body text-center">
            <h3 class="mb-1">{{ totalCount }}</h3>
            <small>Total Reminders</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-dark">
          <div class="card-body text-center">
            <h3 class="mb-1">{{ unreadCount }}</h3>
            <small>Unread</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body text-center">
            <h3 class="mb-1">{{ readCount }}</h3>
            <small>Read</small>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body text-center">
            <h3 class="mb-1">{{ reminders.length }}</h3>
            <small>This Page</small>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input 
            type="text" 
            class="form-control" 
            placeholder="Search reminders..."
            v-model="searchQuery"
            @input="filterReminders"
          >
        </div>
      </div>
      <div class="col-md-3">
        <select class="form-select" v-model="statusFilter" @change="filterReminders">
          <option value="all">All Status</option>
          <option value="unread">Unread Only</option>
          <option value="read">Read Only</option>
        </select>
      </div>
      <div class="col-md-3">
        <select class="form-select" v-model="typeFilter" @change="filterReminders">
          <option value="all">All Types</option>
          <option value="new_quiz">New Quiz</option>
          <option value="inactive_user">Inactive User</option>
          <option value="general">General</option>
        </select>
      </div>
    </div>

    <!-- Reminders List -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-list me-2"></i>
              Reminders ({{ filteredReminders.length }})
            </h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-3">Loading reminders...</p>
            </div>

            <div v-else-if="filteredReminders.length === 0" class="text-center py-5">
              <i class="bi bi-bell-slash fs-1 text-muted"></i>
              <h4 class="text-muted mt-3">No reminders found</h4>
              <p class="text-muted">You're all caught up!</p>
            </div>

            <div v-else class="reminders-list">
              <div 
                v-for="reminder in filteredReminders" 
                :key="reminder.id"
                class="reminder-item p-3 mb-3 rounded border"
                :class="reminder.is_read ? 'bg-light' : 'bg-warning bg-opacity-10 border-warning'"
              >
                <div class="d-flex align-items-start">
                  <div class="reminder-icon me-3">
                    <i :class="getReminderIcon(reminder.reminder_type)" class="fs-4 text-warning"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <h6 class="mb-1" :class="reminder.is_read ? 'text-muted' : 'fw-bold'">
                          {{ getReminderTitle(reminder.reminder_type) }}
                        </h6>
                        <p class="mb-1" :class="reminder.is_read ? 'text-muted' : ''">
                          {{ reminder.message }}
                        </p>
                        <small class="text-muted">
                          <i class="bi bi-clock me-1"></i>
                          {{ formatDate(reminder.created_at) }}
                        </small>
                      </div>
                      <div class="reminder-actions">
                        <button 
                          v-if="!reminder.is_read"
                          @click="markAsRead(reminder.id)" 
                          class="btn btn-sm btn-outline-warning me-2"
                          title="Mark as read"
                        >
                          <i class="bi bi-check"></i>
                        </button>
                        <button 
                          @click="deleteReminder(reminder.id)" 
                          class="btn btn-sm btn-outline-danger"
                          title="Delete reminder"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </div>
                    <div class="reminder-meta">
                      <span :class="reminder.is_read ? 'badge bg-secondary' : 'badge bg-warning'">
                        {{ reminder.is_read ? 'Read' : 'Unread' }}
                      </span>
                      <span class="badge bg-info ms-2">
                        {{ getReminderTypeLabel(reminder.reminder_type) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="totalPages > 1" class="d-flex justify-content-center mt-4">
              <nav>
                <ul class="pagination">
                  <li class="page-item" :class="{ disabled: currentPage === 1 }">
                    <button class="page-link" @click="changePage(currentPage - 1)">
                      <i class="bi bi-chevron-left"></i>
                    </button>
                  </li>
                  <li 
                    v-for="page in visiblePages" 
                    :key="page"
                    class="page-item"
                    :class="{ active: page === currentPage }"
                  >
                    <button class="page-link" @click="changePage(page)">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                    <button class="page-link" @click="changePage(currentPage + 1)">
                      <i class="bi bi-chevron-right"></i>
                    </button>
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
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'

export default {
  name: 'Reminders',
  setup() {
    const store = useStore()
    
    const reminders = ref([])
    const loading = ref(false)
    const searchQuery = ref('')
    const statusFilter = ref('all')
    const typeFilter = ref('all')
    const currentPage = ref(1)
    const totalPages = ref(1)
    const totalCount = ref(0)
    const unreadCount = ref(0)
    const readCount = ref(0)

    const filteredReminders = computed(() => {
      let filtered = reminders.value

      // Filter by search query
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(reminder => 
          reminder.message.toLowerCase().includes(query)
        )
      }

      // Filter by status
      if (statusFilter.value === 'unread') {
        filtered = filtered.filter(reminder => !reminder.is_read)
      } else if (statusFilter.value === 'read') {
        filtered = filtered.filter(reminder => reminder.is_read)
      }

      // Filter by type
      if (typeFilter.value !== 'all') {
        filtered = filtered.filter(reminder => reminder.reminder_type === typeFilter.value)
      }

      return filtered
    })

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, currentPage.value + 2)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      
      return pages
    })

    const fetchReminders = async (page = 1) => {
      loading.value = true
      try {
        const response = await api.get('/user/reminders', {
          params: {
            page,
            per_page: 20,
            unread_only: false
          }
        })
        
        reminders.value = response.data.reminders
        totalCount.value = response.data.total_reminders
        unreadCount.value = response.data.unread_reminders
        readCount.value = totalCount.value - unreadCount.value
        totalPages.value = response.data.pages
        currentPage.value = page
      } catch (error) {
        store.dispatch('showError', 'Failed to load reminders')
      } finally {
        loading.value = false
      }
    }

    const markAsRead = async (reminderId) => {
      try {
        await api.put(`/user/reminders/${reminderId}/mark-read`)
        
        // Update local state
        const reminder = reminders.value.find(r => r.id === reminderId)
        if (reminder) {
          reminder.is_read = true
          unreadCount.value = Math.max(0, unreadCount.value - 1)
          readCount.value = totalCount.value - unreadCount.value
        }
        
        store.dispatch('showSuccess', 'Reminder marked as read')
      } catch (error) {
        store.dispatch('showError', 'Failed to mark reminder as read')
      }
    }

    const markAllAsRead = async () => {
      try {
        await api.put('/user/reminders/mark-all-read')
        
        // Update local state
        reminders.value.forEach(reminder => {
          reminder.is_read = true
        })
        unreadCount.value = 0
        readCount.value = totalCount.value
        
        store.dispatch('showSuccess', 'All reminders marked as read')
      } catch (error) {
        store.dispatch('showError', 'Failed to mark all reminders as read')
      }
    }

    const deleteReminder = async (reminderId) => {
      try {
        await api.delete(`/user/reminders/${reminderId}`)
        
        // Update local state
        const index = reminders.value.findIndex(r => r.id === reminderId)
        if (index !== -1) {
          const wasUnread = !reminders.value[index].is_read
          reminders.value.splice(index, 1)
          totalCount.value--
          
          if (wasUnread) {
            unreadCount.value = Math.max(0, unreadCount.value - 1)
          } else {
            readCount.value = Math.max(0, readCount.value - 1)
          }
        }
        
        store.dispatch('showSuccess', 'Reminder deleted')
      } catch (error) {
        store.dispatch('showError', 'Failed to delete reminder')
      }
    }

    const refreshReminders = () => {
      fetchReminders(1)
    }

    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        fetchReminders(page)
      }
    }

    const filterReminders = () => {
      // Reset to first page when filtering
      currentPage.value = 1
    }

    const getReminderIcon = (type) => {
      const icons = {
        inactive_user: 'bi bi-person-exclamation',
        new_quiz: 'bi bi-plus-circle',
        general: 'bi bi-info-circle'
      }
      return icons[type] || 'bi bi-bell'
    }

    const getReminderTitle = (type) => {
      const titles = {
        inactive_user: 'Welcome Back',
        new_quiz: 'New Quiz Available',
        general: 'General Notification'
      }
      return titles[type] || 'Reminder'
    }

    const getReminderTypeLabel = (type) => {
      const labels = {
        inactive_user: 'Inactive User',
        new_quiz: 'New Quiz',
        general: 'General'
      }
      return labels[type] || 'Unknown'
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      fetchReminders()
    })

    return {
      reminders,
      loading,
      searchQuery,
      statusFilter,
      typeFilter,
      currentPage,
      totalPages,
      totalCount,
      unreadCount,
      readCount,
      filteredReminders,
      visiblePages,
      markAsRead,
      markAllAsRead,
      deleteReminder,
      refreshReminders,
      changePage,
      filterReminders,
      getReminderIcon,
      getReminderTitle,
      getReminderTypeLabel,
      formatDate
    }
  }
}
</script>

<style scoped>
.reminder-item {
  transition: all 0.2s;
}

.reminder-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.reminder-actions {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.reminder-item:hover .reminder-actions {
  opacity: 1;
}

.reminder-meta {
  margin-top: 0.5rem;
}
</style> 