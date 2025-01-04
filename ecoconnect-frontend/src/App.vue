// src/App.vue
<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <template v-if="!isLoggedIn">
        <router-link to="/login">Login</router-link> |
        <router-link to="/signup">Sign Up</router-link>
      </template>
    </nav>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token')
    }
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  margin: 0 10px;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>