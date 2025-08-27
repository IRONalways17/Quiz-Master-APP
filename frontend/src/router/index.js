import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

// Home Route
import Home from '@/views/Home.vue'
import TestHome from '@/views/TestHome.vue'

// Auth Routes
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'

// User Routes
import UserDashboard from '@/views/user/Dashboard.vue'
import Subjects from '@/views/user/Subjects.vue'
import ChapterQuizzes from '@/views/user/ChapterQuizzes.vue'
import QuizInfo from '@/views/user/QuizInfo.vue'
import TakeQuiz from '@/views/user/TakeQuiz.vue'
import QuizResult from '@/views/user/QuizResult.vue'
import Scores from '@/views/user/Scores.vue'
import ScoreDetail from '@/views/user/ScoreDetail.vue'
import Leaderboard from '@/views/user/Leaderboard.vue'
import Profile from '@/views/user/Profile.vue'
import Reminders from '@/views/user/Reminders.vue'

// Admin Routes
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminSubjects from '@/views/admin/Subjects.vue'
import AdminChapters from '@/views/admin/Chapters.vue'
import AdminQuizzes from '@/views/admin/Quizzes.vue'
import AdminQuestions from '@/views/admin/Questions.vue'
import AdminUsers from '@/views/admin/Users.vue'
import AdminProfile from '@/views/admin/Profile.vue'

// Common Routes
import Search from '@/views/common/Search.vue'
import NotFound from '@/views/common/NotFound.vue'

const routes = [
  // Home Route - Always public, no authentication required
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { 
      public: true,
      requiresAuth: false,
      requiresGuest: false
    }
  },
  
  // Auth Routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  
  // User Routes
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/subjects',
    name: 'Subjects',
    component: Subjects,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/subjects/:subjectSlug/chapters',
    name: 'SubjectChapters',
    component: Subjects,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/subjects/:subjectSlug/chapters/:chapterSlug/quizzes',
    name: 'ChapterQuizzes',
    component: ChapterQuizzes,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/chapters/:chapterSlug/quizzes',
    name: 'ChapterQuizzesDeprecated',
    component: ChapterQuizzes,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/quiz/:quizSlug/info',
    name: 'QuizInfo',
    component: QuizInfo,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/quiz/:quizSlug/take',
    name: 'TakeQuiz',
    component: TakeQuiz,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/quiz/:quizSlug/result',
    name: 'QuizResult',
    component: QuizResult,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/scores',
    name: 'Scores',
    component: Scores,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/scores/:scoreId',
    name: 'ScoreDetail',
    component: ScoreDetail,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/leaderboard',
    name: 'Leaderboard',
    component: Leaderboard,
    meta: { requiresAuth: true, role: 'user' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/reminders',
    name: 'Reminders',
    component: Reminders,
    meta: { requiresAuth: true, role: 'user' }
  },
  
  // Admin Routes
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/subjects',
    name: 'AdminSubjects',
    component: AdminSubjects,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/subjects/:subjectId/chapters',
    name: 'AdminChapters',
    component: AdminChapters,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/chapters/:chapterId/quizzes',
    name: 'AdminQuizzes',
    component: AdminQuizzes,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/quizzes',
    name: 'AdminQuizzesList',
    component: AdminQuizzes,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/quizzes/:quizId/questions',
    name: 'AdminQuestions',
    component: AdminQuestions,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/profile',
    name: 'AdminProfile',
    component: AdminProfile,
    meta: { requiresAuth: true, role: 'admin' }
  },
  
  // Common Routes
  {
    path: '/search',
    name: 'Search',
    component: Search,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation Guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  const userRole = store.getters['auth/userRole']
  
  // Always allow access to Home page, login and register - no authentication checks
  if (to.name === 'Home' || to.path === '/' || to.name === 'Login' || to.name === 'Register') {
    console.log('Allowing access to public route:', to.name, to.path)
    
    // If authenticated user tries to access auth pages, redirect to dashboard
    if ((to.name === 'Login' || to.name === 'Register') && isAuthenticated) {
      console.log('Authenticated user accessing auth page, redirecting to dashboard')
      return next(userRole === 'admin' ? '/admin/dashboard' : '/dashboard')
    }
    
    // Only clear stale auth data if there's actually expired tokens
    if (to.name === 'Login' || to.name === 'Register') {
      const token = store.state.auth.token
      if (token && !isAuthenticated) {
        console.log('Clearing stale/expired auth state on auth page access')
        store.commit('auth/CLEAR_AUTH')
      }
    }
    
    return next()
  }
  
  
  console.log('Router guard check:', { to: to.name, isAuthenticated, userRole })
  
  // Check if route requires guest (but we already handled auth pages above)
  if (to.meta.requiresGuest && isAuthenticated) {
    return next(userRole === 'admin' ? '/admin/dashboard' : '/dashboard')
  }
  
  // Check if route requires auth
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }
  
  // Check role requirements
  if (to.meta.role && to.meta.role !== userRole) {
    return next(userRole === 'admin' ? '/admin/dashboard' : '/dashboard')
  }
  
  next()
})

export default router 