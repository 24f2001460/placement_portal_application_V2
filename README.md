#Placement Portal Application

A comprehensive, role-based placement portal application featuring automatic eligibility filtering, student applications, company proposal workflows, admin dashboard management, caching, and background Celery tasks (daily alerts and monthly reports).

---

## Prerequisites
* **Python** (version 3.8 or above)
* **Node.js** (version 18 or above)
* **Redis Server** (running locally on default port `6379`)

---

## 1. Backend Setup & Run

### A. Setup Virtual Environment & Dependencies
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Install python dependencies:
   ```bash
   pip install -r requirement.txt
   ```

### B. Seed the Database
Seed the local SQLite database with initial mock accounts (admin, students, companies, job drives, and applications):
```bash
python run.py --seed
```
* **Default Admin Credentials:**
  * **Email:** `admin@placement.com`
  * **Password:** `admin123`

### C. Run Flask Server
Start the development server running locally on `http://127.0.0.1:5000`:
```bash
python run.py
```

### D. Start Celery Worker & Beat (Background Tasks)
1. Ensure your local **Redis** instance is running:
   ```bash
   redis-server
   ```
2. Start the Celery Worker process:
   ```bash
   celery -A celery_app.celery worker --loglevel=info
   ```
3. Start the Celery Beat scheduler:
   ```bash
   celery -A celery_app.celery beat --loglevel=info
   ```

---

## 2. Frontend Setup & Run

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server running locally on `http://localhost:5173`:
   ```bash
   npm run dev
   ```
4. Build production distribution bundle:
   ```bash
   npm run build
   ```
