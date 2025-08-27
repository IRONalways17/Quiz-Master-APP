<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <h1 class="mb-4">
          <i class="bi bi-speedometer2 me-2"></i>
          Admin Dashboard
        </h1>
      </div>
    </div>
    
    <!-- Statistics Cards -->
    <div class="row g-4 mb-4">
      <div class="col-md-6 col-lg-3">
        <div class="card stat-card border-0 bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2 text-white-50">Total Users</h6>
                <h2 class="card-title mb-0">{{ stats.total_users || 0 }}</h2>
              </div>
              <i class="bi bi-people-fill fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3">
        <div class="card stat-card border-0 bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2 text-white-50">Active Users</h6>
                <h2 class="card-title mb-0">{{ stats.active_users || 0 }}</h2>
              </div>
              <i class="bi bi-person-check-fill fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3">
        <div class="card stat-card border-0 bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2 text-white-50">Total Quizzes</h6>
                <h2 class="card-title mb-0">{{ stats.total_quizzes || 0 }}</h2>
              </div>
              <i class="bi bi-question-circle-fill fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-3">
        <div class="card stat-card border-0 bg-warning text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="card-subtitle mb-2 text-white-50">Active Quizzes</h6>
                <h2 class="card-title mb-0">{{ stats.active_quizzes || 0 }}</h2>
              </div>
              <i class="bi bi-lightning-fill fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="row g-4 mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-lightning me-2"></i>
              Quick Actions
            </h5>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3">
                <router-link to="/admin/subjects" class="btn btn-primary w-100">
                  <i class="bi bi-plus-circle me-2"></i>
                  Add Subject
                </router-link>
              </div>
              <div class="col-md-3">
                <router-link to="/admin/quizzes" class="btn btn-success w-100">
                  <i class="bi bi-plus-circle me-2"></i>
                  Create Quiz
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts -->
    <div class="row g-4">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-graph-up me-2"></i>
              Quiz Activity Trend
            </h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="activityChart"></canvas>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header bg-light">
            <h5 class="mb-0">
              <i class="bi bi-pie-chart me-2"></i>
              Quiz Distribution
            </h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="distributionChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import api from '@/services/api'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'AdminDashboard',
  setup() {
    const store = useStore()
    const stats = ref({})
    const activityChart = ref(null)
    const distributionChart = ref(null)
    let chartInstances = []
    
    const fetchStats = async () => {
      try {
        const response = await api.get('/admin/dashboard/stats')
        stats.value = response.data
        
        // Update charts with real data
        if (chartInstances.length > 0) {
          updateActivityChart(chartInstances[0])
        }
        if (chartInstances.length > 1) {
          updateDistributionChart(chartInstances[1])
        }
      } catch (error) {
        store.dispatch('showError', 'Failed to load dashboard statistics')
      }
    }
    
    const initCharts = () => {
      // Activity Chart - start with empty data, will be updated when stats load
      const activityCtx = activityChart.value.getContext('2d')
      const activityChartInstance = new Chart(activityCtx, {
        type: 'line',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Quiz Attempts',
            data: [0, 0, 0, 0, 0, 0, 0],
            borderColor: 'rgb(79, 70, 229)',
            backgroundColor: 'rgba(79, 70, 229, 0.1)',
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      })
      chartInstances.push(activityChartInstance)
      
      // Distribution Chart - will be updated with real data
      const distributionCtx = distributionChart.value.getContext('2d')
      const distributionChartInstance = new Chart(distributionCtx, {
        type: 'doughnut',
        data: {
          labels: ['Loading...'],
          datasets: [{
            data: [1],
            backgroundColor: ['#6b7280']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
      chartInstances.push(distributionChartInstance)
      
      // Update distribution chart with real data
      updateDistributionChart(distributionChartInstance)
    }
    
    const updateDistributionChart = (chartInstance) => {
      if (stats.value.quiz_distribution) {
        const distribution = stats.value.quiz_distribution
        chartInstance.data.labels = distribution.labels
        chartInstance.data.datasets[0].data = distribution.data
        chartInstance.data.datasets[0].backgroundColor = distribution.colors.slice(0, distribution.labels.length)
        chartInstance.update()
      }
    }
    
    const updateActivityChart = (chart) => {
      if (stats.value.activity_trend) {
        chart.data.labels = stats.value.activity_trend.labels
        chart.data.datasets[0].data = stats.value.activity_trend.data
        chart.update()
      }
    }
    
    onMounted(() => {
      fetchStats()
      initCharts()
    })
    
    onUnmounted(() => {
      chartInstances.forEach(chart => chart.destroy())
    })
    
    return {
      stats,
      activityChart,
      distributionChart
    }
  }
}
</script>

<style scoped>
.stat-card {
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.chart-container {
  position: relative;
  height: 300px;
}
</style> 