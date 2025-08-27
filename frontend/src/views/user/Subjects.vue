<template>
  <div class="container-fluid">
    <!-- Navigation Header -->
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-0">
            <i class="bi bi-book me-2"></i>
            {{ isViewingSubject ? currentSubject?.name : 'Browse Subjects' }}
          </h1>
          <p class="text-muted mb-0">
            {{ isViewingSubject ? 'Explore chapters and quizzes' : 'Choose a subject to start your learning journey' }}
          </p>
        </div>
        <div>
          <button v-if="isViewingSubject" class="btn btn-outline-secondary me-2" @click="goBackToSubjects">
            <i class="bi bi-arrow-left me-1"></i>
            Back to Subjects
          </button>
          <button class="btn btn-outline-secondary me-2" @click="refreshData">
            <i class="bi bi-arrow-clockwise me-1"></i>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Chapters View -->
    <div v-if="isViewingSubject" class="row g-4">
      <!-- Loading indicator -->
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading chapters...</span>
        </div>
        <p class="mt-2 text-muted">Loading chapters...</p>
      </div>
      
      <div v-for="chapter in chapters" :key="chapter.id" class="col-md-6 col-lg-4" v-if="!loading">
        <div class="card chapter-card h-100">
          <div class="card-body">
            <div class="chapter-icon mb-3">
              <i class="bi bi-file-text fs-1 text-primary"></i>
            </div>
            <h5 class="card-title">{{ chapter.name }}</h5>
            <p class="card-text text-muted">{{ chapter.description || 'No description available' }}</p>
            
            <div class="chapter-stats mb-3">
              <div class="row text-center">
                <div class="col-12">
                  <div class="stat-item">
                    <h6 class="mb-1">{{ chapter.quizzes_count || 0 }}</h6>
                    <small class="text-muted">Quizzes</small>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="d-grid">
              <router-link :to="`/subjects/${currentSubject?.slug}/chapters/${chapter.slug}/quizzes`" class="btn btn-primary">
                <i class="bi bi-play-circle me-2"></i>
                Take Quizzes
              </router-link>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="chapters.length === 0 && !loading" class="col-12">
        <div class="text-center py-5">
          <i class="bi bi-inbox fs-1 text-muted"></i>
          <h4 class="text-muted mt-3">No chapters available</h4>
          <p class="text-muted">This subject doesn't have any chapters yet.</p>
        </div>
      </div>
    </div>

    <!-- Subjects View -->
    <div v-else>
      <!-- Loading indicator -->
      <div v-if="loading" class="row">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading subjects...</span>
          </div>
          <p class="mt-2 text-muted">Loading subjects...</p>
        </div>
      </div>
      
      <!-- Search and Filters -->
      <div v-if="!loading" class="row mb-4">
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
        <div class="col-md-6">
          <select class="form-select" v-model="sortBy" @change="sortSubjects">
            <option value="name">Sort by Name</option>
            <option value="chapters_count">Sort by Chapters</option>
            <option value="quizzes_count">Sort by Quizzes</option>
          </select>
        </div>
      </div>

      <!-- Subjects Grid -->
      <div v-if="!loading" class="row g-4">
        <div v-for="subject in filteredSubjects" :key="subject.id" class="col-md-6 col-lg-4">
          <div class="card subject-card h-100">
            <div class="card-body">
              <div class="subject-icon mb-3">
                <i class="bi bi-book fs-1 text-primary"></i>
              </div>
              <h5 class="card-title">{{ subject.name }}</h5>
              <p class="card-text text-muted">{{ subject.description || 'No description available' }}</p>
              
              <div class="subject-stats mb-3">
                <div class="row text-center">
                  <div class="col-6">
                    <div class="stat-item">
                      <h6 class="mb-1">{{ subject.chapters_count || 0 }}</h6>
                      <small class="text-muted">Chapters</small>
                    </div>
                  </div>
                  <div class="col-6">
                    <div class="stat-item">
                      <h6 class="mb-1">{{ subject.quizzes_count || 0 }}</h6>
                      <small class="text-muted">Quizzes</small>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="subject-progress mb-3" v-if="subject.user_progress">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <small class="text-muted">Your Progress</small>
                  <small class="text-muted">{{ subject.user_progress.completed_quizzes }}/{{ subject.quizzes_count }}</small>
                </div>
                <div class="progress" style="height: 6px;">
                  <div 
                    class="progress-bar bg-success" 
                    :style="{ width: `${subject.user_progress.progress_percentage}%` }"
                  ></div>
                </div>
              </div>
              
              <div class="d-grid">
                <router-link :to="`/subjects/${subject.slug}/chapters`" class="btn btn-primary">
                  <i class="bi bi-arrow-right me-2"></i>
                  Explore Chapters
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="filteredSubjects.length === 0" class="col-12">
          <div class="text-center py-5">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <h4 class="text-muted mt-3">No subjects found</h4>
            <p class="text-muted">Try adjusting your search criteria</p>
          </div>
        </div>
      </div>

      <!-- Featured Subject -->
      <div v-if="featuredSubject" class="row mt-5">
        <div class="col-12">
          <div class="card featured-subject">
            <div class="card-body">
              <div class="row align-items-center">
                <div class="col-md-8">
                  <div class="d-flex align-items-center mb-3">
                    <span class="badge bg-warning me-2">Featured</span>
                    <h3 class="mb-0">{{ featuredSubject.name }}</h3>
                  </div>
                  <p class="lead">{{ featuredSubject.description }}</p>
                  <div class="row mb-3">
                    <div class="col-md-4">
                      <div class="featured-stat">
                        <h4 class="text-primary mb-1">{{ featuredSubject.chapters_count }}</h4>
                        <small class="text-muted">Chapters Available</small>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="featured-stat">
                        <h4 class="text-success mb-1">{{ featuredSubject.quizzes_count }}</h4>
                        <small class="text-muted">Interactive Quizzes</small>
                      </div>
                    </div>
                    <div class="col-md-4">
                      <div class="featured-stat">
                        <h4 class="text-info mb-1">{{ featuredSubject.active_users || 0 }}</h4>
                        <small class="text-muted">Active Learners</small>
                      </div>
                    </div>
                  </div>
                  <router-link :to="`/subjects/${featuredSubject.slug}/chapters`" class="btn btn-primary btn-lg">
                    <i class="bi bi-play-circle me-2"></i>
                    Start Learning Now
                  </router-link>
                </div>
                <div class="col-md-4 text-center">
                  <div class="featured-icon">
                    <i class="bi bi-star-fill fs-1 text-warning"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Learning Tips -->
      <div class="row mt-5">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="bi bi-lightbulb me-2"></i>
                Learning Tips
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-4 mb-3">
                  <div class="tip-item">
                    <i class="bi bi-clock text-primary fs-4"></i>
                    <h6>Take Regular Quizzes</h6>
                    <p class="text-muted small">Practice regularly to reinforce your learning and track your progress.</p>
                  </div>
                </div>
                <div class="col-md-4 mb-3">
                  <div class="tip-item">
                    <i class="bi bi-graph-up text-success fs-4"></i>
                    <h6>Review Your Scores</h6>
                    <p class="text-muted small">Analyze your performance to identify areas for improvement.</p>
                  </div>
                </div>
                <div class="col-md-4 mb-3">
                  <div class="tip-item">
                    <i class="bi bi-people text-info fs-4"></i>
                    <h6>Compete with Peers</h6>
                    <p class="text-muted small">Check the leaderboard to see how you rank among other students.</p>
                  </div>
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
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useStore } from 'vuex'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

export default {
  name: 'Subjects',
  setup() {
    const store = useStore()
    const route = useRoute()
    const router = useRouter()
    
    const subjects = ref([])
    const filteredSubjects = ref([])
    const featuredSubject = ref(null)
    const searchQuery = ref('')
    const sortBy = ref('name')
    const currentSubject = ref(null)
    const chapters = ref([])
    const loading = ref(false)

    // Check if we're viewing a specific subject's chapters
    const isViewingSubject = computed(() => route.params.subjectSlug)

    const fetchSubjects = async () => {
      try {
        loading.value = true
        const response = await api.get('/user/subjects')
        subjects.value = response.data.subjects
        filteredSubjects.value = subjects.value
        
        // Set featured subject (first subject with most quizzes)
        if (subjects.value.length > 0) {
          featuredSubject.value = subjects.value.reduce((prev, current) => 
            (current.quizzes_count > prev.quizzes_count) ? current : prev
          )
        }
      } catch (error) {
        store.dispatch('showError', 'Failed to load subjects')
      } finally {
        loading.value = false
      }
    }

    const fetchSubjectChapters = async (subjectSlug) => {
      try {
        // Clear previous data
        chapters.value = []
        currentSubject.value = null
        
        const response = await api.get(`/user/subjects/${subjectSlug}/chapters`)
        
        currentSubject.value = response.data.subject
        chapters.value = response.data.chapters || []
      } catch (error) {
        chapters.value = []
        currentSubject.value = null
        
        if (error.response?.status === 404) {
          store.dispatch('showError', `Subject not found: ${subjectSlug}`)
        } else {
          store.dispatch('showError', 'Failed to load chapters')
        }
        router.push('/subjects')
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
        subject.description?.toLowerCase().includes(query)
      )
    }

    const sortSubjects = () => {
      const sorted = [...filteredSubjects.value]
      
      switch (sortBy.value) {
        case 'name':
          sorted.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'chapters_count':
          sorted.sort((a, b) => (b.chapters_count || 0) - (a.chapters_count || 0))
          break
        case 'quizzes_count':
          sorted.sort((a, b) => (b.quizzes_count || 0) - (a.quizzes_count || 0))
          break
      }
      
      filteredSubjects.value = sorted
    }

    const refreshData = () => {
      if (isViewingSubject.value) {
        fetchSubjectChapters(route.params.subjectSlug)
      } else {
        fetchSubjects()
      }
    }

    const goBackToSubjects = async () => {
      // Clear chapter data
      chapters.value = []
      currentSubject.value = null
      
      // Navigate to subjects route
      await router.push('/subjects')
      await nextTick()
      
      // Refresh subjects data
      fetchSubjects()
    }

    // Watch for route changes
    watch(
      () => ({ path: route.path, params: route.params, name: route.name }),
      (newRoute, oldRoute) => {
        if (!newRoute || !oldRoute) return
        
        // Navigate to subjects from subject chapters
        if (newRoute.name === 'Subjects' && oldRoute.name === 'SubjectChapters') {
          chapters.value = []
          currentSubject.value = null
          nextTick(() => fetchSubjects())
        }
        // Navigate to subject chapters
        else if (newRoute.name === 'SubjectChapters' && newRoute.params.subjectSlug) {
          fetchSubjectChapters(newRoute.params.subjectSlug)
        }
        // Change between different subjects
        else if (
          newRoute.name === 'SubjectChapters' && 
          oldRoute.name === 'SubjectChapters' &&
          newRoute.params.subjectSlug !== oldRoute.params.subjectSlug
        ) {
          fetchSubjectChapters(newRoute.params.subjectSlug)
        }
      },
      { immediate: false, deep: true }
    )

    onMounted(() => {
      refreshData()
    })

    return {
      subjects,
      filteredSubjects,
      featuredSubject,
      searchQuery,
      sortBy,
      currentSubject,
      chapters,
      loading,
      isViewingSubject,
      filterSubjects,
      sortSubjects,
      refreshData,
      goBackToSubjects
    }
  }
}
</script>

<style scoped>
.subject-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.subject-icon {
  text-align: center;
}

.stat-item {
  padding: 0.5rem;
}

.featured-subject {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.featured-subject .card-body {
  color: white;
}

.featured-icon {
  opacity: 0.8;
}

.tip-item {
  text-align: center;
  padding: 1rem;
}

.tip-item i {
  margin-bottom: 1rem;
}

.tip-item h6 {
  margin-bottom: 0.5rem;
}
</style>
