# Todo Full-Stack Application

A modern, feature-rich todo application with AI-powered task parsing, built with React/TypeScript frontend and FastAPI/PostgreSQL backend.

## Features

### Core Features
- ✅ Full CRUD operations for tasks, projects, and tags
- ✅ Smart Views (All, Today, This Week, Overdue)
- ✅ Advanced filtering and search
- ✅ Priority levels (Low, Medium, High) with color coding
- ✅ Due dates with overdue detection
- ✅ Projects for organizing tasks
- ✅ Tags for flexible categorization
- ✅ Modern, responsive UI with Tailwind CSS
- ✅ Toast notifications for user actions
- ✅ Comprehensive test coverage (backend + frontend)

### AI-Powered Features
- ✅ **Natural Language Task Parsing** - Transform conversational input into structured tasks
  - "Buy groceries tomorrow evening high priority" → Automatically extracts title, date, priority, and tags
  - Supports relative dates ("tomorrow", "next Friday", "end of week")
  - Infers priority from keywords ("urgent", "important", "asap")
  - Suggests contextual tags ("work", "personal", "shopping")
  - Uses GPT-4o-mini (~$0.0001 per parse, essentially free for personal use)

## Tech Stack

**Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, React Hot Toast  
**Backend:** FastAPI, PostgreSQL, SQLAlchemy, Alembic, Pydantic, OpenAI  
**Testing:** Pytest (backend), Vitest + Testing Library (frontend)  
**DevOps:** Docker Compose, Git

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL)
- OpenAI API key (optional, for AI features)

### 1. Clone & Setup Database

```bash
git clone <repository-url>
cd todo-fullstack

# Start PostgreSQL
docker-compose up -d
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env and add:
# DATABASE_URL=postgresql://todouser:todopass@localhost:5432/tododb
# OPENAI_API_KEY=sk-your-key-here  (optional, for AI features)

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (create .env file)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start frontend
npm run dev
```

Frontend available at: http://localhost:5173

## AI Setup (Optional)

### Getting Your OpenAI API Key

1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to **API Keys** section
3. Click **"Create new secret key"**
4. Copy the key to `backend/.env`:
   ```
   OPENAI_API_KEY=sk-your-actual-key-here
   ```
5. Add at least $5 in credits to your OpenAI account

### Using AI Task Parsing

1. Start the application (both backend and frontend)
2. Click **"Add New Task"** to expand the form
3. Click the **"✨ Use AI Parser"** button
4. Type naturally:
   - "Buy groceries tomorrow evening high priority"
   - "Schedule dentist appointment next Friday at 2pm"
   - "Review project proposal by end of week for work project"
5. Click **"Parse with AI"**
6. Review and edit the auto-filled fields
7. Submit your task

**Cost:** ~$0.0001 per parse (about $0.15/month for 50 parses/day)

## Project Structure

```
todo-fullstack/
├── backend/
│   ├── app/
│   │   ├── routers/            # API endpoints (tasks, projects, tags, ai)
│   │   ├── services/           # Business logic (AI parsing)
│   │   ├── models.py           # SQLAlchemy database models
│   │   ├── schemas.py          # Pydantic validation schemas
│   │   ├── crud.py             # Database operations
│   │   ├── database.py         # Database connection
│   │   └── main.py             # FastAPI application
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Backend tests (pytest)
│   ├── requirements.txt        # Python dependencies
│   └── env.example             # Environment template
├── frontend/
│   ├── src/
│   │   ├── components/         # React components (TaskForm, TaskItem, TaskList)
│   │   ├── services/           # API client
│   │   ├── types/              # TypeScript type definitions
│   │   ├── App.tsx             # Main application
│   │   └── main.tsx            # Entry point
│   ├── package.json            # Node dependencies
│   └── vite.config.ts          # Vite configuration
└── docker-compose.yml          # PostgreSQL setup
```

## API Endpoints

### Core Resources
- **Tasks:** `GET|POST /api/tasks`, `GET|PATCH|DELETE /api/tasks/{id}`
- **Projects:** `GET|POST /api/projects`, `GET|PATCH|DELETE /api/projects/{id}`
- **Tags:** `GET|POST /api/tags`, `GET|PATCH|DELETE /api/tags/{id}`

### AI Features
- **Parse Task:** `POST /api/ai/parse-task` - Convert natural language to structured task
- **AI Health:** `GET /api/ai/health` - Check if AI service is configured

### Advanced Filtering
Query parameters for `/api/tasks`:
- `completed=true|false` - Filter by completion status
- `project_id=1` - Filter by project
- `tag_ids=1&tag_ids=2` - Filter by tags (AND logic)
- `search=keyword` - Search title and description
- `view=today|week|overdue|all` - Smart views
- `sort=priority|due_date_asc|due_date_desc|created_at_desc` - Sort options

**Example:** `GET /api/tasks?view=today&project_id=1&sort=priority`

## Database Schema

### Task
```
id, title, description, priority (enum), due_date, is_completed,
project_id (FK), created_at, updated_at
Relationships: project (many-to-one), tags (many-to-many)
```

### Project
```
id, name (unique), color (hex), description, created_at
Relationship: tasks (one-to-many, cascade delete)
```

### Tag
```
id, name (unique), color (hex), created_at
Relationship: tasks (many-to-many)
```

## Development

### Backend Commands

```bash
cd backend

# Run tests
pytest
pytest --cov=app --cov-report=html  # With coverage

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Run specific tests
pytest tests/test_ai.py -v
```

### Frontend Commands

```bash
cd frontend

# Development
npm run dev

# Production build
npm run build
npm run preview

# Testing
npm test
npm run test:ui
npm run test:coverage

# Linting
npm run lint
```

## Testing

### Backend Tests (17 tests, 78% coverage)
- Task CRUD operations
- Project and tag management
- Smart views (today, week, overdue)
- Filtering and search
- AI task parsing (with mocked OpenAI)
- Validation and error handling

```bash
cd backend
pytest -v
```

### Frontend Tests (12 tests)
- Component rendering
- Task creation and editing
- API client functionality
- User interactions

```bash
cd frontend
npm test
```

## Environment Variables

### Backend (`backend/.env`)
```bash
# Required: Database connection
DATABASE_URL=postgresql://todouser:todopass@localhost:5432/tododb

# Optional: AI task parsing
OPENAI_API_KEY=sk-your-api-key-here
```

### Frontend (`frontend/.env`)
```bash
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Database Issues
```bash
# Check if PostgreSQL is running
docker ps

# View logs
docker-compose logs postgres

# Restart
docker-compose restart postgres

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
cd backend && alembic upgrade head
```

### Backend Issues
```bash
# Check backend health
curl http://localhost:8000/health

# Check AI service status
curl http://localhost:8000/api/ai/health

# Common fixes:
# 1. Activate virtual environment: source venv/bin/activate
# 2. Reinstall dependencies: pip install -r requirements.txt
# 3. Check .env file exists and has correct values
```

### Frontend Issues
```bash
# Check API connection
curl http://localhost:8000/api/tasks

# Common fixes:
# 1. Clear cache: rm -rf node_modules package-lock.json && npm install
# 2. Check .env file: VITE_API_URL should match backend URL
# 3. Restart dev server: npm run dev
```

### AI Issues

**"AI service not configured" error:**
- Verify `OPENAI_API_KEY` is set in `backend/.env`
- Ensure key is not the placeholder "your-api-key-here"
- Restart backend server after adding key

**AI toggle button not appearing:**
- Frontend checks `/api/ai/health` on load
- Check browser console for errors
- Verify backend is running

**Parsing is slow (>3 seconds):**
- Normal response time: 1-3 seconds
- Check network connection
- Verify OpenAI API status at https://status.openai.com/

## Deployment

### Backend Production
```bash
# Use production ASGI server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Best practices:
# - Use environment variables (not .env files)
# - Enable HTTPS
# - Configure CORS properly
# - Add rate limiting
# - Enable logging and monitoring
# - Set up database backups
```

### Frontend Production
```bash
# Build optimized bundle
npm run build

# Deploy dist/ folder to:
# - Vercel, Netlify, AWS S3, Azure Static Web Apps, GitHub Pages

# Set production environment variable:
VITE_API_URL=https://your-production-api.com
```

## Advanced Configuration

### Customize AI Model

Edit `backend/app/services/ai_service.py`:

```python
# Use cheaper model (slightly less accurate)
parser = AITaskParser(api_key=api_key, model="gpt-3.5-turbo")

# Use better model (more expensive)
parser = AITaskParser(api_key=api_key, model="gpt-4")
```

### Customize AI Prompts

Edit the prompt in `backend/app/services/ai_service.py` in the `parse_task()` method to:
- Modify extraction rules
- Adjust date parsing behavior
- Change tag suggestion logic
- Add domain-specific instructions

### Security Best Practices

1. Never commit `.env` files (already in `.gitignore`)
2. Rotate API keys if exposed
3. Set usage limits in OpenAI dashboard
4. Use different API keys for dev/production
5. Enable rate limiting for production

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## Future Enhancements

- Subtasks/checklist items
- Bulk operations (multi-select, delete, complete)
- Drag-and-drop task ordering
- User authentication and multi-user support
- Recurring tasks
- File attachments
- Reminders and notifications
- Calendar view
- Dark mode
- Mobile apps
- Enhanced AI features (auto-categorization, smart scheduling)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Create an issue in the repository
- Check [existing issues](https://github.com/your-repo/issues) for solutions
- Review API documentation at http://localhost:8000/docs
