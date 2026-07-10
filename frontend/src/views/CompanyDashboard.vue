<template>
  <div class="container py-4">
    <!-- Navbar Header -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div>
        <h1 class="h3 fw-bold mb-0">🏢 {{ companyName || 'Company' }} Dashboard</h1>
        <p class="text-muted mb-0 small">Placement Drives & Applicants Portal</p>
      </div>
      <button @click="logout" class="btn btn-outline-danger btn-sm">logout</button>
    </div>

    <!-- Alert notifications -->
    <div v-if="msg" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ msg }}
      <button type="button" class="btn-close" @click="msg = ''" aria-label="Close"></button>
    </div>
    <div v-if="errMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ errMsg }}
      <button type="button" class="btn-close" @click="errMsg = ''" aria-label="Close"></button>
    </div>

    <!-- Statistics Panel -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card shadow-sm text-center border-dark">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1">Total Drives</h6>
            <h2 class="fw-bold mb-0">{{ drives.length }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm text-center border-dark text-success">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1">Approved Drives</h6>
            <h2 class="fw-bold mb-0">{{ approvedCount }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm text-center border-dark text-warning">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1">Pending Approval</h6>
            <h2 class="fw-bold mb-0">{{ pendingCount }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Control panel actions -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="h5 mb-0 fw-bold">Placement Drive Controls</h3>
      <button @click="showCreateForm = !showCreateForm" class="btn btn-dark btn-sm">
        {{ showCreateForm ? 'Close Form' : 'Create Drive Proposal' }}
      </button>
    </div>

    <!-- Create Drive Form (Toggled) -->
    <div v-if="showCreateForm" class="card border-dark shadow-sm mb-4">
      <div class="card-header bg-dark text-white py-2">
        <h5 class="card-title h6 mb-0">Submit New Drive Proposal</h5>
      </div>
      <div class="card-body p-3">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label small fw-bold">Drive Name</label>
            <input v-model="createForm.drive_name" class="form-control form-control-sm" placeholder="e.g. Campus Recruitment 2026" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold">Job Title</label>
            <input v-model="createForm.job_title" class="form-control form-control-sm" placeholder="e.g. Senior Software Developer" required />
          </div>
          <div class="col-12">
            <label class="form-label small fw-bold">Job Description</label>
            <textarea v-model="createForm.job_description" class="form-control form-control-sm" rows="3" placeholder="Describe the job role, eligibility, package, etc." required></textarea>
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-bold">Location</label>
            <input v-model="createForm.location" class="form-control form-control-sm" placeholder="e.g. Chennai, Remote" />
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-bold">Salary Range / Package</label>
            <input v-model="createForm.salary_range" class="form-control form-control-sm" placeholder="e.g. 600000" />
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-bold">Number of Openings</label>
            <input v-model="createForm.openings" type="number" class="form-control form-control-sm" />
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-bold d-block">Eligible Branches (Select none for all)</label>
            <div class="d-flex flex-wrap gap-2 pt-1">
              <div v-for="branch in ['CSE', 'ECE', 'ME', 'CE', 'EE']" :key="branch" class="form-check form-check-inline mb-0">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  :id="'branch_' + branch" 
                  :value="branch" 
                  v-model="selectedBranches"
                />
                <label class="form-check-label small" :for="'branch_' + branch">{{ branch }}</label>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-bold">Minimum CGPA required</label>
            <input v-model="createForm.min_cgpa" type="number" step="0.1" class="form-control form-control-sm" />
          </div>
          <div class="col-md-4">
            <label class="form-label small fw-bold">Max Backlogs Allowed</label>
            <input v-model="createForm.max_backlogs" type="number" class="form-control form-control-sm" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold">Application Deadline</label>
            <input v-model="createForm.application_deadline" type="datetime-local" class="form-control form-control-sm" required />
          </div>
        </div>
        <div class="text-end mt-3 border-top pt-2">
          <button @click="handleCreateDrive" class="btn btn-success btn-sm px-4">save</button>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <!-- LEFT COLUMN: Upcoming Drives -->
      <div class="col-md-7">
        <div class="card border-dark shadow-sm mb-4">
          <div class="card-header bg-dark text-white py-2">
            <h5 class="card-title h6 mb-0">Upcoming / Active Drives</h5>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover table-striped mb-0 small align-middle">
                <thead>
                  <tr>
                    <th>Sr No.</th>
                    <th>Drive Title</th>
                    <th>Applicants</th>
                    <th>Status</th>
                    <th style="width: 200px; text-align: right;">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(d, idx) in upcomingDrives" :key="d.id" :class="{'table-info': activeDriveForApps && activeDriveForApps.id === d.id}">
                    <td>{{ idx + 1001 }}.</td>
                    <td><strong class="text-dark">{{ d.job_title }}</strong></td>
                    <td><span class="badge bg-secondary">{{ d.total_applicants || 0 }}</span></td>
                    <td><span :class="badgeClass(d.status)">{{ d.status }}</span></td>
                    <td style="text-align: right;">
                      <button @click="selectDriveForApplications(d)" class="btn btn-outline-primary btn-xs py-0 px-2 me-1" style="font-size: 11px;">view details</button>
                      <button 
                        v-if="d.status === 'approved'"
                        @click="markDriveCompleted(d.id)" 
                        class="btn btn-outline-success btn-xs py-0 px-1" 
                        style="font-size: 11px;"
                      >
                        mark as complete
                      </button>
                    </td>
                  </tr>
                  <tr v-if="upcomingDrives.length === 0">
                    <td colspan="5" class="text-center text-muted p-3">No upcoming drives proposed yet</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: Closed Drives -->
      <div class="col-md-5">
        <div class="card border-dark shadow-sm mb-4">
          <div class="card-header bg-dark text-white py-2">
            <h5 class="card-title h6 mb-0">Closed Drives History</h5>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover table-striped mb-0 small align-middle">
                <thead>
                  <tr>
                    <th>Sr No.</th>
                    <th>Drive Title</th>
                    <th>Applicants</th>
                    <th style="width: 100px; text-align: right;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(d, idx) in closedDrives" :key="d.id" :class="{'table-info': activeDriveForApps && activeDriveForApps.id === d.id}">
                    <td>{{ idx + 1011 }}.</td>
                    <td>{{ d.job_title }}</td>
                    <td><span class="badge bg-secondary">{{ d.total_applicants || 0 }}</span></td>
                    <td style="text-align: right;">
                      <button @click="selectDriveForApplications(d)" class="btn btn-outline-secondary btn-xs py-0 px-2" style="font-size: 11px;">update</button>
                    </td>
                  </tr>
                  <tr v-if="closedDrives.length === 0">
                    <td colspan="4" class="text-center text-muted p-3">No closed drives found</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- UPDATE APPLICATIONS FOR THE SELECTED DRIVE -->
    <div v-if="activeDriveForApps" class="card border-dark shadow-sm mt-2 mb-4">
      <div class="card-header bg-dark text-white py-2 d-flex justify-content-between align-items-center">
        <h3 class="card-title h6 mb-0">Update Applications for: {{ activeDriveForApps.job_title }}</h3>
        <button @click="activeDriveForApps = null; applications = []" class="btn btn-close btn-close-white btn-xs" style="font-size: 11px;"></button>
      </div>
      <div class="card-body p-3">
        <!-- Drive Spec Details Box -->
        <div class="row g-2 mb-3 bg-light p-2 border rounded small">
          <div class="col-sm-4"><strong>Salary package:</strong> {{ activeDriveForApps.salary_range || 'N/A' }}</div>
          <div class="col-sm-4"><strong>Job Type:</strong> {{ activeDriveForApps.job_type }}</div>
          <div class="col-sm-4"><strong>Location:</strong> {{ activeDriveForApps.location || 'N/A' }}</div>
          <div class="col-12 mt-1"><strong>Eligibility details:</strong> CGPA &ge; {{ activeDriveForApps.min_cgpa }}, max backlogs &le; {{ activeDriveForApps.max_backlogs }}, branches: {{ activeDriveForApps.eligible_branches || 'All' }}</div>
        </div>

        <h5 class="h6 fw-bold border-bottom pb-1 mb-2">Received Applications</h5>
        <div class="table-responsive">
          <table class="table table-hover table-striped small align-middle">
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Status</th>
                <th style="width: 150px; text-align: right;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.application_id">
                <td><strong>{{ app.student_name }}</strong></td>
                <td>{{ app.branch }}</td>
                <td>{{ app.cgpa }}</td>
                <td><span :class="badgeClass(app.status)">{{ app.status }}</span></td>
                <td style="text-align: right;">
                  <button @click="reviewApplication(app)" class="btn btn-outline-primary btn-xs py-0 px-2" style="font-size: 11px;">review application</button>
                </td>
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="5" class="text-center text-muted p-3">No student applications received for this drive</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="text-end mt-3 border-top pt-2">
          <button @click="activeDriveForApps = null; applications = []" class="btn btn-success btn-sm px-4">save</button>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- STUDENT APPLICATION REVIEW MODAL OVERLAY -->
    <!-- ========================================================================= -->
    <div v-if="reviewingApp" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded shadow-lg">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">📝 Review Student Application</h5>
            <button type="button" class="btn-close btn-close-white" @click="reviewingApp = null"></button>
          </div>
          <div class="modal-body small">
            <h4 class="fw-bold border-bottom pb-2 mb-3">{{ reviewingApp.student_name }}</h4>
            <div class="row g-2 mb-3">
              <div class="col-6"><strong>Branch / Dept:</strong> {{ reviewingApp.branch }}</div>
              <div class="col-6"><strong>Roll Number:</strong> {{ reviewingApp.roll_number }}</div>
              <div class="col-6"><strong>Current CGPA:</strong> {{ reviewingApp.cgpa }}</div>
              <div class="col-6"><strong>Active Backlogs:</strong> {{ reviewingApp.backlogs || 0 }}</div>
              <div class="col-6"><strong>Phone:</strong> {{ reviewingApp.phone || 'N/A' }}</div>
              <div class="col-6"><strong>Applied Date:</strong> {{ reviewingApp.applied_at ? reviewingApp.applied_at.slice(0, 10) : '' }}</div>
              <div class="col-12"><strong>Skills:</strong> {{ reviewingApp.skills || 'None listed' }}</div>
              <div class="col-6"><strong>LinkedIn:</strong> <a v-if="reviewingApp.linkedin_url" :href="reviewingApp.linkedin_url" target="_blank" class="text-primary text-decoration-underline">{{ reviewingApp.linkedin_url }}</a><span v-else>N/A</span></div>
              <div class="col-6"><strong>GitHub:</strong> <a v-if="reviewingApp.github_url" :href="reviewingApp.github_url" target="_blank" class="text-primary text-decoration-underline">{{ reviewingApp.github_url }}</a><span v-else>N/A</span></div>
            </div>

            <strong>Bio:</strong>
            <div class="border rounded p-2 bg-light mb-3" style="max-height: 80px; overflow-y: auto; font-family: monospace;">
              {{ reviewingApp.bio || 'No bio provided.' }}
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold mb-1">Update Selection Status</label>
              <select v-model="selectionStatus" class="form-select form-select-sm mb-2">
                <option value="shortlisted">Shortlist</option>
                <option value="selected">Select (Placed)</option>
                <option value="rejected">Reject</option>
              </select>
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold mb-1">HR Selection Remarks</label>
              <textarea v-model="remarksText" class="form-control form-control-sm" rows="2" placeholder="e.g. Good performance in technical round."></textarea>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top">
              <button @click="viewResume(reviewingApp.application_id)" class="btn btn-outline-success btn-sm">view resume</button>
              <div>
                <button @click="saveSelectionStatus" class="btn btn-success btn-sm me-2">Save Selection</button>
                <button @click="reviewingApp = null" class="btn btn-secondary btn-sm">back</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      companyName: '',
      drives: [],
      msg: '',
      errMsg: '',
      showCreateForm: false,
      createForm: {
        drive_name: '',
        job_title: '',
        job_description: '',
        location: '',
        salary_range: '',
        openings: 1,
        eligible_branches: '',
        min_cgpa: 0,
        max_backlogs: 0,
        application_deadline: ''
      },
      activeDriveForApps: null,
      applications: [],
      reviewingApp: null,
      selectionStatus: '',
      remarksText: '',
      selectedBranches: []
    }
  },
  computed: {
    upcomingDrives() {
      return this.drives.filter(d => d.status === 'approved' || d.status === 'pending')
    },
    closedDrives() {
      return this.drives.filter(d => d.status === 'completed')
    },
    totalDrives() { return this.drives.length },
    approvedCount() { return this.drives.filter(d => d.status === 'approved').length },
    pendingCount() { return this.drives.filter(d => d.status === 'pending').length }
  },
  async mounted() {
    await this.loadDashboard()
    await this.loadDrives()
  },
  methods: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },
    async loadDashboard() {
      try {
        const res = await axios.get('http://127.0.0.1:5000/api/company/dashboard', { headers: this.headers() })
        this.companyName = res.data.company_name
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load company details'
      }
    },
    async loadDrives() {
      try {
        const res = await axios.get('http://127.0.0.1:5000/api/company/drives', { headers: this.headers() })
        this.drives = res.data
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load drives'
      }
    },
    async handleCreateDrive() {
      this.errMsg = ''
      this.msg = ''
      try {
        const payload = { ...this.createForm }
        payload.eligible_branches = this.selectedBranches.join(', ')
        if (!payload.job_title || !payload.job_description || !payload.application_deadline) {
          this.errMsg = 'Please fill out job title, description and application deadline!'
          return
        }
        payload.application_deadline = new Date(payload.application_deadline).toISOString().slice(0, 16)
        
        const res = await axios.post('http://127.0.0.1:5000/api/company/drives', payload, { headers: this.headers() })
        this.msg = res.data.message
        this.showCreateForm = false
        this.selectedBranches = []
        this.createForm = {
          drive_name: '',
          job_title: '',
          job_description: '',
          location: '',
          salary_range: '',
          openings: 1,
          eligible_branches: '',
          min_cgpa: 0,
          max_backlogs: 0,
          application_deadline: ''
        }
        await this.loadDrives()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to create drive'
      }
    },
    async markDriveCompleted(id) {
      try {
        const res = await axios.put(`http://127.0.0.1:5000/api/company/drives/${id}/complete`, {}, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadDrives()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Action failed'
      }
    },
    async selectDriveForApplications(drive) {
      this.activeDriveForApps = drive
      this.reviewingApp = null
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/company/drives/${drive.id}/applications`, { headers: this.headers() })
        this.applications = res.data
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load applications'
      }
    },
    reviewApplication(app) {
      this.reviewingApp = app
      this.selectionStatus = app.status
      this.remarksText = app.remarks || ''
    },
    async saveSelectionStatus() {
      if (!this.selectionStatus) return
      try {
        const res = await axios.put(
          `http://127.0.0.1:5000/api/company/applications/${this.reviewingApp.application_id}/status`, 
          { status: this.selectionStatus, remarks: this.remarksText }, 
          { headers: this.headers() }
        )
        this.msg = res.data.message
        this.reviewingApp = null
        await this.selectDriveForApplications(this.activeDriveForApps)
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        alert(e.response?.data?.error || 'Failed to update selection status')
      }
    },
    viewResume(appId) {
      const appObj = this.applications.find(a => a.application_id === appId)
      if (!appObj || !appObj.student_id) {
        alert('Student details not found for resume.')
        return
      }
      const studentId = appObj.student_id
      axios({
        url: `http://localhost:5000/api/student/profile/resume/view/${studentId}`,
        method: 'GET',
        headers: this.headers(),
        responseType: 'blob'
      }).then((response) => {
        const fileURL = window.URL.createObjectURL(new Blob([response.data]))
        const fileLink = document.createElement('a')
        fileLink.href = fileURL
        fileLink.setAttribute('download', `resume_student_${studentId}.pdf`)
        document.body.appendChild(fileLink)
        fileLink.click()
        document.body.removeChild(fileLink)
      }).catch(() => {
        alert('Resume file not found or couldn\'t be loaded.')
      })
    },
    logout() {
      localStorage.clear()
      this.$router.push('/login')
    },
    badgeClass(status) {
      const map = {
        'approved': 'badge bg-success',
        'pending': 'badge bg-warning text-dark',
        'completed': 'badge bg-secondary',
        'rejected': 'badge bg-danger',
        'shortlisted': 'badge bg-info',
        'selected': 'badge bg-success',
        'applied': 'badge bg-secondary'
      }
      return map[status] || 'badge bg-secondary'
    }
  }
}
</script>
