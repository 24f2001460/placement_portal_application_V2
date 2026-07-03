<template>
  <div style="padding-top: 100px;">
    <div class="wf-card">
      <h2 style="text-align: center; margin-top: 0; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px;">Login Form</h2>
      
      <div v-if="error" style="border: 1px solid red; color: red; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div style="margin-bottom: 15px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Username</label>
          <input
            v-model="form.email"
            type="email"
            class="wf-input"
            placeholder="Enter Username"
            required
          />
        </div>

        <div style="margin-bottom: 20px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Password</label>
          <input
            v-model="form.password"
            type="password"
            class="wf-input"
            placeholder="Enter Password"
            required
          />
        </div>

        <div style="text-align: center; margin-bottom: 15px;">
          <button type="submit" class="wf-btn" style="padding: 6px 25px; border: 1px solid #000;" :disabled="loading">
            {{ loading ? 'Loading...' : 'Login' }}
          </button>
        </div>
      </form>

      <div style="text-align: center; font-size: 14px; margin-top: 15px; border-top: 1px solid #ccc; padding-top: 15px;">
        Do not have an account? <router-link to="/register" style="color: #0d6efd; text-decoration: underline;">Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'LoginView',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        const resp = await axios.post('http://127.0.0.1:5000/api/auth/login', this.form)
        localStorage.setItem('token', resp.data.access_token)
        localStorage.setItem('role', resp.data.user.role)
        localStorage.setItem('email', resp.data.user.email)
        
        const role = resp.data.user.role
        if (role === 'admin') {
          this.$router.push('/admin/dashboard')
        } else if (role === 'company') {
          this.$router.push('/company/dashboard')
        } else if (role === 'student') {
          this.$router.push('/student/dashboard')
        }
      } catch (e) {
        this.error = e.response?.data?.error || 'Wrong credentials'
        this.form.password = ''
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
