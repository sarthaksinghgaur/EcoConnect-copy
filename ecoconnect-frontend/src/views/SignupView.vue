// src/views/SignupView.vue
<template>
  <div class="signup">
    <h2>Sign Up</h2>
    <form @submit.prevent="handleSignup">
      <div>
        <input 
          type="text" 
          v-model="username" 
          placeholder="Username"
          required
        >
      </div>
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
      <button type="submit">Sign Up</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SignupView',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      error: null
    }
  },
  methods: {
    async handleSignup() {
      try {
        await axios.post('http://localhost:5000/api/auth/signup', {
          username: this.username,
          email: this.email,
          password: this.password
        })

        this.error = null
        alert('Signup successful! Please login with your credentials.')
        this.$router.push('/login')
      } catch (err) {
        this.error = err.response?.data?.error || 'Signup failed'
      }
    }
  }
}
</script>

<style scoped>
.signup {
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