<template>
  <div class="test-home">
    <h1>🎉 SUCCESS! Home Page is Working!</h1>
    <p>This proves the routing issue is fixed.</p>
    
    <div class="test-info">
      <h2>Student Information</h2>
      <p><strong>Name:</strong> Aaryan Choudhary</p>
      <p><strong>Roll No:</strong> 23F2003700</p>
      <p><strong>Course:</strong> Diploma in Data Science</p>
      <p><strong>Institution:</strong> IIT Madras</p>
    </div>
    
    <div class="test-links">
      <router-link to="/login" class="btn btn-primary">Login</router-link>
      <router-link to="/register" class="btn btn-secondary">Register</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestHome'
}
</script>

<style scoped>
.test-home {
  padding: 2rem;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
}

.test-info {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  border-radius: 10px;
  margin: 2rem auto;
  max-width: 400px;
}

.test-links {
  margin-top: 2rem;
}

.btn {
  margin: 0 1rem;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 5px;
  display: inline-block;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}
</style> 