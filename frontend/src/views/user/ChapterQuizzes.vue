<template>
  <div class="container-fluid">
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-0">
            <i class="bi bi-question-circle me-2"></i>
            {{ chapter?.name }} - Quizzes
          </h1>
          <p class="text-muted mb-0">{{ chapter?.description }}</p>
        </div>
        <div>
          <button class="btn btn-outline-secondary" @click="goBack">
            <i class="bi bi-arrow-left me-2"></i>
            Back to Chapters
          </button>
        </div>
      </div>
    </div>
    
    <div class="row g-4">
             <div v-for="quiz in quizzes" :key="quiz.id" class="col-md-6 col-lg-4">
         <div class="card quiz-card h-100">
           <div class="card-body">
             <h5 class="card-title">{{ quiz.title }}</h5>
            <p class="card-text text-muted">{{ quiz.description || 'No description' }}</p>
            <div class="quiz-meta mb-2">
              <span class="badge bg-info me-2">{{ quiz.duration_minutes }} min</span>
              <span class="badge bg-success">{{ quiz.total_questions || quiz.questions?.length || 0 }} questions</span>
            </div>
            <div class="quiz-status mb-3">
              <span v-if="quiz.can_attempt" class="badge bg-success">Available</span>
              <span v-else-if="quiz.user_attempts >= quiz.max_attempts" class="badge bg-warning">Max Attempts Reached</span>
              <span v-else class="badge bg-secondary">{{ quiz.status }}</span>
            </div>
                         <div class="d-grid">
               <router-link :to="`/quiz/${quiz.slug}/info`" class="btn btn-primary">
                 <i class="bi bi-play-circle me-2"></i>
                 Take Quiz
               </router-link>
             </div>
          </div>
        </div>
      </div>
      
      <div v-if="quizzes.length === 0" class="col-12">
        <div class="text-center py-5">
          <i class="bi bi-inbox fs-1 text-muted"></i>
          <h4 class="text-muted mt-3">No quizzes available for this chapter</h4>
          <p class="text-muted">Check back later for new quizzes.</p>
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
  name: 'ChapterQuizzes',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()
    const chapter = ref(null)
    const quizzes = ref([])

    const fetchQuizzes = async () => {
      try {
        const chapterSlug = route.params.chapterSlug
        const subjectSlug = route.params.subjectSlug
        
        let response
        if (subjectSlug) {
          response = await api.get(`/user/subjects/${subjectSlug}/chapters/${chapterSlug}/quizzes`)
        } else {
          response = await api.get(`/user/chapters/${chapterSlug}/quizzes`)
        }
        
        chapter.value = response.data.chapter
        if(chapter == undefined) {window.location.reload();}
        quizzes.value = response.data.quizzes || []
      } catch (error) {
        if (error.response?.status === 400 && error.response?.data?.available_chapters) {
          store.dispatch('showError', error.response.data.error)
        } else {
          store.dispatch('showError', 'Failed to load quizzes')
        }
        quizzes.value = []
      }
    }

    const goBack = () => {
      const subjectSlug = route.params.subjectSlug
      if (subjectSlug) {
        router.push(`/subjects/${subjectSlug}/chapters`)
      } else if (chapter.value?.subject_id) {
        router.push(`/subjects/${chapter.value.subject_slug}/chapters`)
      } else {
        router.push('/subjects')
      }
    }

    onMounted(() => {
      fetchQuizzes()
    })

    return {
      chapter,
      quizzes,
      goBack
    }
  }
}
</script>

<style scoped>
.quiz-card {
  transition: transform 0.2s, box-shadow 0.2s;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.quiz-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.quiz-meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.quiz-status {
  display: flex;
  gap: 0.5rem;
}
</style>
