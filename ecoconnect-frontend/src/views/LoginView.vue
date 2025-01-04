// src/views/LoginView.vue
<template>
  <div class="login">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <input 
          type="email" 
          v-model="email" 
          placeholder="Email"
          required
        >
      </div>
      <div>
        <input 
          type="password" 
          v-model="password" 
          placeholder="Password"
          required
        >
      </div>
      <button type="submit">Login</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginView',
  data() {
    return {
      email: '',
      password: '',
      error: null
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post('http://localhost:5000/api/auth/login', {
          email: this.email,
          password: this.password
        })

        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('refreshToken', response.data.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))

        // Check if user is admin and redirect accordingly
        if (response.data.user.email === 'admin@ecoconnect.com') {
          this.$router.push('/admin-dashboard')
        } else {
          this.$router.push('/dashboard')
        }
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed'
      }
    }
  }
}
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
}
form div {
  margin: 10px 0;
}
input {
  width: 100%;
  padding: 8px;
  margin: 5px 0;
}
.error {
  color: red;
}
</style>