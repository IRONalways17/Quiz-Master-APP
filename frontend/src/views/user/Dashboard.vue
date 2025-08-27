<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12">
        <div class="welcome-banner bg-primary text-white p-4 rounded">
          <div class="row align-items-center">
            <div class="col-md-8">
              <h1 class="mb-2">
                <i class="bi bi-person-circle me-2"></i>
                Welcome back, {{ user?.full_name }}!
              </h1>
              <p class="mb-0">Ready to test your knowledge? Choose a subject and start learning!</p>
            </div>
            <div class="col-md-4 text-end">
              <div class="stats-summary">
                <div class="stat-item">
                  <h3 class="mb-0">{{ stats.total_quizzes_taken || 0 }}</h3>
                  <small>Quizzes Taken</small>
                </div>
                <div class="stat-item">
                  <h3 class="mb-0">{{ stats.average_score || 0 }}%</h3>
                  <small>Avg Score</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card action-card h-100">
          <div class="card-body text-center">
            <i class="bi bi-book fs-1 text-primary mb-3"></i>
            <h5 class="card-title">Browse Subjects</h5>
            <p class="card-text">Explore different subjects and chapters</p>
            <router-link to="/subjects" class="btn btn-primary">
              <i class="bi bi-arrow-right me-2"></i>
              Start Learning
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card action-card h-100">
          <div class="card-body text-center">
            <i class="bi bi-trophy fs-1 text-warning mb-3"></i>
            <h5 class="card-title">My Scores</h5>
            <p class="card-text">View your quiz performance history</p>
            <router-link to="/scores" class="btn btn-warning">
              <i class="bi bi-bar-chart me-2"></i>
              View Scores
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card action-card h-100">
          <div class="card-body text-center">
            <i class="bi bi-award fs-1 text-success mb-3"></i>
            <h5 class="card-title">Leaderboard</h5>
            <p class="card-text">See how you rank among other students</p>
            <router-link to="/leaderboard" class="btn btn-success">
              <i class="bi bi-list-ol me-2"></i>
              View Rankings
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card action-card h-100">
          <div class="card-body text-center">
            <i class="bi bi-person-gear fs-1 text-info mb-3"></i>
            <h5 class="card-title">Profile</h5>
            <p class="card-text">Update your personal information</p>
            <router-link to="/profile" class="btn btn-info">
              <i class="bi bi-gear me-2"></i>
              Edit Profile
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card action-card h-100">
          <div class="card-body text-center">
            <i class="bi bi-download fs-1 text-secondary mb-3"></i>
            <h5 class="card-title">Export Data</h5>
            <p class="card-text">Download your quiz history as CSV</p>
            <button @click="exportUserData" class="btn btn-secondary" :disabled="exporting">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-download me-2"></i>
              {{ exporting ? 'Exporting...' : 'Export CSV' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reminders Section -->
    <div class="row mb-4" v-if="reminders.length > 0">
      <div class="col-12">
        <div class="card border-warning">
          <div class="card-header bg-warning text-dark">
            <h5 class="mb-0">
              <i class="bi bi-bell me-2"></i>
              📌 Reminders
              <span v-if="unreadReminders > 0" class="badge bg-danger ms-2">{{ unreadReminders }}</span>
            </h5>
          </div>
          <div class="card-body">
            <div class="reminder-list">
              <div v-for="reminder in reminders.slice(0, 3)" :key="reminder.id" 
                   class="reminder-item p-3 mb-2 rounded" 
                   :class="reminder.is_read ? 'bg-light' : 'bg-warning bg-opacity-10 border border-warning'">
                <div class="d-flex align-items-start">
                  <div class="reminder-icon me-3">
                    <i :class="getReminderIcon(reminder.reminder_type)" class="fs-5 text-warning"></i>
                  </div>
                  <div class="flex-grow-1">
                    <p class="mb-1" :class="reminder.is_read ? 'text-muted' : ''">{{ reminder.message }}</p>
                    <small class="text-muted">{{ formatDate(reminder.created_at) }}</small>
                  </div>
                  <div class="reminder-actions">
                    <button v-if="!reminder.is_read" 
                            @click="markReminderRead(reminder.id)" 
                            class="btn btn-sm btn-outline-warning me-2">
                      <i class="bi bi-check"></i>
                    </button>
                    <button @click="deleteReminder(reminder.id)" 
                            class="btn btn-sm btn-outline-danger">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="reminders.length > 3" class="text-center mt-3">
              <button @click="showAllReminders = !showAllReminders" class="btn btn-outline-warning btn-sm">
                {{ showAllReminders ? 'Show Less' : `View All ${reminders.length} Reminders` }}
              </button>
            </div>
            <div v-if="reminders.length > 3 && showAllReminders" class="mt-3">
              <div v-for="reminder in reminders.slice(3)" :key="`more-${reminder.id}`" 
                   class="reminder-item p-3 mb-2 rounded" 
                   :class="reminder.is_read ? 'bg-light' : 'bg-warning bg-opacity-10 border border-warning'">
                <div class="d-flex align-items-start">
                  <div class="reminder-icon me-3">
                    <i :class="getReminderIcon(reminder.reminder_type)" class="fs-5 text-warning"></i>
                  </div>
                  <div class="flex-grow-1">
                    <p class="mb-1" :class="reminder.is_read ? 'text-muted' : ''">{{ reminder.message }}</p>
                    <small class="text-muted">{{ formatDate(reminder.created_at) }}</small>
                  </div>
                  <div class="reminder-actions">
                    <button v-if="!reminder.is_read" 
                            @click="markReminderRead(reminder.id)" 
                            class="btn btn-sm btn-outline-warning me-2">
                      <i class="bi bi-check"></i>
                    </button>
                    <button @click="deleteReminder(reminder.id)" 
                            class="btn btn-sm btn-outline-danger">
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="unreadReminders > 0" class="text-center mt-3">
              <button @click="markAllRemindersRead" class="btn btn-warning btn-sm">
                <i class="bi bi-check-all me-1"></i>
                Mark All as Read
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="row g-4">
      <!-- Recent Activity -->
      <div class="col-lg-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-clock-history me-2"></i>
              Recent Activity
            </h5>
          </div>
          <div class="card-body">
            <div v-if="recentActivity.length > 0">
              <div v-for="activity in recentActivity" :key="activity.id" class="activity-item mb-3">
                <div class="d-flex align-items-start">
                  <div class="activity-icon me-3">
                    <i :class="getActivityIcon(activity)" class="fs-4"></i>
                  </div>
                  <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start mb-1">
                      <h6 class="mb-0">{{ activity.title || activity.quiz_title }}</h6>
                      <span v-if="activity.score" :class="getScoreBadgeClass(activity.score)" class="ms-2">
                        {{ activity.score }}%
                      </span>
                    </div>
                    <p class="text-muted mb-1 small">{{ activity.description || `${activity.subject_name} - ${activity.chapter_name}` }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">{{ formatDate(activity.created_at) }}</small>
                      <div class="activity-details">
                        <span v-if="activity.time_taken" class="badge bg-secondary me-2">
                          <i class="bi bi-clock me-1"></i>{{ formatTime(activity.time_taken) }}
                        </span>
                        <span v-if="activity.score_text" class="badge bg-light text-dark me-2">
                          {{ activity.score_text }}
                        </span>
                        <span v-if="activity.passed !== undefined" :class="activity.passed ? 'badge bg-success' : 'badge bg-danger'">
                          {{ activity.passed ? 'Passed' : 'Failed' }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="bi bi-inbox fs-1 text-muted"></i>
              <p class="text-muted mt-2">No recent activity</p>
              <router-link to="/subjects" class="btn btn-primary">
                Start Your First Quiz
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Performance Chart -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-graph-up me-2"></i>
              Performance Trend (Recent Attempts)
            </h5>
          </div>
          <div class="card-body">
            <div v-if="performanceData.message && performanceData.data.length === 0" class="text-center py-5">
              <i class="bi bi-graph-up fs-1 text-muted mb-3"></i>
              <h6 class="text-muted">{{ performanceData.message }}</h6>
              <p class="text-muted small mb-3">Start taking quizzes to see your performance trend</p>
              <router-link to="/subjects" class="btn btn-primary">
                <i class="bi bi-play-circle me-2"></i>
                Take Your First Quiz
              </router-link>
            </div>
            <div v-else class="chart-container">
              <canvas ref="performanceChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'UserDashboard',
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const user = ref(null)
    const stats = ref({})
    const recentActivity = ref([])
    const reminders = ref([])
    const unreadReminders = ref(0)
    const showAllReminders = ref(false)
    const performanceChart = ref(null)
    const performanceData = ref({ labels: [], data: [] })
    let chartInstance = null

    const fetchUserData = async () => {
      try {
        const response = await api.get('/user/profile')
        user.value = response.data.profile
      } catch (error) {
        store.dispatch('showError', 'Failed to load user data')
      }
    }

    const fetchStats = async () => {
      try {
        const response = await api.get('/user/dashboard/stats')
        stats.value = response.data
      } catch (error) {
        store.dispatch('showError', 'Failed to load dashboard statistics')
      }
    }

    const fetchRecentActivity = async () => {
      try {
        const response = await api.get('/user/recent-activity')
        recentActivity.value = response.data.activities
      } catch (error) {
        store.dispatch('showError', 'Failed to load recent activity')
      }
    }

    const fetchPerformanceData = async () => {
      try {
        const response = await api.get('/user/performance-trend')
        performanceData.value = response.data
      } catch (error) {
        console.error('Failed to load performance data:', error)
        // Set default empty data if fetch fails
        performanceData.value = { 
          labels: ['No Data'], 
          data: [0], 
          message: 'No performance data available yet'
        }
      }
    }

    const initPerformanceChart = () => {
      if (!performanceChart.value) return
      
      const ctx = performanceChart.value.getContext('2d')
      
      // Destroy existing chart if it exists
      if (chartInstance) {
        chartInstance.destroy()
      }
      
      const hasData = performanceData.value.data && performanceData.value.data.length > 0 && performanceData.value.data.some(d => d > 0)
      
      // Create gradient
      const gradient = ctx.createLinearGradient(0, 0, 0, 400)
      gradient.addColorStop(0, 'rgba(79, 70, 229, 0.3)')
      gradient.addColorStop(1, 'rgba(79, 70, 229, 0.05)')
      
      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: hasData ? performanceData.value.labels : ['#1 - No Data'],
          datasets: [{
            label: 'Quiz Score (%)',
            data: hasData ? performanceData.value.data : [null],
            borderColor: hasData ? 'rgb(79, 70, 229)' : 'rgb(203, 213, 225)',
            backgroundColor: hasData ? gradient : 'rgba(203, 213, 225, 0.1)',
            borderWidth: 3,
            tension: 0.4,
            fill: true,
            spanGaps: false, // Don't connect across null values for attempt-based data
            pointBackgroundColor: hasData ? 'rgb(79, 70, 229)' : 'rgb(203, 213, 225)',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: hasData ? 6 : 4,
            pointHoverRadius: hasData ? 8 : 4,
            pointHoverBackgroundColor: hasData ? 'rgb(67, 56, 202)' : 'rgb(203, 213, 225)',
            pointHoverBorderColor: '#ffffff',
            pointHoverBorderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 20,
              bottom: 10,
              left: 10,
              right: 10
            }
          },
          plugins: {
            legend: {
              display: true,
              position: 'top',
              labels: {
                usePointStyle: true,
                padding: 20,
                font: {
                  size: 12,
                  weight: '500'
                }
              }
            },
            tooltip: {
              enabled: true,
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              titleColor: '#ffffff',
              bodyColor: '#ffffff',
              borderColor: 'rgb(79, 70, 229)',
              borderWidth: 1,
              cornerRadius: 8,
              displayColors: false,
              callbacks: {
                title: function(context) {
                  return context[0].label
                },
                label: function(context) {
                  if (context.parsed.y === null) {
                    return 'No quiz taken'
                  }
                  return `Quiz Score: ${context.parsed.y}%`
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 105, // Add padding above 100% to prevent point cutoff
              grid: {
                color: 'rgba(0, 0, 0, 0.05)',
                drawBorder: false
              },
              ticks: {
                font: {
                  size: 11
                },
                color: '#6b7280',
                callback: function(value) {
                  // Only show labels for meaningful values
                  if (value <= 100) {
                    return value + '%'
                  }
                  return ''
                },
                padding: 10,
                stepSize: 20 // Show ticks at 0%, 20%, 40%, 60%, 80%, 100%
              }
            },
            x: {
              grid: {
                display: false
              },
              ticks: {
                font: {
                  size: 11
                },
                color: '#6b7280',
                maxRotation: 45,
                padding: 10
              }
            }
          },
          interaction: {
            intersect: false,
            mode: 'index'
          },
          animation: {
            duration: 1000,
            easing: 'easeInOutQuart'
          }
        }
      })
    }

    const getActivityIcon = (activity) => {
      if (activity.type) {
        const icons = {
          excellent_score: 'bi bi-trophy-fill text-warning',
          good_score: 'bi bi-check-circle-fill text-success',
          average_score: 'bi bi-info-circle-fill text-info',
          needs_improvement: 'bi bi-exclamation-triangle-fill text-danger'
        }
        return icons[activity.type] || 'bi bi-info-circle-fill text-info'
      }
      
      // Fallback for old format
      const icons = {
        quiz_completed: 'bi bi-check-circle-fill text-success',
        quiz_started: 'bi bi-play-circle-fill text-primary',
        score_achieved: 'bi bi-trophy-fill text-warning'
      }
      return icons[activity.type] || 'bi bi-info-circle-fill text-info'
    }

    const getScoreBadgeClass = (score) => {
      if (score >= 90) return 'badge bg-success'
      if (score >= 80) return 'badge bg-info'
      if (score >= 70) return 'badge bg-warning'
      return 'badge bg-danger'
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffInHours = (now - date) / (1000 * 60 * 60)
      
      if (diffInHours < 24) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      } else if (diffInHours < 48) {
        return 'Yesterday'
      } else {
        return date.toLocaleDateString()
      }
    }

    const formatTime = (seconds) => {
      if (!seconds) return 'N/A'
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}m ${remainingSeconds}s`
    }

    const exporting = ref(false)

    const exportUserData = async () => {
      exporting.value = true
      try {
        const response = await api.post('/user/export/scores')
        store.dispatch('showSuccess', 'Export started! You will receive an email when it\'s ready.')
      } catch (error) {
        store.dispatch('showError', 'Failed to start export')
      } finally {
        exporting.value = false
      }
    }

    const fetchReminders = async () => {
      try {
        const response = await api.get('/user/reminders')
        reminders.value = response.data.reminders
        unreadReminders.value = response.data.unread_reminders
      } catch (error) {
        store.dispatch('showError', 'Failed to load reminders')
      }
    }

    const markReminderRead = async (reminderId) => {
      try {
        await api.put(`/user/reminders/${reminderId}/mark-read`)
        // Update local state
        const reminder = reminders.value.find(r => r.id === reminderId)
        if (reminder) {
          reminder.is_read = true
          unreadReminders.value = Math.max(0, unreadReminders.value - 1)
        }
        store.dispatch('showSuccess', 'Reminder marked as read')
      } catch (error) {
        store.dispatch('showError', 'Failed to mark reminder as read')
      }
    }

    const markAllRemindersRead = async () => {
      try {
        await api.put('/user/reminders/mark-all-read')
        // Update local state
        reminders.value.forEach(reminder => {
          reminder.is_read = true
        })
        unreadReminders.value = 0
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
          if (wasUnread) {
            unreadReminders.value = Math.max(0, unreadReminders.value - 1)
          }
        }
        store.dispatch('showSuccess', 'Reminder deleted')
      } catch (error) {
        store.dispatch('showError', 'Failed to delete reminder')
      }
    }

    const getReminderIcon = (type) => {
      const icons = {
        inactive_user: 'bi bi-person-exclamation',
        new_quiz: 'bi bi-plus-circle',
        general: 'bi bi-info-circle'
      }
      return icons[type] || 'bi bi-bell'
    }

    onMounted(async () => {
      await Promise.all([
        fetchUserData(),
        fetchStats(),
        fetchRecentActivity(),
        fetchReminders(),
        fetchPerformanceData()
      ])
      
      // Initialize chart after data is loaded
      initPerformanceChart()
    })

    // Watch for performance data changes and update chart
    watch(performanceData, (newData) => {
      if (newData && performanceChart.value) {
        initPerformanceChart()
      }
    }, { deep: true })

    onUnmounted(() => {
      if (chartInstance) {
        chartInstance.destroy()
      }
    })

    return {
      user,
      stats,
      recentActivity,
      reminders,
      unreadReminders,
      showAllReminders,
      performanceChart,
      performanceData,
      getActivityIcon,
      getScoreBadgeClass,
      getReminderIcon,
      formatDate,
      formatTime,
      exporting,
      exportUserData,
      markReminderRead,
      markAllRemindersRead,
      deleteReminder
    }
  }
}
</script>

<style scoped>
.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-summary {
  display: flex;
  gap: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-item h3 {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.action-card {
  transition: transform 0.2s;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.action-card:hover {
  transform: translateY(-5px);
}

.activity-item {
  padding: 1rem;
  border-radius: 8px;
  background-color: #f8f9fa;
  transition: background-color 0.2s;
}

.activity-item:hover {
  background-color: #e9ecef;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.quiz-item {
  padding: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background-color: #fff;
}

.quiz-meta {
  margin-top: 0.5rem;
}

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  margin: 10px 0;
}

.activity-item {
  padding: 1.25rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.activity-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #cbd5e1;
}

.activity-icon {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.activity-details .badge {
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
