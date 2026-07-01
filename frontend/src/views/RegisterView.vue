<template>
  <div class="container-fluid bg-light min-vh-100 d-flex justify-content-center align-items-center py-4">

    <div class="card shadow border-0" style="max-width:520px;width:100%;">

      <div class="card-body p-4">

        <!-- Logo -->
        <div class="text-center mb-4">

          <div
            class="rounded-circle bg-primary text-white d-inline-flex justify-content-center align-items-center fs-2"
            style="width:70px;height:70px;">

            📝

          </div>

          <h3 class="fw-bold mt-3 mb-1">
            Create Account
          </h3>

          <p class="text-muted mb-0">
            Join Placement Portal
          </p>

        </div>

        <!-- Alerts -->

        <div
          v-if="error"
          class="alert alert-danger">

          {{ error }}

        </div>

        <div
          v-if="success"
          class="alert alert-success">

          {{ success }}

        </div>

        <!-- Register As -->

        <div class="mb-3">

          <label class="form-label">
            Register As
          </label>

          <select
            v-model="role"
            class="form-select">

            <option value="student">
              Student
            </option>

            <option value="company">
              Company
            </option>

          </select>

        </div>

        <!-- Email -->

        <div class="mb-3">

          <label class="form-label">
            Email
          </label>

          <input
            v-model="form.email"
            type="email"
            class="form-control"
            placeholder="Enter email"
            required>

        </div>

        <!-- Password -->

        <div class="mb-4">

          <label class="form-label">
            Password
          </label>

          <input
            v-model="form.password"
            type="password"
            class="form-control"
            placeholder="Create password"
            required>

        </div>

        <!-- Student Form -->

        <template v-if="role==='student'">

          <div class="mb-3">

            <label class="form-label">
              Full Name
            </label>

            <input
              v-model="form.full_name"
              class="form-control"
              placeholder="Enter full name">

          </div>

          <div class="mb-3">

            <label class="form-label">
              Roll Number
            </label>

            <input
              v-model="form.roll_number"
              class="form-control"
              placeholder="Enter roll number">

          </div>

          <div class="mb-3">

            <label class="form-label">
              Branch
            </label>

            <select
              v-model="form.branch"
              class="form-select">

              <option>CSE</option>
              <option>ECE</option>
              <option>ME</option>
              <option>CE</option>
              <option>EE</option>

            </select>

          </div>

          <div class="row">

            <div class="col-md-6 mb-3">

              <label class="form-label">
                Year
              </label>

              <input
                v-model="form.year"
                type="number"
                class="form-control">

            </div>

            <div class="col-md-6 mb-3">

              <label class="form-label">
                CGPA
              </label>

              <input
                v-model="form.cgpa"
                type="number"
                step="0.1"
                class="form-control">

            </div>

          </div>

        </template>

        <!-- Company Form -->

        <template v-else>

          <div class="mb-3">

            <label class="form-label">
              Company Name
            </label>

            <input
              v-model="form.company_name"
              class="form-control"
              placeholder="Enter company name">

          </div>

          <div class="mb-3">

            <label class="form-label">
              HR Contact Name
            </label>

            <input
              v-model="form.hr_contact_name"
              class="form-control"
              placeholder="Enter HR contact name">

          </div>

          <div class="mb-3">

            <label class="form-label">
              HR Phone
            </label>

            <input
              v-model="form.hr_phone"
              class="form-control"
              placeholder="Enter phone number">

          </div>

          <div class="mb-4">

            <label class="form-label">
              Website
            </label>

            <input
              v-model="form.website"
              class="form-control"
              placeholder="https://company.com">

          </div>

        </template>

        <!-- Register Button -->

        <button
          class="btn btn-primary w-100"
          :disabled="loading"
          @click="handleRegister">

          <span
            v-if="loading"
            class="spinner-border spinner-border-sm me-2">
          </span>

          {{ loading ? "Creating Account..." : "Create Account" }}

        </button>

        <hr class="my-4">

        <p class="text-center mb-0 text-muted">

          Already have an account?

          <router-link
            to="/login"
            class="text-decoration-none fw-semibold">

            Login

          </router-link>

        </p>

      </div>

    </div>

  </div>
</template>

<style scoped>

.card{
    border-radius:12px;
    max-height:90vh;
    overflow-y:auto;
}

</style>

<script>
import axios from 'axios'

export default {
  name: 'StudentRegister',

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
        cgpa: 0,

        company_name: '',
        hr_contact_name: '',
        hr_phone: '',
        website: ''
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

        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)

      } catch (e) {

        this.error =
          e.response?.data?.error ||
          'Registration failed!'

      } finally {

        this.loading = false

      }

    }

  }

}
</script>
