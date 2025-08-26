<template>
  <div id="app">
    <!-- Public/Guest Navbar (Home, Login, Register pages) -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm" v-if="!isAuthenticated">
      <div class="container">
        <router-link class="navbar-brand fw-bold d-flex align-items-center" to="/">
          <img src="https://raw.githubusercontent.com/23f2003700/B/refs/heads/main/topim.png" 
               alt="IIT Madras Logo" 
               class="navbar-brand-logo me-2">
          Quiz Master V2
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#guestNavbar">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="guestNavbar">
          <div class="navbar-nav ms-auto">
            <router-link to="/" class="nav-link" 
                         :class="{ 'active fw-semibold': $route.name === 'Home' }">
              <i class="bi bi-house me-1"></i>
              Home
            </router-link>
            <router-link to="/login" class="btn btn-outline-light me-2"
                         :class="{ 'active': $route.name === 'Login' }">
              <i class="bi bi-box-arrow-in-right me-1"></i>
              Login
            </router-link>
            <router-link to="/register" class="btn btn-light"
                         :class="{ 'active': $route.name === 'Register' }">
              <i class="bi bi-person-plus me-1"></i>
              Register
            </router-link>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Authenticated User Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm" v-if="isAuthenticated">
      <div class="container-fluid">
        <router-link class="navbar-brand fw-bold d-flex align-items-center" to="/">
          <img src="https://raw.githubusercontent.com/23f2003700/B/refs/heads/main/topim.png" 
               alt="IIT Madras Logo" 
               class="navbar-brand-logo me-2">
          Quiz Master V2
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <template v-if="userRole === 'admin'">
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/dashboard">
                  <i class="bi bi-speedometer2 me-1"></i> Dashboard
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/subjects">
                  <i class="bi bi-book me-1"></i> Subjects
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/quizzes">
                  <i class="bi bi-question-circle me-1"></i> Quizzes
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/users">
                  <i class="bi bi-people me-1"></i> Users
                </router-link>
              </li>
            </template>
            
            <template v-else>
              <li class="nav-item">
                <router-link class="nav-link" to="/dashboard">
                  <i class="bi bi-house me-1"></i> Dashboard
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/subjects">
                  <i class="bi bi-collection me-1"></i> Subjects
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/scores">
                  <i class="bi bi-trophy me-1"></i> My Scores
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/leaderboard">
                  <i class="bi bi-award me-1"></i> Leaderboard
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/reminders">
                  <i class="bi bi-bell me-1"></i> Reminders
                  <span v-if="unreadReminders > 0" class="badge bg-danger ms-1">{{ unreadReminders }}</span>
                </router-link>
              </li>
            </template>
          </ul>
          
          <div class="d-flex align-items-center">
            <form class="d-flex me-3" @submit.prevent="handleSearch">
              <input 
                class="form-control form-control-sm me-2" 
                type="search" 
                placeholder="Search..." 
                v-model="searchQuery"
              >
              <button class="btn btn-outline-light btn-sm" type="submit">
                <i class="bi bi-search"></i>
              </button>
            </form>
            
            <div class="dropdown">
              <button 
                class="btn btn-outline-light btn-sm dropdown-toggle" 
                type="button" 
                data-bs-toggle="dropdown"
              >
                <i class="bi bi-person-circle me-1"></i>
                {{ currentUser?.full_name || currentUser?.email }}
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <router-link class="dropdown-item" :to="userRole === 'admin' ? '/admin/profile' : '/profile'">
                    <i class="bi bi-person me-2"></i> Profile
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item text-danger" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right me-2"></i> Logout
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <main class="main-content" :class="{ 'no-padding': $route.name === 'Home' }">
      <router-view></router-view>
    </main>
    
    <!-- Toast Container -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="toast show"
        :class="`border-${toast.type}`"
      >
        <div class="toast-header">
          <i :class="`bi bi-${getToastIcon(toast.type)} me-2 text-${toast.type}`"></i>
          <strong class="me-auto">{{ toast.title }}</strong>
          <button type="button" class="btn-close" @click="removeToast(toast.id)"></button>
        </div>
        <div class="toast-body">
          {{ toast.message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const store = useStore()
    const router = useRouter()
    const searchQuery = ref('')
    
    const isAuthenticated = computed(() => store.getters['auth/isAuthenticated'])
    const currentUser = computed(() => store.getters['auth/currentUser'])
    const userRole = computed(() => store.getters['auth/userRole'])
    const toasts = computed(() => store.state.toasts)
    const unreadReminders = computed(() => store.state.reminders?.unread_count || 0)
    
    const handleSearch = () => {
      if (searchQuery.value.trim()) {
        router.push({ 
          name: 'Search', 
          query: { q: searchQuery.value }
        })
        searchQuery.value = ''
      }
    }
    
    const logout = async () => {
      await store.dispatch('auth/logout')
      router.push('/login')
    }
    
    const removeToast = (id) => {
      store.commit('REMOVE_TOAST', id)
    }
    
    const getToastIcon = (type) => {
      const icons = {
        success: 'check-circle-fill',
        error: 'x-circle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill'
      }
      return icons[type] || 'info-circle-fill'
    }
    
    return {
      isAuthenticated,
      currentUser,
      userRole,
      toasts,
      unreadReminders,
      searchQuery,
      handleSearch,
      logout,
      removeToast,
      getToastIcon
    }
  }
}
</script>

<style>
:root {
  --primary-color: #4f46e5;
  --secondary-color: #7c3aed;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #3b82f6;
  --dark-color: #1f2937;
  --light-color: #f9fafb;
}

* {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f3f4f6;
  margin: 0;
  padding: 0;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 2rem 0;
}

.navbar {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
}

.navbar-brand {
  font-size: 1.5rem;
  letter-spacing: -0.5px;
}

.nav-link {
  transition: all 0.3s ease;
  border-radius: 0.375rem;
  margin: 0 0.25rem;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.router-link-active {
  background-color: rgba(255, 255, 255, 0.2) !important;
}

.card {
  border: none;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.btn {
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn:active {
  transform: scale(0.95);
}

.toast {
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Guest Navbar Styles */
.navbar .nav-link.active {
  color: #fff !important;
  font-weight: 600;
}

.navbar .btn.active {
  opacity: 0.9;
  box-shadow: inset 0 3px 5px rgba(0,0,0,.125);
}

/* Logo Styles */
.navbar-logo {
  display: flex;
  align-items: center;
}

.navbar-logo-img {
  height: 50px;
  width: auto;
  border-radius: 8px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.navbar-logo-img:hover {
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.navbar-logo-auth {
  display: flex;
  align-items: center;
  margin-left: 1rem;
}

.navbar-brand-logo {
  height: 32px;
  width: auto;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.navbar-brand-logo:hover {
  transform: scale(1.05);
}

/* Remove main content padding for home page */
.main-content.no-padding {
  padding: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .main-content {
    padding: 1rem 0;
  }
  
  .navbar-logo-img {
    height: 40px;
  }
  
  .navbar-logo-img-small {
    height: 30px;
  }
  
  .navbar-nav.ms-3 {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style> 