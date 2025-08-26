<template>
  <div class="home-page">
    <!-- Hero Section with Background Image -->
    <section class="hero-section">
      <div class="hero-overlay">
        <div class="container">
          <div class="row align-items-center min-vh-100">
            <div class="col-lg-6">
              <div class="hero-content">
                <h1 class="hero-title">Quiz Master V2</h1>
                <h2 class="hero-subtitle">Modern Application Development II (MAD-II)</h2>
                <div class="student-info">
                  <h3>Student Information</h3>
                  <p><strong>Name:</strong> Aaryan Choudhary</p>
                  <p><strong>Roll No:</strong> 23F2003700</p>
                  <p><strong>Course:</strong> Diploma in Data Science</p>
                  <p><strong>Institution:</strong> IIT Madras</p>
                </div>
                <div class="feature-highlights">
                  <div class="feature-item">
                    <i class="bi bi-trophy-fill"></i>
                    <span>Interactive Quizzes</span>
                  </div>
                  <div class="feature-item">
                    <i class="bi bi-graph-up"></i>
                    <span>Performance Analytics</span>
                  </div>
                  <div class="feature-item">
                    <i class="bi bi-clock-fill"></i>
                    <span>Real-time Scoring</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-lg-6">
              <div class="access-cards">
                <div class="access-card admin-card">
                  <div class="card-icon">
                    <i class="bi bi-gear-fill"></i>
                  </div>
                  <h3>Admin / Quiz Master</h3>
                  <p>Complete control over quiz management, user monitoring, and system analytics</p>
                  <ul class="features-list">
                    <li><i class="bi bi-check-circle-fill"></i> Manage Subjects & Chapters</li>
                    <li><i class="bi bi-check-circle-fill"></i> Create & Schedule Quizzes</li>
                    <li><i class="bi bi-check-circle-fill"></i> Monitor User Performance</li>
                    <li><i class="bi bi-check-circle-fill"></i> Generate Reports</li>
                  </ul>
                  <router-link to="/login" class="btn btn-admin">
                    <i class="bi bi-person-gear"></i>
                    Admin Login
                  </router-link>
                  <small class="text-muted">Pre-registered Account Available</small>
                </div>

                <div class="access-card user-card">
                  <div class="card-icon">
                    <i class="bi bi-person-fill"></i>
                  </div>
                  <h3>User / Student</h3>
                  <p>Access engaging quizzes, track your progress, and compete with peers</p>
                  <ul class="features-list">
                    <li><i class="bi bi-check-circle-fill"></i> Take Interactive Quizzes</li>
                    <li><i class="bi bi-check-circle-fill"></i> View Score History</li>
                    <li><i class="bi bi-check-circle-fill"></i> Access Leaderboards</li>
                    <li><i class="bi bi-check-circle-fill"></i> Track Performance</li>
                  </ul>
                  <div class="user-actions">
                    <router-link to="/login" class="btn btn-user">
                      <i class="bi bi-box-arrow-in-right"></i>
                      Student Login
                    </router-link>
                    <router-link to="/register" class="btn btn-user-outline">
                      <i class="bi bi-person-plus"></i>
                      Register Now
                    </router-link>
                  </div>
                  <small class="text-muted">Multiple Accounts via Registration</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Key Features Section -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title text-center">Key Features</h2>
        <div class="row">
          <div class="col-md-4">
            <div class="feature-box">
              <div class="feature-icon">
                <i class="bi bi-database-fill"></i>
              </div>
              <h4>Smart Database Design</h4>
              <p>Structured data management with SQLite and Redis caching for optimal performance</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-box">
              <div class="feature-icon">
                <i class="bi bi-shield-check"></i>
              </div>
              <h4>Secure Authentication</h4>
              <p>JWT-based authentication with role-based access control for admins and users</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-box">
              <div class="feature-icon">
                <i class="bi bi-calendar-check"></i>
              </div>
              <h4>Quiz Scheduling</h4>
              <p>Advanced scheduling system with automated reminders and time-locked assessments</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-box">
              <div class="feature-icon">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <h4>Analytics & Reports</h4>
              <p>Comprehensive performance analytics with CSV exports and visual dashboards</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-box">
              <div class="feature-icon">
                <i class="bi bi-search"></i>
              </div>
              <h4>Advanced Search</h4>
              <p>Powerful search capabilities across quizzes, subjects, and user performance data</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-box">
              <div class="feature-icon">
                <i class="bi bi-phone"></i>
              </div>
              <h4>Responsive Design</h4>
              <p>Mobile-friendly interface with Bootstrap styling for seamless cross-device experience</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Tech Stack Section -->
    <section class="tech-stack-section">
      <div class="container">
        <h2 class="section-title text-center">Technology Stack</h2>
        <div class="row">
          <div class="col-md-6">
            <h4><i class="bi bi-server"></i> Backend Technologies</h4>
            <div class="tech-grid">
              <div class="tech-item">
                <i class="bi bi-flask"></i>
                <span>Flask</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-database"></i>
                <span>SQLite</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-memory"></i>
                <span>Redis</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-gear"></i>
                <span>Celery</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-shield"></i>
                <span>JWT Auth</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-file-earmark-text"></i>
                <span>SQLAlchemy</span>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <h4><i class="bi bi-laptop"></i> Frontend Technologies</h4>
            <div class="tech-grid">
              <div class="tech-item">
                <i class="bi bi-code-square"></i>
                <span>Vue.js 3</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-bootstrap"></i>
                <span>Bootstrap 5</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-router"></i>
                <span>Vue Router</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-box"></i>
                <span>Vuex</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-arrow-repeat"></i>
                <span>Axios</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-bar-chart"></i>
                <span>Chart.js</span>
              </div>
            </div>
          </div>
        </div>
        <div class="row mt-4">
          <div class="col-12 text-center">
            <h4><i class="bi bi-tools"></i> Development & Deployment</h4>
            <div class="tech-grid justify-content-center">
              <div class="tech-item">
                <i class="bi bi-ubuntu"></i>
                <span>Ubuntu/WSL</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-lightning"></i>
                <span>Vite</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-npm"></i>
                <span>NPM</span>
              </div>
              <div class="tech-item">
                <i class="bi bi-python"></i>
                <span>Python 3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  mounted() {
    // Add any initialization logic here
  }
}
</script>

<style scoped>
/* Hero Section */
.hero-section {
  background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)),
              url('https://raw.githubusercontent.com/23f2003700/B/refs/heads/main/Quizme.png');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  position: relative;
}

.hero-overlay {
  background: linear-gradient(135deg, rgba(74, 144, 226, 0.1), rgba(80, 227, 194, 0.1));
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.hero-content {
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.hero-title {
  font-size: 4rem;
  font-weight: 700;
  background: linear-gradient(45deg, #4A90E2, #50E3C2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
}

.hero-subtitle {
  font-size: 1.8rem;
  color: #FFD700;
  margin-bottom: 2rem;
  font-weight: 500;
}

.student-info {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.student-info h3 {
  color: #FFD700;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.student-info p {
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.feature-highlights {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #50E3C2;
  font-weight: 500;
}

.feature-item i {
  font-size: 1.2rem;
}

/* Access Cards */
.access-cards {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.access-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.access-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 25px 45px rgba(0, 0, 0, 0.3);
}

.admin-card {
  border-left: 5px solid #E74C3C;
}

.user-card {
  border-left: 5px solid #4A90E2;
}

.card-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: white;
}

.admin-card .card-icon {
  background: linear-gradient(45deg, #E74C3C, #C0392B);
}

.user-card .card-icon {
  background: linear-gradient(45deg, #4A90E2, #3498DB);
}

.access-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #2C3E50;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  text-align: left;
}

.features-list li {
  padding: 0.5rem 0;
  color: #555;
}

.features-list i {
  color: #27AE60;
  margin-right: 0.5rem;
}

.btn-admin {
  background: linear-gradient(45deg, #E74C3C, #C0392B);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  margin: 0.5rem;
  transition: all 0.3s ease;
}

.btn-admin:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(231, 76, 60, 0.3);
  color: white;
  text-decoration: none;
}

.btn-user {
  background: linear-gradient(45deg, #4A90E2, #3498DB);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  margin: 0.25rem;
  transition: all 0.3s ease;
}

.btn-user:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(74, 144, 226, 0.3);
  color: white;
  text-decoration: none;
}

.btn-user-outline {
  background: transparent;
  border: 2px solid #4A90E2;
  color: #4A90E2;
  padding: 10px 22px;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  display: inline-block;
  margin: 0.25rem;
  transition: all 0.3s ease;
}

.btn-user-outline:hover {
  background: #4A90E2;
  color: white;
  text-decoration: none;
}

.user-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Features Section */
.features-section {
  padding: 5rem 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2C3E50;
  margin-bottom: 3rem;
}

.feature-box {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.feature-box:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: white;
  background: linear-gradient(45deg, #4A90E2, #50E3C2);
}

.feature-box h4 {
  font-size: 1.3rem;
  color: #2C3E50;
  margin-bottom: 1rem;
}

.feature-box p {
  color: #7F8C8D;
  line-height: 1.6;
}

/* Tech Stack Section */
.tech-stack-section {
  padding: 5rem 0;
  background: #2C3E50;
  color: white;
}

.tech-stack-section .section-title {
  color: white;
}

.tech-stack-section h4 {
  color: #FFD700;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.tech-item {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.tech-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-5px);
}

.tech-item i {
  font-size: 2rem;
  color: #50E3C2;
  margin-bottom: 0.5rem;
  display: block;
}

.tech-item span {
  font-weight: 500;
  font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1.3rem;
  }
  
  .access-cards {
    gap: 1rem;
  }
  
  .feature-highlights {
    flex-direction: column;
    gap: 1rem;
  }
  
  .user-actions {
    flex-direction: column;
  }
  
  .tech-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .hero-content {
    text-align: center;
  }
  
  .student-info {
    margin-bottom: 1rem;
  }
  
  .access-card {
    padding: 1.5rem;
  }
}
</style> 