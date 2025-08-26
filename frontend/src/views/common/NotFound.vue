<template>
  <div class="container">
    <div class="row justify-content-center align-items-center min-vh-100">
      <div class="col-md-6 text-center">
        <h1 class="display-1 text-primary">404</h1>
        <h2 class="mb-4">Page Not Found</h2>
        <p class="text-muted mb-4">The page you're looking for doesn't exist.</p>
        <router-link to="/" class="btn btn-primary">
          <i class="bi bi-house me-2"></i>
          Go Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script> 