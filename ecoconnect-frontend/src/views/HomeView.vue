// src/views/HomeView.vue
<template>
  <div class="home">
    <h1>Welcome to EcoConnect</h1>
    <div class="nav-links">
      <router-link to="/login">Login</router-link> |
      <router-link to="/signup">Sign Up</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 20px;
}
.nav-links {
  margin-top: 20px;
}
</style>
