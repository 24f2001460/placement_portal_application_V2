<template>
  <div class="container-fluid bg-light min-vh-100 d-flex justify-content-center align-items-center">

    <div class="card shadow border-0" style="max-width:420px;width:100%;">

      <div class="card-body p-4">

        <!-- Logo -->
        <div class="text-center mb-4">
          <div
            class="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center fs-2"
            style="width:70px;height:70px;">
            🎓
          </div>

          <h3 class="fw-bold mt-3 mb-1">
            Placement Portal
          </h3>

          <p class="text-muted mb-0">
            Sign in to your account
          </p>
        </div>

        <!-- Error -->
        <div
          v-if="error"
          class="alert alert-danger">
          {{ error }}
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin">

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

          <div class="mb-4">

            <label class="form-label">
              Password
            </label>

            <input
              v-model="form.password"
              type="password"
              class="form-control"
              placeholder="Enter password"
              required>

          </div>

          <button
            class="btn btn-primary w-100"
            type="submit"
            :disabled="loading">

            <span
              v-if="loading"
              class="spinner-border spinner-border-sm me-2">
            </span>

            {{ loading ? "Signing In..." : "Login" }}

          </button>

        </form>

        <hr class="my-4">

        <p class="text-center mb-0 text-muted">

          Don't have an account?

          <router-link
            to="/register"
            class="text-decoration-none fw-semibold">

            Register

          </router-link>

        </p>

      </div>

    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LoginView",

  data() {
    return {
      form: {
        email: "",
        password: ""
      },
      loading: false,
      error: ""
    };
  },

  methods: {
    async handleLogin() {

      this.loading = true;
      this.error = "";

      try {

        const resp = await axios.post(
          "http://127.0.0.1:5000/api/auth/login",
          this.form
        );

        localStorage.setItem(
          "token",
          resp.data.access_token
        );

        localStorage.setItem(
          "role",
          resp.data.user.role
        );

        const role = resp.data.user.role;

        if (role === "admin") {
          this.$router.push("/admin/dashboard");
        }

        if (role === "company") {
          this.$router.push("/company/dashboard");
        }

        if (role === "student") {
          this.$router.push("/student/dashboard");
        }

      } catch (e) {

        this.error =
          e.response?.data?.error ||
          "Login Failed";

        this.form.password = "";

      } finally {

        this.loading = false;

      }
    }
  }
};
</script>

<style scoped>

.card{
    border-radius:12px;
}

</style>
