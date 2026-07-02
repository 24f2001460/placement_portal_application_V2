<template>
<div class="min-vh-100 bg-light">

  <!-- Navbar -->
  <nav class="navbar navbar-dark bg-dark px-4">
    <span class="navbar-brand">
      🎓 Admin Dashboard
    </span>

    <div class="d-flex align-items-center">
      <span class="text-white me-3">
        <i class="bi bi-person-circle"></i>
        {{email}}
      </span>

      <button @click="logout" class="btn btn-outline-light btn-sm">
        Logout
      </button>
    </div>
  </nav>


  <div class="container py-4">

    <!-- Stats -->
    <div class="row g-3 mb-4">

      <div class="col-md-3">
        <div class="card text-center p-3">
          <i class="bi bi-people fs-2 text-primary"></i>
          <h3 class="mt-2 mb-0">{{stats.total_students}}</h3>
          <p class="text-muted mb-0">Students</p>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-center p-3">
          <i class="bi bi-building fs-2 text-success"></i>
          <h3 class="mt-2 mb-0">{{stats.total_companies}}</h3>
          <p class="text-muted mb-0">Companies</p>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-center p-3">
          <i class="bi bi-briefcase fs-2 text-warning"></i>
          <h3 class="mt-2 mb-0">{{stats.total_drives}}</h3>
          <p class="text-muted mb-0">Drives</p>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card text-center p-3">
          <i class="bi bi-clock-history fs-2 text-danger"></i>
          <h3 class="mt-2 mb-0">{{stats.pending_companies}}</h3>
          <p class="text-muted mb-0">Pending</p>
        </div>
      </div>

    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4">

      <li class="nav-item">
        <button
          class="nav-link"
          :class="{active:tab==='companies'}"
          @click="tab='companies';loadCompanies()">

          <i class="bi bi-building"></i>
          Companies

          <span v-if="stats.pending_companies" class="badge bg-danger ms-1">
            {{stats.pending_companies}}
          </span>
        </button>
      </li>

      <li class="nav-item">
        <button
          class="nav-link"
          :class="{active:tab==='drives'}"
          @click="tab='drives';loadDrives()">

          <i class="bi bi-briefcase"></i>
          Drives
        </button>
      </li>

      <li class="nav-item">
        <button
          class="nav-link"
          :class="{active:tab==='students'}"
          @click="tab='students';loadStudents()">

          <i class="bi bi-person"></i>
          Students
        </button>
      </li>

    </ul>

    <!-- Alerts -->
    <div v-if="msg" class="alert alert-success">
      {{msg}}
    </div>

    <div v-if="errMsg" class="alert alert-danger">
      {{errMsg}}
    </div>


    <!-- ================= COMPANIES ================= -->
    <div v-if="tab==='companies'" class="card p-3">
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-dark">
            <tr>
              <th>Company</th>
              <th>Email</th>
              <th>HR Contact</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td><strong>{{c.company_name}}</strong></td>
              <td>{{c.email}}</td>
              <td>{{c.hr_contact}}</td>

              <td>
                <span :class="badgeClass(c.approval_status)">
                  {{c.approval_status}}
                </span>
              </td>

              <td>
                <button
                  v-if="c.approval_status==='pending'"
                  @click="approveCompany(c.id,'approve')"
                  class="btn btn-success btn-sm me-2">
                  ✔ Approve
                </button>

                <button
                  v-if="c.approval_status==='pending'"
                  @click="approveCompany(c.id,'reject')"
                  class="btn btn-danger btn-sm">
                  ✘ Reject
                </button>

                <span v-else class="text-muted">Completed</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>


    <!-- ================= DRIVES ================= -->
    <div v-if="tab==='drives'" class="card p-3">
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-dark">
            <tr>
              <th>Job</th>
              <th>Company</th>
              <th>Status</th>
              <th>Deadline</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td><strong>{{d.job_title}}</strong></td>
              <td>{{d.company}}</td>

              <td>
                <span :class="badgeClass(d.status)">
                  {{d.status}}
                </span>
              </td>

              <td>{{d.deadline?.slice(0,10)}}</td>

              <td>
                <button
                  v-if="d.status==='pending'"
                  @click="approveDrive(d.id,'approve')"
                  class="btn btn-success btn-sm me-2">
                  Approve
                </button>

                <button
                  v-if="d.status==='pending'"
                  @click="approveDrive(d.id,'reject')"
                  class="btn btn-danger btn-sm">
                  Reject
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>


    <!-- ================= STUDENTS ================= -->
    <div v-if="tab==='students'" class="card p-3">
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead class="table-dark">
            <tr>
              <th>Name</th>
              <th>Roll</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Placed</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td><strong>{{s.full_name}}</strong></td>
              <td>{{s.roll_number}}</td>
              <td>{{s.branch}}</td>
              <td>{{s.cgpa}}</td>

              <td>
                <span :class="s.is_placed?'badge bg-success':'badge bg-secondary'">
                  {{s.is_placed?'Yes':'No'}}
                </span>
              </td>

              <td>
                <span :class="badgeClass(s.status)">
                  {{s.status}}
                </span>
              </td>

              <td>
                <button
                  v-if="s.status!=='blacklisted'"
                  @click="blacklistStudent(s.id)"
                  class="btn btn-danger btn-sm">
                  Blacklist
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</div>
</template>

<style scoped>

.nav-tabs .nav-link.active {
  font-weight: 600;
}

</style>

<script>
import axios from 'axios'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      tab: 'companies',
      stats: {
        total_students: 0,
        total_companies: 0,
        total_drives: 0,
        pending_companies: 0,
        pending_drives: 0
      },
      companies: [],
      drives: [],
      students: [],
      msg: '',
      errMsg: '',
      email: localStorage.getItem('email') || 'Admin'
    }
  },

  async mounted() {
    await this.loadStats()
    await this.loadCompanies()
  },

  methods: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },

    async loadStats() {
      try {
        const res = await axios.get('http://localhost:5000/api/admin/dashboard', { headers: this.headers() })
        this.stats = res.data
      } catch (e) {
        this.errMsg = 'Stats load nahi hue: ' + (e.response?.data?.error || e.message)
      }
    },

    async loadCompanies() {
      try {
        const res = await axios.get('http://localhost:5000/api/admin/companies', { headers: this.headers() })
        this.companies = res.data
      } catch (e) {
        this.errMsg = 'Companies load nahi hui: ' + (e.response?.data?.error || e.message)
      }
    },

    async loadDrives() {
      try {
        const res = await axios.get('http://localhost:5000/api/admin/drives', { headers: this.headers() })
        this.drives = res.data
      } catch (e) {
        this.errMsg = 'Drives load nahi hue: ' + (e.response?.data?.error || e.message)
      }
    },

    async loadStudents() {
      try {
        const res = await axios.get('http://localhost:5000/api/admin/students', { headers: this.headers() })
        this.students = res.data
      } catch (e) {
        this.errMsg = 'Students load nahi hue: ' + (e.response?.data?.error || e.message)
      }
    },

    async approveCompany(id, action) {
      try {
        const res = await axios.put(
          `http://localhost:5000/api/admin/companies/${id}/approve`,
          { action },
          { headers: this.headers() }
        )
        this.msg = res.data.message
        await this.loadStats()
        await this.loadCompanies()
        setTimeout(() => this.msg = '', 3000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Error hua'
      }
    },

    async approveDrive(id, action) {
      try {
        await axios.put(
          `http://localhost:5000/api/admin/drives/${id}/approve`,
          { action },
          { headers: this.headers() }
        )
        this.msg = `Drive ${action}d successfully`
        await this.loadStats()
        await this.loadDrives()
        setTimeout(() => this.msg = '', 3000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Error hua'
      }
    },

    async blacklistStudent(id) {
      if (!confirm('Sure ho? Student blacklist ho jayega!')) return
      try {
        await axios.put(
          `http://localhost:5000/api/admin/students/${id}/blacklist`,
          {},
          { headers: this.headers() }
        )
        this.msg = 'Student blacklisted!'
        await this.loadStudents()
        setTimeout(() => this.msg = '', 3000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Error hua'
      }
    },

    badgeClass(status) {
      const map = {
        'approved'   : 'badge bg-success',
        'pending'    : 'badge bg-warning text-dark',
        'rejected'   : 'badge bg-danger',
        'blacklisted': 'badge bg-dark'
      }
      return map[status] || 'badge bg-secondary'
    },

    logout() {
      localStorage.clear()
      this.$router.replace('/login')
    }
  }
}
</script>
