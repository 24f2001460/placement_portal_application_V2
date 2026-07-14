<template>
  <div style="padding-top: 50px; padding-bottom: 50px;">
    <div class="wf-card" style="max-width: 800px;">
      <h2 style="text-align: center; margin-top: 0; margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px;">Register Form</h2>

      <div v-if="error" style="border: 1px solid red; color: red; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
        {{ error }}
      </div>

      <div v-if="success" style="border: 1px solid green; color: green; padding: 10px; margin-bottom: 15px; border-radius: 4px;">
        {{ success }}
      </div>

      <!-- Account Settings Row -->
      <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Register As</label>
          <select v-model="role" class="wf-select">
            <option value="student">Student</option>
            <option value="company">Company</option>
          </select>
        </div>

        <div style="flex: 1; min-width: 200px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Username (Email)</label>
          <input v-model="form.email" type="email" class="wf-input" placeholder="Enter Username (Email)" required />
        </div>

        <div style="flex: 1; min-width: 200px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Password</label>
          <input v-model="form.password" type="password" class="wf-input" placeholder="Enter Password" required />
        </div>
      </div>

      <!-- Student Fields -->
      <div v-if="role === 'student'">
        <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Full Name</label>
            <input v-model="form.full_name" type="text" class="wf-input" placeholder="Mr. Abcde" required />
          </div>

          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Roll Number</label>
            <input v-model="form.roll_number" type="text" class="wf-input" placeholder="24f200..." required />
          </div>
        </div>

        <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="flex: 2; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Branch</label>
            <select v-model="form.branch" class="wf-select">
              <option value="CSE">Computer Science and Engineering</option>
              <option value="ECE">Electronics and Communication Engineering</option>
              <option value="ME">Mechanical Engineering</option>
              <option value="CE">Civil Engineering</option>
              <option value="EE">Electrical Engineering</option>
            </select>
          </div>

          <div style="flex: 1; min-width: 100px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Year</label>
            <input v-model="form.year" type="number" min="1" max="4" class="wf-input" required />
          </div>

          <div style="flex: 1; min-width: 100px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">CGPA</label>
            <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="wf-input" required />
          </div>
        </div>
      </div>

      <!-- Company Fields -->
      <div v-if="role === 'company'">
        <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Company Name</label>
            <input v-model="form.company_name" type="text" class="wf-input" placeholder="e.g. Google" required />
          </div>

          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Industry</label>
            <input v-model="form.industry" type="text" class="wf-input" placeholder="e.g. IT, Sales" required />
          </div>
        </div>

        <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">HR Contact Name</label>
            <input v-model="form.hr_contact_name" type="text" class="wf-input" placeholder="HR Name" required />
          </div>

          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">HR Phone</label>
            <input v-model="form.hr_phone" type="text" class="wf-input" placeholder="Phone Number" required />
          </div>
        </div>

        <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Company Website</label>
            <input v-model="form.website" type="url" class="wf-input" placeholder="e.g. https://google.com" />
          </div>

          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Headquarters</label>
            <input v-model="form.headquarters" type="text" class="wf-input" placeholder="e.g. Mountain View, CA" />
          </div>
        </div>

        <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Founded Year</label>
            <input v-model="form.founded_year" type="number" class="wf-input" placeholder="e.g. 1998" />
          </div>

          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; font-weight: bold; margin-bottom: 5px;">Number of Employees</label>
            <input v-model="form.employee_count" type="text" class="wf-input" placeholder="e.g. 150000 or 100-500" />
          </div>
        </div>

        <div style="margin-bottom: 15px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Company Description</label>
          <textarea v-model="form.description" class="wf-input" rows="3" placeholder="Briefly describe the company organization..."></textarea>
        </div>
      </div>

      <div style="text-align: center; margin-top: 20px;">
        <button @click="handleRegister" class="wf-btn wf-btn-primary" style="padding: 8px 30px; border: 1px solid #000;" :disabled="loading">
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </div>

      <div style="text-align: center; font-size: 14px; margin-top: 15px; border-top: 1px solid #ccc; padding-top: 15px;">
        Already have an account? <router-link to="/login" style="color: #0d6efd; text-decoration: underline;">Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterView',
  data() {
    return {
      role: 'student',
      error: '',
      success: '',
      loading: false,
      form: {
        email: '',
        password: '',
        full_name: '',
        roll_number: '',
        branch: 'CSE',
        year: 1,
        cgpa: 8.0,
        company_name: '',
        hr_contact_name: '',
        hr_phone: '',
        industry: '',
        website: '',
        description: '',
        headquarters: '',
        founded_year: '',
        employee_count: ''
      }
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        const url = `http://localhost:5000/api/auth/register/${this.role}`
        const resp = await axios.post(url, this.form)
        this.success = resp.data.message
        setTimeout(() => this.$router.push('/login'), 2000)
      } catch (e) {
        this.error = e.response?.data?.error || 'Registration failed!'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
