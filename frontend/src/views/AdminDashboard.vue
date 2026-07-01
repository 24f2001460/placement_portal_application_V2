<template>

<div class="bg-light min-vh-100">

    <!-- Navbar -->

    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">

        <div class="container-fluid px-4">

            <span class="navbar-brand fw-bold">

                🎓 Placement Portal

            </span>

            <div class="d-flex align-items-center">

                <span class="text-muted me-3">

                    <i class="bi bi-person-circle me-1"></i>

                    {{ email }}

                </span>

                <button
                    @click="logout"
                    class="btn btn-outline-danger btn-sm">

                    Logout

                </button>

            </div>

        </div>

    </nav>



    <div class="container py-4">

        <!-- Alerts -->

        <div
            v-if="msg"
            class="alert alert-success">

            {{ msg }}

        </div>

        <div
            v-if="errMsg"
            class="alert alert-danger">

            {{ errMsg }}

        </div>



        <!-- Stats -->

        <div class="row g-4 mb-4">

            <div class="col-lg-3 col-md-6">

                <div class="card shadow-sm h-100">

                    <div class="card-body text-center">

                        <i class="bi bi-people-fill fs-1 text-primary"></i>

                        <h3 class="fw-bold mt-3">

                            {{ stats.total_students }}

                        </h3>

                        <p class="text-muted mb-0">

                            Students

                        </p>

                    </div>

                </div>

            </div>



            <div class="col-lg-3 col-md-6">

                <div class="card shadow-sm h-100">

                    <div class="card-body text-center">

                        <i class="bi bi-building fs-1 text-success"></i>

                        <h3 class="fw-bold mt-3">

                            {{ stats.total_companies }}

                        </h3>

                        <p class="text-muted mb-0">

                            Companies

                        </p>

                    </div>

                </div>

            </div>



            <div class="col-lg-3 col-md-6">

                <div class="card shadow-sm h-100">

                    <div class="card-body text-center">

                        <i class="bi bi-briefcase-fill fs-1 text-warning"></i>

                        <h3 class="fw-bold mt-3">

                            {{ stats.total_drives }}

                        </h3>

                        <p class="text-muted mb-0">

                            Drives

                        </p>

                    </div>

                </div>

            </div>



            <div class="col-lg-3 col-md-6">

                <div class="card shadow-sm h-100">

                    <div class="card-body text-center">

                        <i class="bi bi-clock-history fs-1 text-danger"></i>

                        <h3 class="fw-bold mt-3">

                            {{ stats.pending_companies }}

                        </h3>

                        <p class="text-muted mb-0">

                            Pending Companies

                        </p>

                    </div>

                </div>

            </div>

        </div>



        <!-- Tabs -->

        <ul class="nav nav-pills mb-4">

            <li class="nav-item">

                <button
                    class="nav-link"
                    :class="{active:tab==='companies'}"
                    @click="tab='companies';loadCompanies()">

                    Companies

                    <span
                        v-if="stats.pending_companies"
                        class="badge bg-danger ms-2">

                        {{ stats.pending_companies }}

                    </span>

                </button>

            </li>



            <li class="nav-item">

                <button
                    class="nav-link"
                    :class="{active:tab==='drives'}"
                    @click="tab='drives';loadDrives()">

                    Drives

                </button>

            </li>



            <li class="nav-item">

                <button
                    class="nav-link"
                    :class="{active:tab==='students'}"
                    @click="tab='students';loadStudents()">

                    Students

                </button>

            </li>

        </ul>



        <!-- Companies -->

        <div
            v-if="tab==='companies'"
            class="card shadow-sm">

            <div class="card-body">

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

                            <tr
                                v-for="c in companies"
                                :key="c.id">

                                <td>

                                    <strong>

                                        {{ c.company_name }}

                                    </strong>

                                </td>

                                <td>{{ c.email }}</td>

                                <td>{{ c.hr_contact }}</td>

                                <td>

                                    <span :class="badgeClass(c.approval_status)">

                                        {{ c.approval_status }}

                                    </span>

                                </td>

                                <td>

                                    <button
                                        v-if="c.approval_status==='pending'"
                                        class="btn btn-success btn-sm me-2"
                                        @click="approveCompany(c.id,'approve')">

                                        Approve

                                    </button>

                                    <button
                                        v-if="c.approval_status==='pending'"
                                        class="btn btn-danger btn-sm"
                                        @click="approveCompany(c.id,'reject')">

                                        Reject

                                    </button>

                                    <span
                                        v-else
                                        class="text-muted">

                                        Completed

                                    </span>

                                </td>

                            </tr>

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

        <!-- ================= DRIVES ================= -->

        <div
            v-if="tab==='drives'"
            class="card shadow-sm">

            <div class="card-body">

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

                            <tr
                                v-for="d in drives"
                                :key="d.id">

                                <td>

                                    <strong>

                                        {{ d.job_title }}

                                    </strong>

                                </td>

                                <td>

                                    {{ d.company }}

                                </td>

                                <td>

                                    <span :class="badgeClass(d.status)">

                                        {{ d.status }}

                                    </span>

                                </td>

                                <td>

                                    {{ d.deadline?.slice(0,10) }}

                                </td>

                                <td>

                                    <button
                                        v-if="d.status==='pending'"
                                        class="btn btn-success btn-sm me-2"
                                        @click="approveDrive(d.id,'approve')">

                                        Approve

                                    </button>

                                    <button
                                        v-if="d.status==='pending'"
                                        class="btn btn-danger btn-sm"
                                        @click="approveDrive(d.id,'reject')">

                                        Reject

                                    </button>

                                </td>

                            </tr>

                        </tbody>

                    </table>

                </div>

            </div>

        </div>



        <!-- ================= STUDENTS ================= -->

        <div
            v-if="tab==='students'"
            class="card shadow-sm">

            <div class="card-body">

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

                            <tr
                                v-for="s in students"
                                :key="s.id">

                                <td>

                                    <strong>

                                        {{ s.full_name }}

                                    </strong>

                                </td>

                                <td>

                                    {{ s.roll_number }}

                                </td>

                                <td>

                                    {{ s.branch }}

                                </td>

                                <td>

                                    {{ s.cgpa }}

                                </td>

                                <td>

                                    <span
                                        :class="s.is_placed ? 'badge bg-success' : 'badge bg-secondary'">

                                        {{ s.is_placed ? 'Yes' : 'No' }}

                                    </span>

                                </td>

                                <td>

                                    <span :class="badgeClass(s.status)">

                                        {{ s.status }}

                                    </span>

                                </td>

                                <td>

                                    <button
                                        v-if="s.status!=='blacklisted'"
                                        class="btn btn-outline-danger btn-sm"
                                        @click="blacklistStudent(s.id)">

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

</div>

</template>

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

      return {

        Authorization:
          `Bearer ${localStorage.getItem('token')}`

      }

    },



    async loadStats() {

      try {

        const res = await axios.get(

          'http://localhost:5000/api/admin/dashboard',

          {
            headers: this.headers()
          }

        )

        this.stats = res.data

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Unable to load dashboard statistics.'

      }

    },



    async loadCompanies() {

      try {

        const res = await axios.get(

          'http://localhost:5000/api/admin/companies',

          {
            headers: this.headers()
          }

        )

        this.companies = res.data

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Unable to load companies.'

      }

    },



    async loadDrives() {

      try {

        const res = await axios.get(

          'http://localhost:5000/api/admin/drives',

          {
            headers: this.headers()
          }

        )

        this.drives = res.data

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Unable to load drives.'

      }

    },



    async loadStudents() {

      try {

        const res = await axios.get(

          'http://localhost:5000/api/admin/students',

          {
            headers: this.headers()
          }

        )

        this.students = res.data

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Unable to load students.'

      }

    },



    async approveCompany(id, action) {

      try {

        const res = await axios.put(

          `http://localhost:5000/api/admin/companies/${id}/approve`,

          {
            action
          },

          {
            headers: this.headers()
          }

        )

        this.msg = res.data.message

        await this.loadStats()

        await this.loadCompanies()

        setTimeout(() => {

          this.msg = ''

        }, 3000)

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Operation failed.'

      }

    },



    async approveDrive(id, action) {

      try {

        await axios.put(

          `http://localhost:5000/api/admin/drives/${id}/approve`,

          {
            action
          },

          {
            headers: this.headers()
          }

        )

        this.msg =
          `Drive ${action}d successfully`

        await this.loadStats()

        await this.loadDrives()

        setTimeout(() => {

          this.msg = ''

        }, 3000)

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Operation failed.'

      }

    },



    async blacklistStudent(id) {

      if (

        !confirm(
          'Are you sure you want to blacklist this student?'
        )

      ) return

      try {

        await axios.put(

          `http://localhost:5000/api/admin/students/${id}/blacklist`,

          {},

          {
            headers: this.headers()
          }

        )

        this.msg =
          'Student blacklisted successfully.'

        await this.loadStudents()

        setTimeout(() => {

          this.msg = ''

        }, 3000)

      }

      catch (e) {

        this.errMsg =
          e.response?.data?.error ||
          'Operation failed.'

      }

    },



    badgeClass(status) {

      const map = {

        approved:
          'badge bg-success',

        pending:
          'badge bg-warning text-dark',

        rejected:
          'badge bg-danger',

        blacklisted:
          'badge bg-dark'

      }

      return map[status] ||
             'badge bg-secondary'

    },



    logout() {

      localStorage.clear()

      this.$router.replace('/login')

    }

  }

}

</script>
<style scoped>

.card{
    border-radius:12px;
}

.table th,
.table td{
    vertical-align:middle;
}

.nav-pills .nav-link{
    border-radius:8px;
}

.nav-pills .nav-link.active{
    font-weight:600;
}

</style>
