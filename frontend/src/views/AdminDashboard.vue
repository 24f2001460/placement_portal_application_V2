<template>
  <div class="container py-4">
    <!-- Navbar Header -->
    <div class="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
      <div>
        <h1 class="h3 fw-bold mb-0">🎓 Admin Control Panel</h1>
        <p class="text-muted mb-0 small">Secure Institution Placement Management Portal</p>
      </div>
      <div class="d-flex align-items-center gap-3">
        <span class="badge bg-dark p-2">{{ email }}</span>
        <button @click="logout" class="btn btn-outline-danger btn-sm">logout</button>
      </div>
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

    <!-- Stats summary cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card shadow-sm text-center border-dark bg-light">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1 fw-bold">Total Students</h6>
            <h2 class="fw-bold mb-0 text-primary">{{ students.length }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm text-center border-dark bg-light">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1 fw-bold">Total Companies</h6>
            <h2 class="fw-bold mb-0 text-success">{{ companies.length }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm text-center border-dark bg-light">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1 fw-bold">Active Drives</h6>
            <h2 class="fw-bold mb-0 text-info">{{ activeDrives.length }}</h2>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card shadow-sm text-center border-dark bg-light">
          <div class="card-body py-3">
            <h6 class="text-muted small text-uppercase mb-1 fw-bold">Pending Requests</h6>
            <h2 class="fw-bold mb-0 text-danger">{{ pendingCompanies.length + pendingDrives.length }}</h2>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Card -->
    <div class="card mb-4 border-dark">
      <div class="card-body p-3">
        <div class="d-flex gap-2">
          <input 
            v-model="searchQuery" 
            class="form-control" 
            placeholder="Search student, roll number, organization name, job title..." 
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="btn btn-dark px-4">Search</button>
          <button v-if="searchActive" @click="resetSearch" class="btn btn-outline-secondary">Reset</button>
        </div>
      </div>
    </div>

    <!-- Category Tabs Navigation -->
    <ul class="nav nav-tabs mb-4 border-bottom border-dark" id="adminTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link fw-bold" 
          :class="{ active: currentTab === 'companies' }" 
          @click="currentTab = 'companies'"
          type="button"
        >
          🏢 Companies 
          <span v-if="pendingCompanies.length > 0" class="badge bg-danger ms-1">{{ pendingCompanies.length }}</span>
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link fw-bold" 
          :class="{ active: currentTab === 'students' }" 
          @click="currentTab = 'students'"
          type="button"
        >
          🎓 Students
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link fw-bold" 
          :class="{ active: currentTab === 'drives' }" 
          @click="currentTab = 'drives'"
          type="button"
        >
          💼 Placement Drives
          <span v-if="pendingDrives.length > 0" class="badge bg-warning text-dark ms-1">{{ pendingDrives.length }}</span>
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link fw-bold" 
          :class="{ active: currentTab === 'applications' }" 
          @click="currentTab = 'applications'"
          type="button"
        >
          📝 Student Applications ({{ applications.length }})
        </button>
      </li>
    </ul>

    <!-- ================= COMPANIES TAB ================= -->
    <div v-if="currentTab === 'companies'">
      <!-- Pending Requests Section -->
      <div class="card mb-4 border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Pending Company Approvals</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>HR Contact Name</th>
                  <th>HR Phone</th>
                  <th>Website</th>
                  <th>Industry</th>
                  <th style="width: 220px; text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in pendingCompanies" :key="c.id">
                  <td><strong>{{ c.company_name }}</strong></td>
                  <td>{{ c.hr_contact || 'N/A' }}</td>
                  <td>{{ c.hr_phone || 'N/A' }}</td>
                  <td><a :href="c.website" target="_blank" class="text-primary text-decoration-underline">{{ c.website || 'N/A' }}</a></td>
                  <td>{{ c.industry || 'N/A' }}</td>
                  <td style="text-align: right;">
                    <button @click="viewCompanyDetails(c)" class="btn btn-outline-secondary btn-xs py-0 px-2 me-1" style="font-size: 11px;">details</button>
                    <button @click="approveCompany(c.id, 'approve')" class="btn btn-success btn-xs py-0 px-2 me-1" style="font-size: 11px;">Approve</button>
                    <button @click="approveCompany(c.id, 'reject')" class="btn btn-danger btn-xs py-0 px-2" style="font-size: 11px;">Reject</button>
                  </td>
                </tr>
                <tr v-if="pendingCompanies.length === 0">
                  <td colspan="6" class="text-center text-muted p-3">No pending registration requests</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Approved and Blacklisted Section -->
      <div class="card border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Registered Companies Directory</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>HR Contact Name</th>
                  <th>Email Address</th>
                  <th>Industry</th>
                  <th>Headquarters</th>
                  <th>Status</th>
                  <th style="width: 220px; text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in filteredCompanies" :key="c.id">
                  <td><strong>{{ c.company_name }}</strong></td>
                  <td>{{ c.hr_contact || 'N/A' }}</td>
                  <td>{{ c.email }}</td>
                  <td>{{ c.industry || 'N/A' }}</td>
                  <td>{{ c.headquarters || 'N/A' }}</td>
                  <td>
                    <span :class="badgeClass(c.approval_status)">{{ c.approval_status }}</span>
                  </td>
                  <td style="text-align: right;">
                    <button @click="viewCompanyDetails(c)" class="btn btn-outline-secondary btn-xs py-0 px-2 me-1" style="font-size: 11px;">details</button>
                    <button 
                      v-if="c.approval_status !== 'blacklisted'"
                      @click="blacklistCompany(c.id)" 
                      class="btn btn-outline-danger btn-xs py-0 px-2" 
                      style="font-size: 11px;"
                    >
                      blacklist
                    </button>
                    <button 
                      v-else
                      @click="approveCompany(c.id, 'approve')" 
                      class="btn btn-success btn-xs py-0 px-2" 
                      style="font-size: 11px;"
                    >
                      re-activate
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredCompanies.length === 0">
                  <td colspan="7" class="text-center text-muted p-3">No registered companies found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= STUDENTS TAB ================= -->
    <div v-if="currentTab === 'students'">
      <div class="card border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Registered Student Directory</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Roll Number</th>
                  <th>Branch / Dept</th>
                  <th>Academic Year</th>
                  <th>CGPA</th>
                  <th>Backlogs</th>
                  <th>Placed</th>
                  <th>Status</th>
                  <th style="width: 220px; text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="s in filteredStudents" :key="s.id">
                  <td><strong>{{ s.full_name }}</strong></td>
                  <td>{{ s.roll_number }}</td>
                  <td>{{ s.branch }}</td>
                  <td>Year {{ s.year }}</td>
                  <td>{{ s.cgpa }}</td>
                  <td>{{ s.backlogs }}</td>
                  <td>
                    <span class="badge" :class="s.is_placed ? 'bg-success' : 'bg-secondary'">{{ s.is_placed ? 'Placed' : 'Not Placed' }}</span>
                  </td>
                  <td>
                    <span :class="badgeClass(s.status)">{{ s.status }}</span>
                  </td>
                  <td style="text-align: right;">
                    <button @click="viewStudentDetails(s)" class="btn btn-outline-secondary btn-xs py-0 px-2 me-1" style="font-size: 11px;">details</button>
                    <button 
                      v-if="s.status !== 'blacklisted'"
                      @click="blacklistStudent(s.id)" 
                      class="btn btn-outline-danger btn-xs py-0 px-2" 
                      style="font-size: 11px;"
                    >
                      blacklist
                    </button>
                    <button 
                      v-else
                      @click="activateStudent(s.id)" 
                      class="btn btn-success btn-xs py-0 px-2" 
                      style="font-size: 11px;"
                    >
                      re-activate
                    </button>
                  </td>
                </tr>
                <tr v-if="filteredStudents.length === 0">
                  <td colspan="9" class="text-center text-muted p-3">No registered students found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= PLACEMENT DRIVES TAB ================= -->
    <div v-if="currentTab === 'drives'">
      <!-- Proposed Drives Section -->
      <div class="card mb-4 border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Pending Drive Proposals</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Location</th>
                  <th>Openings</th>
                  <th>Min CGPA</th>
                  <th>Deadline</th>
                  <th style="width: 220px; text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in pendingDrives" :key="d.id">
                  <td><strong>{{ d.job_title }}</strong></td>
                  <td>{{ d.company }}</td>
                  <td>{{ d.location || 'N/A' }}</td>
                  <td>{{ d.openings }}</td>
                  <td>&ge; {{ d.min_cgpa }}</td>
                  <td>{{ d.deadline ? d.deadline.slice(0, 16).replace('T', ' ') : '' }}</td>
                  <td style="text-align: right;">
                    <button @click="viewDriveDetails(d)" class="btn btn-outline-secondary btn-xs py-0 px-2 me-1" style="font-size: 11px;">details</button>
                    <button @click="approveDrive(d.id, 'approve')" class="btn btn-success btn-xs py-0 px-2 me-1" style="font-size: 11px;">Approve</button>
                    <button @click="approveDrive(d.id, 'reject')" class="btn btn-danger btn-xs py-0 px-2" style="font-size: 11px;">Reject</button>
                  </td>
                </tr>
                <tr v-if="pendingDrives.length === 0">
                  <td colspan="7" class="text-center text-muted p-3">No pending drive proposals</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Ongoing Approved Drives Section -->
      <div class="card mb-4 border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Ongoing Approved Drives</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Location</th>
                  <th>Salary Package</th>
                  <th>Deadline</th>
                  <th style="width: 220px; text-align: right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in activeDrives" :key="d.id">
                  <td><strong>{{ d.job_title }}</strong></td>
                  <td>{{ d.company }}</td>
                  <td>{{ d.location || 'N/A' }}</td>
                  <td>{{ d.salary_range || 'N/A' }}</td>
                  <td>{{ d.deadline ? d.deadline.slice(0, 16).replace('T', ' ') : '' }}</td>
                  <td style="text-align: right;">
                    <button @click="viewDriveDetails(d)" class="btn btn-outline-secondary btn-xs py-0 px-2 me-1" style="font-size: 11px;">details</button>
                    <button @click="markDriveComplete(d.id)" class="btn btn-outline-success btn-xs py-0 px-2 me-1" style="font-size: 11px;">mark completed</button>
                    <button @click="cancelDrive(d.id)" class="btn btn-outline-danger btn-xs py-0 px-2" style="font-size: 11px;">cancel</button>
                  </td>
                </tr>
                <tr v-if="activeDrives.length === 0">
                  <td colspan="6" class="text-center text-muted p-3">No active ongoing drives</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Closed & Rejected Drives Section -->
      <div class="card border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Completed, Rejected, & Cancelled Drives History</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Location</th>
                  <th>Salary</th>
                  <th>Status</th>
                  <th>Rejection Reason</th>
                  <th style="width: 100px; text-align: right;">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="d in inactiveDrives" :key="d.id">
                  <td><strong>{{ d.job_title }}</strong></td>
                  <td>{{ d.company }}</td>
                  <td>{{ d.location || 'N/A' }}</td>
                  <td>{{ d.salary_range || 'N/A' }}</td>
                  <td><span :class="badgeClass(d.status)">{{ d.status }}</span></td>
                  <td><span class="text-muted small">{{ d.rejection_reason || 'None' }}</span></td>
                  <td style="text-align: right;">
                    <button @click="viewDriveDetails(d)" class="btn btn-outline-secondary btn-xs py-0 px-2" style="font-size: 11px;">details</button>
                  </td>
                </tr>
                <tr v-if="inactiveDrives.length === 0">
                  <td colspan="7" class="text-center text-muted p-3">No drive history records found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= STUDENT APPLICATIONS TAB ================= -->
    <div v-if="currentTab === 'applications'">
      <div class="card border-dark shadow-sm">
        <div class="card-header bg-dark text-white py-2">
          <h5 class="card-title h6 mb-0">Student Application Logs</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover table-striped mb-0 small align-middle">
              <thead>
                <tr>
                  <th style="width: 80px;">Sr No.</th>
                  <th>Student Name</th>
                  <th>Roll Number</th>
                  <th>Branch</th>
                  <th>Job Drive</th>
                  <th>Company Name</th>
                  <th>Applied On</th>
                  <th>Status</th>
                  <th style="width: 100px; text-align: right;">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(app, idx) in applications" :key="app.id">
                  <td>{{ idx + 1 }}.</td>
                  <td><strong>{{ app.student_name }}</strong></td>
                  <td>{{ app.roll_number }}</td>
                  <td>{{ app.branch }}</td>
                  <td>{{ app.job_title }}</td>
                  <td>{{ app.company_name }}</td>
                  <td>{{ app.applied_at ? app.applied_at.slice(0, 16).replace('T', ' ') : '' }}</td>
                  <td>
                    <span :class="badgeClass(app.status)">{{ app.status }}</span>
                  </td>
                  <td style="text-align: right;">
                    <button @click="viewStudentApplication(app)" class="btn btn-outline-primary btn-xs py-0 px-2" style="font-size: 11px;">view log</button>
                  </td>
                </tr>
                <tr v-if="applications.length === 0">
                  <td colspan="9" class="text-center text-muted p-3">No student applications found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ========================================================================= -->
    <!-- INTERACTIVE DETAIL MODAL OVERLAYS (Bootstrap style wireframe modals) -->
    <!-- ========================================================================= -->

    <!-- COMPANY DETAILS MODAL -->
    <div v-if="selectedCompany" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded-3 shadow">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">🏢 Company Profile Details</h5>
            <button type="button" class="btn-close btn-close-white" @click="selectedCompany = null"></button>
          </div>
          <div class="modal-body">
            <h4 class="fw-bold border-bottom pb-2 mb-3">{{ selectedCompany.company_name }}</h4>
            <div class="row g-2 mb-3 small">
              <div class="col-6"><strong>Email:</strong> {{ selectedCompany.email }}</div>
              <div class="col-6"><strong>HR Contact:</strong> {{ selectedCompany.hr_contact }}</div>
              <div class="col-6"><strong>HR Phone:</strong> {{ selectedCompany.hr_phone || 'N/A' }}</div>
              <div class="col-6"><strong>Website:</strong> <a :href="selectedCompany.website" target="_blank" class="text-primary text-decoration-underline">{{ selectedCompany.website || 'N/A' }}</a></div>
              <div class="col-6"><strong>Industry:</strong> {{ selectedCompany.industry || 'N/A' }}</div>
              <div class="col-6"><strong>Headquarters:</strong> {{ selectedCompany.headquarters || 'N/A' }}</div>
              <div class="col-6"><strong>Founded Year:</strong> {{ selectedCompany.founded_year || 'N/A' }}</div>
              <div class="col-6"><strong>Employees:</strong> {{ selectedCompany.employee_count || 'N/A' }}</div>
              <div class="col-12 mt-2"><strong>Approval Status:</strong> <span :class="badgeClass(selectedCompany.approval_status)">{{ selectedCompany.approval_status }}</span></div>
            </div>
            <strong>Description:</strong>
            <div class="border rounded p-2 mt-1 small bg-light" style="white-space: pre-wrap; font-family: monospace; max-height: 150px; overflow-y: auto;">
              {{ selectedCompany.description || 'No description provided.' }}
            </div>
          </div>
          <div class="modal-footer py-1">
            <button type="button" class="btn btn-secondary btn-sm" @click="selectedCompany = null">Close</button>
            <template v-if="selectedCompany.approval_status === 'pending'">
              <button @click="approveCompany(selectedCompany.id, 'approve'); selectedCompany = null" class="btn btn-success btn-sm">Approve</button>
              <button @click="approveCompany(selectedCompany.id, 'reject'); selectedCompany = null" class="btn btn-danger btn-sm">Reject</button>
            </template>
            <button 
              v-if="selectedCompany.approval_status === 'blacklisted'"
              @click="approveCompany(selectedCompany.id, 'approve'); selectedCompany = null" 
              class="btn btn-success btn-sm"
            >
              Re-Activate Company
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- STUDENT DETAILS MODAL -->
    <div v-if="selectedStudent" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded-3 shadow">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">🎓 Student Profile Details</h5>
            <button type="button" class="btn-close btn-close-white" @click="selectedStudent = null"></button>
          </div>
          <div class="modal-body">
            <h4 class="fw-bold border-bottom pb-2 mb-3">{{ selectedStudent.full_name }}</h4>
            <div class="row g-2 mb-3 small">
              <div class="col-6"><strong>Roll Number:</strong> {{ selectedStudent.roll_number }}</div>
              <div class="col-6"><strong>Email:</strong> {{ selectedStudent.email }}</div>
              <div class="col-6"><strong>Branch:</strong> {{ selectedStudent.branch }}</div>
              <div class="col-6"><strong>Academic Year:</strong> Year {{ selectedStudent.year }}</div>
              <div class="col-6"><strong>Current CGPA:</strong> {{ selectedStudent.cgpa }}</div>
              <div class="col-6"><strong>Active Backlogs:</strong> {{ selectedStudent.backlogs }}</div>
              <div class="col-6"><strong>Phone:</strong> {{ selectedStudent.phone || 'N/A' }}</div>
              <div class="col-6"><strong>Graduation Year:</strong> {{ selectedStudent.graduation_year || 'N/A' }}</div>
              <div class="col-6"><strong>Placement Status:</strong> <span class="badge" :class="selectedStudent.is_placed ? 'bg-success' : 'bg-secondary'">{{ selectedStudent.is_placed ? 'Placed' : 'Not Placed' }}</span></div>
              <div class="col-6"><strong>Status:</strong> <span :class="badgeClass(selectedStudent.status)">{{ selectedStudent.status }}</span></div>
            </div>
            <p class="mb-1 small"><strong>Skills:</strong> {{ selectedStudent.skills || 'None listed' }}</p>
            <p class="mb-1 small"><strong>LinkedIn:</strong> <a v-if="selectedStudent.linkedin_url" :href="selectedStudent.linkedin_url" target="_blank" class="text-decoration-underline">{{ selectedStudent.linkedin_url }}</a><span v-else>N/A</span></p>
            <p class="mb-1 small"><strong>GitHub:</strong> <a v-if="selectedStudent.github_url" :href="selectedStudent.github_url" target="_blank" class="text-decoration-underline">{{ selectedStudent.github_url }}</a><span v-else>N/A</span></p>
            <strong class="small d-block mt-2">Bio:</strong>
            <div class="border rounded p-2 mt-1 small bg-light mb-3" style="white-space: pre-wrap; font-family: monospace; max-height: 100px; overflow-y: auto;">
              {{ selectedStudent.bio || 'No bio provided.' }}
            </div>
            
            <div v-if="selectedStudent.resume_filename" class="text-center p-2 border rounded border-success bg-light">
              <span class="small me-3">📄 Resume is available ({{ selectedStudent.resume_filename }})</span>
              <button @click="viewResume(selectedStudent.id)" class="btn btn-outline-success btn-sm py-0" style="font-size: 12px;">download resume</button>
            </div>
            <div v-else class="text-center p-2 border rounded border-secondary bg-light text-muted small">
              No resume uploaded yet
            </div>
          </div>
          <div class="modal-footer py-1">
            <button type="button" class="btn btn-secondary btn-sm" @click="selectedStudent = null">Close</button>
            <button 
              v-if="selectedStudent.status !== 'blacklisted'"
              @click="blacklistStudent(selectedStudent.id); selectedStudent = null" 
              class="btn btn-danger btn-sm"
            >
              Blacklist Student
            </button>
            <button 
              v-else
              @click="activateStudent(selectedStudent.id); selectedStudent = null" 
              class="btn btn-success btn-sm"
            >
              Re-Activate Student
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- DRIVE DETAILS MODAL -->
    <div v-if="selectedDrive" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded-3 shadow">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">💼 Placement Drive Details</h5>
            <button type="button" class="btn-close btn-close-white" @click="selectedDrive = null"></button>
          </div>
          <div class="modal-body">
            <h4 class="fw-bold border-bottom pb-2 mb-3">{{ selectedDrive.job_title }}</h4>
            <div class="row g-2 mb-3 small">
              <div class="col-6"><strong>Company:</strong> {{ selectedDrive.company }}</div>
              <div class="col-6"><strong>Location:</strong> {{ selectedDrive.location || 'N/A' }}</div>
              <div class="col-6"><strong>Job Type:</strong> {{ selectedDrive.job_type }}</div>
              <div class="col-6"><strong>Salary Package:</strong> {{ selectedDrive.salary_range || 'N/A' }}</div>
              <div class="col-6"><strong>Openings:</strong> {{ selectedDrive.openings }}</div>
              <div class="col-6"><strong>Minimum CGPA:</strong> {{ selectedDrive.min_cgpa }}</div>
              <div class="col-6"><strong>Max Backlogs Allowed:</strong> {{ selectedDrive.max_backlogs }}</div>
              <div class="col-12"><strong>Eligible Branches:</strong> {{ selectedDrive.eligible_branches || 'All' }}</div>
              <div class="col-12"><strong>Application Deadline:</strong> {{ selectedDrive.deadline ? selectedDrive.deadline.slice(0, 16).replace('T', ' ') : 'N/A' }}</div>
              <div class="col-6"><strong>Status:</strong> <span :class="badgeClass(selectedDrive.status)">{{ selectedDrive.status }}</span></div>
            </div>
            <strong>Job Description:</strong>
            <div class="border rounded p-2 mt-1 small bg-light" style="white-space: pre-wrap; font-family: monospace; max-height: 150px; overflow-y: auto;">
              {{ selectedDrive.job_description || 'No description provided.' }}
            </div>
          </div>
          <div class="modal-footer py-1">
            <button type="button" class="btn btn-secondary btn-sm" @click="selectedDrive = null">Close</button>
            <template v-if="selectedDrive.status === 'pending'">
              <button @click="approveDrive(selectedDrive.id, 'approve'); selectedDrive = null" class="btn btn-success btn-sm">Approve Proposal</button>
              <button @click="approveDrive(selectedDrive.id, 'reject'); selectedDrive = null" class="btn btn-danger btn-sm">Reject Proposal</button>
            </template>
            <button 
              v-if="selectedDrive.status === 'approved'"
              @click="markDriveComplete(selectedDrive.id); selectedDrive = null" 
              class="btn btn-success btn-sm"
            >
              Mark Completed
            </button>
            <button 
              v-if="selectedDrive.status === 'approved'"
              @click="cancelDrive(selectedDrive.id); selectedDrive = null" 
              class="btn btn-danger btn-sm"
            >
              Cancel Drive
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- STUDENT APPLICATION DETAILS MODAL -->
    <div v-if="selectedApplication" class="modal fade show d-block" tabindex="-1" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border border-dark rounded-3 shadow">
          <div class="modal-header bg-dark text-white py-2">
            <h5 class="modal-title h6">📝 Student Application Review</h5>
            <button type="button" class="btn-close btn-close-white" @click="selectedApplication = null"></button>
          </div>
          <div class="modal-body">
            <h5 class="fw-bold border-bottom pb-2 mb-3">Application Status: <span :class="badgeClass(selectedApplication.status)">{{ selectedApplication.status }}</span></h5>
            <div class="row g-2 mb-3 small">
              <div class="col-6"><strong>Student Name:</strong> {{ selectedApplication.student_name }}</div>
              <div class="col-6"><strong>Roll Number:</strong> {{ selectedApplication.roll_number }}</div>
              <div class="col-6"><strong>Department:</strong> {{ selectedApplication.branch }}</div>
              <div class="col-6"><strong>Student CGPA:</strong> {{ selectedApplication.student_cgpa }}</div>
              <div class="col-6"><strong>Job Drive:</strong> {{ selectedApplication.job_title }}</div>
              <div class="col-6"><strong>Company:</strong> {{ selectedApplication.company_name }}</div>
              <div class="col-6"><strong>Applied On:</strong> {{ selectedApplication.applied_at ? selectedApplication.applied_at.slice(0, 16).replace('T', ' ') : 'N/A' }}</div>
            </div>
            
            <strong>Cover Letter / Notes:</strong>
            <div class="border rounded p-2 mt-1 mb-3 small bg-light" style="white-space: pre-wrap; font-family: monospace; max-height: 100px; overflow-y: auto;">
              {{ selectedApplication.cover_letter || 'No cover letter provided.' }}
            </div>

            <strong>Company Remarks:</strong>
            <div class="border rounded p-2 mt-1 mb-3 small bg-light" style="white-space: pre-wrap; font-family: monospace; max-height: 80px; overflow-y: auto;">
              {{ selectedApplication.remarks || 'No remarks from company yet.' }}
            </div>

            <div class="text-center p-2 border rounded bg-light">
              <button @click="viewResume(selectedApplication.student_id)" class="btn btn-outline-primary btn-sm">download student resume</button>
            </div>
          </div>
          <div class="modal-footer py-1">
            <button type="button" class="btn btn-secondary btn-sm" @click="selectedApplication = null">Close</button>
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
      email: localStorage.getItem('email') || 'Admin',
      searchQuery: '',
      searchActive: false,
      msg: '',
      errMsg: '',
      currentTab: 'companies',
      companies: [],
      students: [],
      drives: [],
      applications: [],
      selectedCompany: null,
      selectedStudent: null,
      selectedDrive: null,
      selectedApplication: null
    }
  },
  computed: {
    pendingCompanies() {
      return this.companies.filter(c => c.approval_status === 'pending')
    },
    filteredCompanies() {
      return this.companies.filter(c => c.approval_status === 'approved' || c.approval_status === 'blacklisted')
    },
    filteredStudents() {
      return this.students
    },
    pendingDrives() {
      return this.drives.filter(d => d.status === 'pending')
    },
    activeDrives() {
      return this.drives.filter(d => d.status === 'approved')
    },
    inactiveDrives() {
      // Completed, rejected, or cancelled
      return this.drives.filter(d => d.status === 'completed' || d.status === 'rejected' || d.status === 'cancelled')
    }
  },
  async mounted() {
    await this.loadAll()
  },
  methods: {
    headers() {
      return { Authorization: `Bearer ${localStorage.getItem('token')}` }
    },
    async loadAll() {
      this.errMsg = ''
      try {
        const [compRes, studRes, driveRes, appRes] = await Promise.all([
          axios.get('http://localhost:5000/api/admin/companies', { headers: this.headers() }),
          axios.get('http://localhost:5000/api/admin/students', { headers: this.headers() }),
          axios.get('http://localhost:5000/api/admin/drives', { headers: this.headers() }),
          axios.get('http://localhost:5000/api/admin/applications', { headers: this.headers() })
        ])
        this.companies = compRes.data
        this.students = studRes.data
        this.drives = driveRes.data
        this.applications = appRes.data
      } catch (e) {
        this.errMsg = 'Failed to load data: ' + (e.response?.data?.error || e.message)
      }
    },
    async handleSearch() {
      if (!this.searchQuery.trim()) {
        await this.loadAll()
        return
      }
      this.searchActive = true
      try {
        const res = await axios.get(`http://localhost:5000/api/admin/search?q=${this.searchQuery}`, { headers: this.headers() })
        this.companies = res.data.companies
        this.students = res.data.students
        this.drives = res.data.drives
      } catch (e) {
        this.errMsg = 'Search failed: ' + (e.response?.data?.error || e.message)
      }
    },
    async resetSearch() {
      this.searchQuery = ''
      this.searchActive = false
      await this.loadAll()
    },
    async approveCompany(id, action) {
      let reason = ''
      if (action === 'reject') {
        reason = prompt('Please enter a rejection reason:')
        if (reason === null) return // cancelled
      }
      try {
        const res = await axios.put(
          `http://localhost:5000/api/admin/companies/${id}/approve`,
          { action, reason },
          { headers: this.headers() }
        )
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Error updating company status'
      }
    },
    async approveDrive(id, action) {
      let reason = ''
      if (action === 'reject') {
        reason = prompt('Please enter a rejection reason for this drive:')
        if (reason === null) return // cancelled
      }
      try {
        const res = await axios.put(
          `http://localhost:5000/api/admin/drives/${id}/approve`,
          { action, reason },
          { headers: this.headers() }
        )
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Error updating drive status'
      }
    },
    async blacklistCompany(id) {
      if (!confirm('Are you sure you want to blacklist this company? This will deactivate their login and cancel all their placement drives.')) return
      try {
        const res = await axios.put(`http://localhost:5000/api/admin/companies/${id}/blacklist`, {}, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Blacklist failed'
      }
    },
    async blacklistStudent(id) {
      if (!confirm('Are you sure you want to blacklist this student? This will deactivate their login.')) return
      try {
        const res = await axios.put(`http://localhost:5000/api/admin/students/${id}/blacklist`, {}, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Blacklist failed'
      }
    },
    async activateStudent(id) {
      try {
        const res = await axios.put(`http://localhost:5000/api/admin/students/${id}/activate`, {}, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Activation failed'
      }
    },
    async cancelDrive(id) {
      if (!confirm('Are you sure you want to cancel this drive?')) return
      try {
        const res = await axios.put(`http://localhost:5000/api/admin/drives/${id}/cancel`, {}, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Cancel drive failed'
      }
    },
    async markDriveComplete(id) {
      try {
        const res = await axios.put(`http://localhost:5000/api/admin/drives/${id}/complete`, {}, { headers: this.headers() })
        this.msg = res.data.message
        await this.loadAll()
        setTimeout(() => this.msg = '', 4000)
      } catch (e) {
        this.errMsg = e.response?.data?.error || 'Action failed'
      }
    },
    viewCompanyDetails(company) {
      this.selectedCompany = company
    },
    viewStudentDetails(student) {
      this.selectedStudent = student
    },
    viewDriveDetails(drive) {
      this.selectedDrive = drive
    },
    viewStudentApplication(app) {
      this.selectedApplication = app
    },
    viewResume(studentId) {
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
      this.$router.replace('/login')
    },
    badgeClass(status) {
      const map = {
        'approved': 'badge bg-success',
        'pending': 'badge bg-warning text-dark',
        'completed': 'badge bg-secondary',
        'rejected': 'badge bg-danger',
        'cancelled': 'badge bg-danger',
        'blacklisted': 'badge bg-dark',
        'selected': 'badge bg-success',
        'shortlisted': 'badge bg-info',
        'applied': 'badge bg-warning text-dark'
      }
      return map[status] || 'badge bg-secondary'
    }
  }
}
</script>
