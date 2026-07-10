<template>
  <div class="container py-4">
    <!-- Student Header -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div>
        <h1 class="h3 fw-bold mb-0">🎓 Student Dashboard</h1>
        <p class="text-muted mb-0 small">Welcome, {{ profile.full_name || 'Student' }} | Roll No: {{ profile.roll_number || 'N/A' }} | Branch: {{ profile.branch || 'N/A' }}</p>
      </div>
      <div class="d-flex align-items-center gap-2 small">
        <button @click="tab = 'profile'" class="btn btn-outline-primary btn-sm">Edit Profile</button>
        <button @click="showHistory" class="btn btn-outline-dark btn-sm">History Log</button>
        <button @click="logout" class="btn btn-outline-danger btn-sm">logout</button>
      </div>
    </div>

    <!-- Notifications Section -->
    <div v-if="notifications.length > 0" class="mb-4">
      <div v-for="n in unreadNotifications" :key="n.id" class="alert alert-warning py-2 px-3 mb-2 d-flex justify-content-between align-items-center small shadow-sm border-warning">
        <span>⚠️ <strong>{{ n.title }}</strong>: {{ n.message }}</span>
        <div>
          <button v-if="n.link" @click="handleNotifAction(n)" class="btn btn-dark btn-xs py-0 px-2 me-2" style="font-size: 11px;">Download</button>
          <button @click="markNotifRead(n.id)" class="btn btn-outline-secondary btn-xs py-0 px-1" style="font-size: 11px;">Dismiss</button>
        </div>
      </div>
    </div>

    <!-- Alert Messaging -->
    <div v-if="msg" class="alert alert-success alert-dismissible fade show" role="alert">
      {{ msg }}
      <button type="button" class="btn-close" @click="msg = ''" aria-label="Close"></button>
    </div>
    <div v-if="errMsg" class="alert alert-danger alert-dismissible fade show" role="alert">
      {{ errMsg }}
      <button type="button" class="btn-close" @click="errMsg = ''" aria-label="Close"></button>
    </div>

    <!-- Stats Summary Cards -->
    <div class="row g-3 mb-4" v-if="tab !== 'profile' && !showHistoryActive">
      <div class="col-md-4">
        <div class="card shadow-sm text-center border-dark">
          <div class="card-body py-2">
            <h6 class="text-muted small text-uppercase mb-0">Academic CGPA</h6>
            <h3 class="fw-bold mb-0 text-primary">{{ profile.cgpa }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm text-center border-dark">
          <div class="card-body py-2">
            <h6 class="text-muted small text-uppercase mb-0">Total Applications</h6>
            <h3 class="fw-bold mb-0">{{ profile.total_applications }}</h3>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card shadow-sm text-center border-dark">
          <div class="card-body py-2">
            <h6 class="text-muted small text-uppercase mb-0">Placement Status</h6>
            <h3 class="fw-bold mb-0" :class="profile.is_placed ? 'text-success' : 'text-secondary'">
              {{ profile.is_placed ? 'Placed' : 'Not Placed' }}
            </h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Control Tabs -->
    <div class="mb-4 border-bottom pb-2 d-flex justify-content-between align-items-center" v-if="tab !== 'profile' && !showHistoryActive">
      <div class="d-flex gap-2">
        <button @click="tab = 'drives'; activeCompany = null; selectedDrive = null" class="btn btn-sm" :class="tab === 'drives' ? 'btn-dark' : 'btn-outline-dark'">Drives & Companies</button>
        <button @click="tab = 'applications'; activeCompany = null; selectedDrive = null" class="btn btn-sm" :class="tab === 'applications' ? 'btn-dark' : 'btn-outline-dark'">My Applied Drives</button>
      </div>

      <!-- Search Filters -->
      <div v-if="tab === 'drives'" class="d-flex align-items-center gap-3">
        <div class="form-check form-switch mb-0">
          <input class="form-check-input" type="checkbox" id="eligibleCheck" v-model="eligibleOnly" @change="loadDrives">
          <label class="form-check-label small fw-bold" for="eligibleCheck">Eligible Only</label>
        </div>
        <div class="d-flex gap-1">
          <input v-model="searchQuery" class="form-control form-control-sm" placeholder="Search job title..." @keyup.enter="loadDrives" style="width: 180px;" />
          <button @click="loadDrives" class="btn btn-dark btn-sm">Search</button>
          <button @click="resetSearch" class="btn btn-outline-secondary btn-sm">Reset</button>
        </div>
      </div>
    </div>

    <!-- ================= APPLIED DRIVES TAB ================= -->
    <div v-if="tab === 'applications' && !showHistoryActive">
      <div class="card border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">My Applications</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th style="width: 80px;">Sr No.</th>
                  <th>Drive Name</th>
                  <th>Company</th>
                  <th>Applied Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(app, idx) in appliedDrives" :key="app.application_id">
                  <td>{{ idx + 1 }}.</td>
                  <td><strong>{{ app.job_title }}</strong></td>
                  <td>{{ app.company }}</td>
                  <td>{{ app.applied_at ? app.applied_at.slice(0, 10) : '' }}</td>
                  <td><span :class="badgeClass(app.status)">{{ app.status }}</span></td>
                </tr>
                <tr v-if="appliedDrives.length === 0">
                  <td colspan="5" class="text-center text-muted p-3">You have not applied for any placement drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= DRIVES & COMPANIES LISTS GRID ================= -->
    <div v-if="tab === 'drives' && !activeCompany && !selectedDrive && !showHistoryActive">
      <div class="row g-4">
        <!-- Organizations / Companies List -->
        <div class="col-md-5">
          <div class="card border-dark shadow-sm h-100">
            <div class="card-header bg-dark text-white py-2 d-flex justify-content-between align-items-center">
              <h5 class="card-title h6 mb-0">Organizations Overview</h5>
              <div class="d-flex gap-1 align-items-center">
                <input v-model="companySearchQuery" class="form-control form-control-xs py-0 px-1 text-dark" placeholder="Search..." @keyup.enter="loadCompanies" style="width: 100px; font-size: 11px; height: 22px; background: white;" />
                <button @click="loadCompanies" class="btn btn-light btn-xs py-0 px-2" style="font-size: 11px; height: 22px;">Go</button>
              </div>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 450px;">
                <table class="table table-hover table-striped mb-0 small align-middle">
                  <thead>
                    <tr>
                      <th>Company</th>
                      <th style="width: 100px; text-align: right;">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="c in companies" :key="c.id">
                      <td><strong>{{ c.company_name }}</strong></td>
                      <td style="text-align: right;">
                        <button @click="viewCompany(c)" class="btn btn-outline-primary btn-xs py-0 px-2" style="font-size: 11px;">view details</button>
                      </td>
                    </tr>
                    <tr v-if="companies.length === 0">
                      <td colspan="2" class="text-center text-muted p-3">No active organizations registered</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Drives List -->
        <div class="col-md-7">
          <div class="card border-dark shadow-sm h-100">
            <div class="card-header bg-dark text-white py-2">
              <h5 class="card-title h6 mb-0">Approved Placement Opportunities</h5>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive" style="max-height: 450px;">
                <table class="table table-hover table-striped mb-0 small align-middle">
                  <thead>
                    <tr>
                      <th>Opportunity</th>
                      <th>Company</th>
                      <th>CGPA</th>
                      <th style="width: 100px; text-align: right;">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="d in drives" :key="d.id">
                      <td><strong>{{ d.job_title }}</strong></td>
                      <td>{{ d.company }}</td>
                      <td>&ge; {{ d.min_cgpa }}</td>
                      <td style="text-align: right;">
                        <button @click="viewDrive(d)" class="btn btn-outline-primary btn-xs py-0 px-2" style="font-size: 11px;">view details</button>
                      </td>
                    </tr>
                    <tr v-if="drives.length === 0">
                      <td colspan="4" class="text-center text-muted p-3">No active approved drives matching search</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= EDIT PROFILE FORM TAB ================= -->
    <div v-if="tab === 'profile' && !showHistoryActive" class="card border-dark shadow-sm">
      <div class="card-header bg-dark text-white py-2">
        <h5 class="card-title h6 mb-0">Modify Student Profile</h5>
      </div>
      <div class="card-body p-3">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label small fw-bold">Full Name</label>
            <input v-model="editProfile.full_name" class="form-control form-control-sm" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold">Phone Number</label>
            <input v-model="editProfile.phone" class="form-control form-control-sm" />
          </div>
          <div class="col-12">
            <label class="form-label small fw-bold">Skills Keywords</label>
            <input v-model="editProfile.skills" class="form-control form-control-sm" placeholder="e.g. Python, Java, JavaScript, Vue, HTML/CSS" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold">LinkedIn URL</label>
            <input v-model="editProfile.linkedin_url" class="form-control form-control-sm" />
          </div>
          <div class="col-md-6">
            <label class="form-label small fw-bold">GitHub URL</label>
            <input v-model="editProfile.github_url" class="form-control form-control-sm" />
          </div>
          <div class="col-12">
            <label class="form-label small fw-bold">Professional Bio / About Me</label>
            <textarea v-model="editProfile.bio" class="form-control form-control-sm" rows="3"></textarea>
          </div>
        </div>

        <!-- Resume File Management -->
        <div class="border rounded p-3 mt-4 mb-3 bg-light">
          <label class="form-label small fw-bold d-block mb-1">Resume Document (PDF or DOCX)</label>
          <div class="d-flex align-items-center gap-3">
            <input type="file" ref="resumeFile" @change="handleResumeChange" class="form-control form-control-sm" style="max-width: 350px;" />
            <button @click="uploadResume" class="btn btn-outline-dark btn-sm">Upload File</button>
          </div>
          <p v-if="profile.resume_filename" class="text-success small mt-2 mb-0">
            ✔ Active Uploaded Document: <strong>{{ profile.resume_filename }}</strong>
          </p>
        </div>

        <div class="text-end border-top pt-2">
          <button @click="updateProfile" class="btn btn-success btn-sm px-4 me-2">Save Profile</button>
          <button @click="tab = 'drives'" class="btn btn-secondary btn-sm">Cancel</button>
        </div>
      </div>
    </div>

    <!-- ================= HISTORY SCREEN / MODAL OVERLAY ================= -->
    <div v-if="showHistoryActive" class="card border-dark shadow-sm">
      <div class="card-header bg-dark text-white py-2 d-flex justify-content-between align-items-center">
        <h5 class="card-title h6 mb-0">Placement Application History Log</h5>
        <button @click="showHistoryActive = false; tab = 'drives'" class="btn btn-close btn-close-white btn-xs" style="font-size: 11px;"></button>
      </div>
      <div class="card-body p-3">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <p class="mb-1 small"><strong>Student Name:</strong> {{ profile.full_name }}</p>
            <p class="mb-0 small"><strong>Roll Number / Branch:</strong> {{ profile.roll_number }} / {{ profile.branch }}</p>
          </div>
          <button @click="exportCSV" class="btn btn-outline-success btn-sm">Export Applications CSV</button>
        </div>

        <div v-if="exportMsg" class="alert alert-info py-2 px-3 small border-info">
          {{ exportMsg }}
        </div>

        <div class="table-responsive">
          <table class="table table-hover table-striped mb-0 small align-middle">
            <thead>
              <tr>
                <th style="width: 80px;">Drive No.</th>
                <th>Job Title / Company</th>
                <th>Applied On</th>
                <th>Remarks</th>
                <th>Selection Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(app, idx) in appliedDrives" :key="app.application_id">
                <td>{{ idx + 1 }}.</td>
                <td><strong>{{ app.job_title }}</strong> at {{ app.company }}</td>
                <td>{{ app.applied_at ? app.applied_at.slice(0, 10) : '' }}</td>
                <td>{{ app.remarks || 'No remarks recorded' }}</td>
                <td><span :class="badgeClass(app.status)">{{ app.status }}</span></td>
              </tr>
              <tr v-if="appliedDrives.length === 0">
                <td colspan="5" class="text-center text-muted p-3">No placement drive history found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- STUDENT INTERACTIVE DETAILS MODAL OVERLAYS -->
    <!-- ========================================================================= -->

    <!-- COMPANY DETAILS MODAL -->
    <div v-if="activeCompany" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded shadow-lg">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">🏢 {{ activeCompany.company_name }} profile overview</h5>
            <button type="button" class="btn-close btn-close-white" @click="activeCompany = null"></button>
          </div>
          <div class="modal-body small">
            <h4 class="fw-bold border-bottom pb-2 mb-3">{{ activeCompany.company_name }}</h4>
            <div class="row g-2 mb-3">
              <div class="col-6"><strong>Industry:</strong> {{ activeCompany.industry || 'Tech' }}</div>
              <div class="col-6"><strong>Website:</strong> <a :href="activeCompany.website" target="_blank" class="text-decoration-underline">{{ activeCompany.website || 'N/A' }}</a></div>
              <div class="col-12"><strong>Headquarters:</strong> {{ activeCompany.headquarters || 'N/A' }}</div>
            </div>

            <strong>Overview:</strong>
            <div class="border rounded p-2 bg-light mb-3" style="max-height: 120px; overflow-y: auto;">
              {{ activeCompany.description || 'No overview description provided.' }}
            </div>

            <h5 class="h6 fw-bold border-bottom pb-1 mb-2">Available Jobs</h5>
            <div class="table-responsive">
              <table class="table table-hover table-striped mb-0 align-middle">
                <thead>
                  <tr>
                    <th>Job Title</th>
                    <th>Salary</th>
                    <th style="width: 80px; text-align: right;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="d in activeCompany.drives" :key="d.id">
                    <td>{{ d.job_title }}</td>
                    <td>{{ d.salary_range || 'N/A' }}</td>
                    <td style="text-align: right;">
                      <button @click="viewDrive(d)" class="btn btn-outline-primary btn-xs py-0 px-2" style="font-size: 11px;">view</button>
                    </td>
                  </tr>
                  <tr v-if="!activeCompany.drives || activeCompany.drives.length === 0">
                    <td colspan="3" class="text-center text-muted p-2">No active drives posted.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="modal-footer py-1">
            <button type="button" class="btn btn-secondary btn-sm" @click="activeCompany = null">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- DRIVE DETAILS & APPLY MODAL -->
    <div v-if="selectedDrive" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded shadow-lg">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">💼 Opportunity Details</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeDriveDetails"></button>
          </div>
          <div class="modal-body small">
            <h4 class="fw-bold border-bottom pb-2 mb-3">{{ selectedDrive.job_title }}</h4>
            <div class="row g-2 mb-3">
              <div class="col-6"><strong>Company:</strong> {{ selectedDrive.company }}</div>
              <div class="col-6"><strong>Location:</strong> {{ selectedDrive.location || 'N/A' }}</div>
              <div class="col-6"><strong>Salary Package:</strong> {{ selectedDrive.salary_range || 'N/A' }}</div>
              <div class="col-6"><strong>Required CGPA:</strong> &ge; {{ selectedDrive.min_cgpa }}</div>
              <div class="col-12"><strong>Eligible Branches:</strong> {{ selectedDrive.eligible_branches || 'All' }}</div>
              <div class="col-12"><strong>Deadline:</strong> {{ selectedDrive.deadline ? selectedDrive.deadline.slice(0, 16).replace('T', ' ') : 'N/A' }}</div>
            </div>

            <strong>Description:</strong>
            <div class="border rounded p-2 bg-light mb-3" style="max-height: 120px; overflow-y: auto; font-family: monospace;">
              {{ selectedDrive.job_description || 'No description provided.' }}
            </div>

            <!-- Eligibility Banner -->
            <div v-if="!selectedDrive.already_applied" class="border-top pt-3">
              <div v-if="!selectedDrive.is_eligible" class="alert alert-danger py-2 px-3 border-danger mb-0">
                ❌ <strong>Not Eligible:</strong> {{ selectedDrive.eligibility_reason }}
              </div>
              <div v-else>
                <div class="mb-2">
                  <label class="form-label fw-bold mb-1">Cover Letter / Notes for Application</label>
                  <textarea v-model="coverLetter" class="form-control form-control-sm" rows="3" placeholder="Briefly state your suitability for this role..."></textarea>
                </div>
                <div class="text-end">
                  <button @click="applyDrive(selectedDrive.id)" class="btn btn-success btn-sm px-4">Apply</button>
                </div>
              </div>
            </div>
            <div v-else class="text-center p-2 border rounded border-secondary bg-light text-muted fw-bold">
              ✔ You have already applied for this opportunity
            </div>
          </div>
          <div class="modal-footer py-1">
            <button type="button" class="btn btn-secondary btn-sm" @click="closeDriveDetails">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      tab: 'drives',
      searchQuery: '',
      eligibleOnly: false,
      msg: '',
      errMsg: '',
      exportMsg: '',
      profile: {},
      editProfile: {
        full_name: '',
        phone: '',
        skills: '',
        linkedin_url: '',
        github_url: '',
        bio: ''
      },
      companies: [],
      companySearchQuery: '',
      drives: [],
      appliedDrives: [],
      activeCompany: null,
      selectedDrive: null,
      coverLetter: '',
      resumeFileSelected: null,
      notifications: [],
      showHistoryActive: false
    }
  },
  computed: {
    unreadNotifications() {
      return this.notifications.filter(n => !n.is_read)
    }
  },
  async mounted() {
    await this.loadProfile()
    await this.loadCompanies()
    await this.loadDrives()
    await this.loadApplications()
    await this.loadNotifications()
  },
  methods: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },
    async loadProfile() {
      try {
        const res = await axios.get('http://localhost:5000/api/student/dashboard', { headers: this.headers() })
        this.profile = res.data
        this.editProfile = {
          full_name: res.data.full_name || '',
          phone: res.data.phone || '',
          skills: res.data.skills || '',
          linkedin_url: res.data.linkedin_url || '',
          github_url: res.data.github_url || '',
          bio: res.data.bio || ''
        }
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load profile details'
      }
    },
    async loadCompanies() {
      try {
        const res = await axios.get(`http://localhost:5000/api/student/companies?search=${this.companySearchQuery}`, { headers: this.headers() })
        this.companies = res.data
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load companies'
      }
    },
    async loadDrives() {
      try {
        const eligibleParam = this.eligibleOnly ? '&eligible_only=true' : ''
        const res = await axios.get(`http://localhost:5000/api/student/drives?search=${this.searchQuery}${eligibleParam}`, { headers: this.headers() })
        this.drives = res.data
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load drives'
      }
    },
    async loadApplications() {
      try {
        const res = await axios.get('http://localhost:5000/api/student/applications', { headers: this.headers() })
        this.appliedDrives = res.data
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to load applied drives'
      }
    },
    async loadNotifications() {
      try {
        const res = await axios.get('http://localhost:5000/api/student/notifications', { headers: this.headers() })
        this.notifications = res.data
      } catch (e) {
        console.log('Failed to fetch notifications:', e.message)
      }
    },
    async markNotifRead(id) {
      try {
        await axios.put(`http://localhost:5000/api/student/notifications/${id}/read`, {}, { headers: this.headers() })
        await this.loadNotifications()
      } catch (e) {
        console.log('Notification read error:', e.message)
      }
    },
    handleNotifAction(n) {
      this.markNotifRead(n.id)
      if (n.link) {
        axios({
          url: `http://localhost:5000${n.link}`,
          method: 'GET',
          headers: this.headers(),
          responseType: 'blob'
        }).then((response) => {
          const fileURL = window.URL.createObjectURL(new Blob([response.data]))
          const fileLink = document.createElement('a')
          fileLink.href = fileURL
          fileLink.setAttribute('download', `exported_history_${this.profile.id}.csv`)
          document.body.appendChild(fileLink)
          fileLink.click()
          document.body.removeChild(fileLink)
        }).catch(() => {
          alert('Failed to download exported CSV.')
        })
      }
    },
    resetSearch() {
      this.searchQuery = ''
      this.eligibleOnly = false
      this.companySearchQuery = ''
      this.loadDrives()
      this.loadCompanies()
    },
    viewCompany(company) {
      this.activeCompany = company
      this.selectedDrive = null
      this.showHistoryActive = false
    },
    async viewDrive(drive) {
      // Find full drive details from general list
      // Since our general list get_drives has the eligible reasons, etc., let's match
      const matchingDrive = this.drives.find(d => d.id === drive.id)
      if (matchingDrive) {
        this.selectedDrive = matchingDrive
      } else {
        this.selectedDrive = drive
      }
      this.activeCompany = null
      this.showHistoryActive = false
    },
    closeDriveDetails() {
      this.selectedDrive = null
    },
    async applyDrive(id) {
      this.errMsg = ''
      this.msg = ''
      try {
        const res = await axios.post(
          `http://localhost:5000/api/student/drives/${id}/apply`, 
          { cover_letter: this.coverLetter }, 
          { headers: this.headers() }
        )
        this.msg = res.data.message
        this.selectedDrive = null
        this.coverLetter = ''
        await this.loadDrives()
        await this.loadApplications()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to apply'
      }
    },
    async updateProfile() {
      this.errMsg = ''
      this.msg = ''
      try {
        const res = await axios.put('http://localhost:5000/api/student/profile', this.editProfile, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadProfile()
        setTimeout(() => {
          this.msg = ''
          this.tab = 'drives'
        }, 2000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to save profile'
      }
    },
    handleResumeChange(event) {
      this.resumeFileSelected = event.target.files[0]
    },
    async uploadResume() {
      if (!this.resumeFileSelected) {
        alert('Please select a file first!')
        return
      }
      this.errMsg = ''
      this.msg = ''
      try {
        const formData = new FormData()
        formData.append('resume', this.resumeFileSelected)
        const res = await axios.post('http://localhost:5000/api/student/profile/resume', formData, {
          headers: {
            ...this.headers(),
            'Content-Type': 'multipart/form-data'
          }
        })
        this.msg = res.data.message
        await this.loadProfile()
        this.resumeFileSelected = null
        this.$refs.resumeFile.value = ''
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Failed to upload resume'
      }
    },
    showHistory() {
      this.showHistoryActive = true
      this.activeCompany = null
      this.selectedDrive = null
      this.tab = ''
      this.loadApplications()
    },
    async exportCSV() {
      this.exportMsg = ''
      try {
        const res = await axios.post('http://localhost:5000/api/student/applications/export', {}, { headers: this.headers() })
        this.exportMsg = res.data.message + " You will receive a notification alert and email once the export finishes."
        const pollInterval = setInterval(async () => {
          await this.loadNotifications()
          const finished = this.notifications.some(n => n.title === 'Applications Export Ready' && !n.is_read)
          if (finished) {
            clearInterval(pollInterval)
          }
        }, 3000)
        setTimeout(() => clearInterval(pollInterval), 60000)
      } catch (e) {
        this.exportMsg = 'CSV Export failed. Please try again.'
      }
    },
    logout() {
      localStorage.clear()
      this.$router.replace('/login')
    },
    badgeClass(status) {
      const map = {
        'selected': 'badge bg-success',
        'shortlisted': 'badge bg-info',
        'applied': 'badge bg-warning text-dark',
        'rejected': 'badge bg-danger'
      }
      return map[status] || 'badge bg-secondary'
    }
  }
}
</script>
