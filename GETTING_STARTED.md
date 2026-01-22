# Getting Started with Todo App

This guide will help you set up and run the Todo application locally for development.

## System Requirements

Before you begin, ensure you have the following installed:

1. **Python 3.11 or higher**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **Node.js 18 or higher**
   - Download: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

3. **Docker Desktop**
   - Download: https://www.docker.com/get-started
   - Verify: `docker --version` and `docker-compose --version`

4. **Git** (if cloning from repository)
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

## Step-by-Step Setup

### Step 1: Get the Code

```bash
# If from a repository
git clone <repository-url>
cd todo-fullstack

# Or if you already have the folder
cd todo-fullstack
```

### Step 2: Start the Database

Open a terminal and run:

```bash
docker-compose up -d
```

This starts PostgreSQL in the background. Verify it's running:

```bash
docker ps
```

You should see a container named `postgres` running.

### Step 3: Set Up the Backend

Open a **new terminal** and follow these steps:

```bash
# Navigate to backend folder
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
venv\Scripts\activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On macOS/Linux:
source venv/bin/activate

# You should see (venv) in your terminal prompt

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
# On Windows:
copy env.example .env

# On macOS/Linux:
cp env.example .env

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test the backend:**
- Open http://localhost:8000 in your browser
- You should see: `{"message":"Todo API","version":"1.0.0","docs":"/docs","redoc":"/redoc"}`
- Visit http://localhost:8000/docs to see the interactive API documentation

### Step 4: Set Up the Frontend

Open **another new terminal** and follow these steps:

```bash
# Navigate to frontend folder
cd frontend

# Install Node.js dependencies (this may take a few minutes)
npm install

# Create environment file with this content:
# VITE_API_URL=http://localhost:8000

# On Windows (PowerShell):
echo "VITE_API_URL=http://localhost:8000" > .env

# On macOS/Linux:
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the development server
npm run dev
```

You should see output like:
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h to show help
```

**Test the frontend:**
- Open http://localhost:5173 in your browser
- You should see the Todo App interface

## You're Ready!

You now have three terminals running:
1. **Docker** - Running PostgreSQL (in background)
2. **Backend** - FastAPI server at http://localhost:8000
3. **Frontend** - React app at http://localhost:5173

### Try It Out

1. **Create a project:**
   - In the right sidebar, click "+ New" under Projects
   - Enter "Work" and pick a color
   - Click "Create Project"

2. **Create a tag:**
   - Click "+ New" under Tags
   - Enter "urgent" and pick a color
   - Click "Create Tag"

3. **Create a task:**
   - Fill out the task form:
     - Title: "Complete project documentation"
     - Description: "Write comprehensive README files"
     - Priority: High
     - Due Date: Tomorrow
     - Project: Work
     - Tags: urgent
   - Click "Add Task"

4. **Try the filters:**
   - Click "Today" to see today's tasks
   - Search for keywords
   - Filter by project or tags
   - Try different sort orders

## Running Tests

### Backend Tests

In the backend terminal:

```bash
# Make sure you're in the backend folder and venv is activated
cd backend
# (venv should be shown in prompt)

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_tasks.py

# View coverage report
# Open backend/htmlcov/index.html in your browser
```

### Frontend Tests

The frontend doesn't have tests set up yet. This is a good Phase 2 addition!

## Stopping the Application

When you're done developing:

1. **Stop the frontend:** Press `Ctrl+C` in the frontend terminal

2. **Stop the backend:** Press `Ctrl+C` in the backend terminal

3. **Stop PostgreSQL:**
   ```bash
   docker-compose down
   ```

4. **Deactivate Python virtual environment:**
   ```bash
   deactivate
   ```

## Restarting the Application

Next time you want to work on the app:

1. **Start PostgreSQL:**
   ```bash
   docker-compose up -d
   ```

2. **Start Backend:**
   ```bash
   cd backend
   venv\Scripts\activate  # Windows
   # or: source venv/bin/activate  # macOS/Linux
   uvicorn app.main:app --reload
   ```

3. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## Troubleshooting

### "Python not found"

- Install Python 3.11+ from https://python.org
- During installation, check "Add Python to PATH"
- Restart your terminal

### "Node not found"

- Install Node.js 18+ from https://nodejs.org
- Restart your terminal

### "docker: command not found"

- Install Docker Desktop from https://docker.com
- Start Docker Desktop application
- Wait for it to fully start (icon should be green)

### "Port already in use"

If you see errors about ports being in use:

**Backend (port 8000):**
- Find what's using port 8000: `netstat -ano | findstr :8000` (Windows)
- Kill the process or change the port in the uvicorn command

**Frontend (port 5173):**
- The error message will suggest an alternative port
- Or change the port in `frontend/vite.config.ts`

**PostgreSQL (port 5432):**
- Stop any other PostgreSQL instances
- Or change the port in `docker-compose.yml`

### "Cannot connect to database"

1. Check Docker is running: `docker ps`
2. Check PostgreSQL logs: `docker-compose logs postgres`
3. Restart PostgreSQL: `docker-compose restart postgres`
4. Verify DATABASE_URL in `backend/.env`

### "Module not found" (Backend)

```bash
# Make sure virtual environment is activated
cd backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### "Module not found" (Frontend)

```bash
cd frontend

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json  # macOS/Linux
# or manually delete node_modules folder on Windows

npm install
```

### Frontend shows "Failed to load tasks"

1. Check backend is running: http://localhost:8000
2. Check VITE_API_URL in `frontend/.env`
3. Check browser console (F12) for errors
4. Check backend terminal for error logs

## Next Steps

1. **Explore the API documentation:**
   - http://localhost:8000/docs

2. **Try all the features:**
   - Create tasks with different priorities
   - Use smart views (Today, This Week, Overdue)
   - Search and filter tasks
   - Organize with projects and tags

3. **Read the documentation:**
   - `README.md` - Project overview
   - `backend/README.md` - Backend details
   - `frontend/README.md` - Frontend details

4. **Plan Phase 2 features:**
   - Review the feature list in `README.md`
   - Consider what to build next

## Getting Help

- Check the documentation in the README files
- Review the code comments
- Test the API at http://localhost:8000/docs
- Check browser console (F12) for frontend errors
- Check backend terminal for backend errors

## Happy Coding!

You're all set to start developing. The app has a solid foundation with:
- Full CRUD operations
- Advanced filtering and search
- Projects and tags
- Smart views
- Comprehensive tests
- Clean, modern UI

Build something amazing!
