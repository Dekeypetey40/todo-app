# Todo Application - Complete Architecture Documentation

**A Multi-Level Guide from Product Vision to Implementation Details**

**Last Updated:** January 22, 2026  
**Version:** 1.0 (MVP + Enhancements)

---

## Table of Contents

1. [Macro Level: Product & Strategy](#macro-level-product--strategy)
2. [Technology Stack: Why These Tools?](#technology-stack-why-these-tools)
3. [Architecture Overview](#architecture-overview)
4. [Backend Deep Dive](#backend-deep-dive)
5. [Frontend Deep Dive](#frontend-deep-dive)
6. [Database Design](#database-design)
7. [API Design Philosophy](#api-design-philosophy)
8. [State Management Strategy](#state-management-strategy)
9. [File-by-File Reference](#file-by-file-reference)
10. [Development Workflow](#development-workflow)
11. [Testing Strategy](#testing-strategy)
12. [Performance Optimizations](#performance-optimizations)

---

# Macro Level: Product & Strategy

## Product Vision

**Goal:** Build a modern, feature-rich todo application that balances simplicity with power-user features.

**Target Users:**
- Individuals managing personal tasks
- Small teams needing lightweight project organization
- Users who want more than a basic list but less than full project management

**Core Value Proposition:**
- Fast, intuitive task capture
- Flexible organization (projects, tags, smart views)
- Beautiful, modern interface
- No learning curve for basic use
- Power features available when needed

---

## MVP Strategy: Build → Learn → Iterate

### Phase 1: Core MVP (Completed)
**Principle:** Ship the smallest useful product first.

**MVP Features:**
1. ✅ Create, read, update, delete tasks
2. ✅ Task properties: title, description, priority, due date
3. ✅ Mark tasks as complete
4. ✅ Basic filtering and sorting

**Why This MVP?**
- **Validates core hypothesis:** Do users need another todo app?
- **Establishes technical foundation:** Database, API, frontend patterns
- **Enables learning:** Real usage data before adding complexity
- **Fast to market:** ~1 week to build and deploy

---

### Phase 2: Organization Features (Completed)
**Principle:** Add organization without overwhelming simplicity.

**Added Features:**
1. ✅ Projects (group tasks by area)
2. ✅ Tags (flexible categorization)
3. ✅ Smart Views (Today, This Week, Overdue)
4. ✅ Search functionality

**Why These Features?**
- **Projects:** User research showed desire to separate work/personal/hobbies
- **Tags:** Provides flexible categorization without rigid hierarchies
- **Smart Views:** Reduces cognitive load ("What should I work on?")
- **Search:** Essential for users with 50+ tasks

**What We Didn't Add (Yet):**
- ❌ Subtasks (adds complexity, unclear value)
- ❌ Bulk operations (niche use case)
- ❌ Drag-and-drop ordering (nice-to-have, not essential)
- ❌ Recurring tasks (complex, low initial demand)

---

### Phase 3: UX Polish (Completed)
**Principle:** Professional apps feel professional.

**Enhancements:**
1. ✅ Modern, responsive design (Tailwind CSS)
2. ✅ Toast notifications (user feedback)
3. ✅ Pagination (performance for large lists)
4. ✅ Routing (dedicated views per context)
5. ✅ Collapsible task form (reduce clutter)

**Why These Enhancements?**
- **Design:** First impressions matter; users judge quality by appearance
- **Toasts:** Silent failures confuse users; explicit feedback builds trust
- **Pagination:** 100+ tasks shouldn't slow the app
- **Routing:** Shareable URLs, browser navigation (back/forward)
- **Collapsible form:** Focuses on task list, form appears when needed

---

### Phase 4: Advanced Features (Completed)
**Principle:** Add power without compromising simplicity.

**Latest Additions:**
1. ✅ AI-powered task parsing (natural language input)
2. ✅ Optimistic UI updates (instant feedback)
3. ✅ Service layer architecture (backend scalability)
4. ✅ Comprehensive testing (frontend + backend)

---

## Feature Prioritization Framework

We used the **RICE** method to prioritize features:

| Feature | Reach | Impact | Confidence | Effort | Score |
|---------|-------|--------|------------|--------|-------|
| Projects | High (80%) | High (3) | High (100%) | Low (2) | **120** |
| Tags | Medium (50%) | High (3) | High (100%) | Low (2) | **75** |
| Smart Views | High (80%) | High (3) | High (100%) | Medium (3) | **80** |
| Search | Medium (40%) | Medium (2) | High (100%) | Low (2) | **40** |
| Subtasks | Low (20%) | Medium (2) | Medium (50%) | High (8) | **2.5** |
| Recurring | Low (15%) | Low (1) | Low (50%) | Very High (10) | **0.75** |

**Result:** Projects, Tags, Smart Views, and Search made it into MVP. Subtasks and Recurring deferred.

---

# Technology Stack: Why These Tools?

## Backend Stack

### FastAPI (Python Web Framework)
**Chosen over:** Flask, Django, Express (Node.js)

**Why FastAPI?**
1. **Automatic API Docs:** Built-in Swagger UI (essential for frontend devs)
2. **Type Safety:** Pydantic validates requests/responses automatically
3. **Performance:** Async support + fast JSON serialization (near-Node.js speeds)
4. **Developer Experience:** Less boilerplate than Django, more structure than Flask
5. **Modern:** Built for Python 3.6+ with type hints

**Perfect For:**
- APIs (our primary use case)
- Typed Python (catches bugs at dev time)
- Teams that want speed without sacrificing structure

**Not Ideal For:**
- Server-rendered HTML (use Django)
- Microservices with heavy async (use Go/Rust)

**Decision Rationale:**
```
Flask: Too minimal, would need many plugins
Django: Too heavy, built for server-rendered apps
FastAPI: Goldilocks - just right for REST APIs
```

---

### PostgreSQL (Database)
**Chosen over:** MySQL, MongoDB, SQLite

**Why PostgreSQL?**
1. **Relational Data:** Tasks have clear relationships (projects, tags)
2. **ACID Guarantees:** Task completion shouldn't be "eventually consistent"
3. **Advanced Features:** Full-text search, JSON columns, array types
4. **Rock Solid:** Battle-tested, excellent documentation
5. **Free & Open Source:** No licensing concerns

**Perfect For:**
- Structured data with relationships
- Applications needing transactions
- Complex queries (joins, aggregations)

**Not Ideal For:**
- Unstructured data (use MongoDB)
- Simple key-value storage (use Redis)
- Embedded databases (use SQLite)

**Our Use Case:**
- Tasks belong to Projects
- Tasks have many Tags (many-to-many)
- Need transactional integrity (delete project shouldn't orphan tasks)

---

### SQLAlchemy (ORM)
**Chosen over:** Raw SQL, Django ORM, Tortoise ORM

**Why SQLAlchemy?**
1. **Database Agnostic:** Easy to switch from Postgres to MySQL if needed
2. **Prevents SQL Injection:** Parameterized queries by default
3. **Relationships:** Handles joins automatically (`task.project.name`)
4. **Migrations:** Works with Alembic for schema changes
5. **Flexibility:** Can drop to raw SQL when needed

**Perfect For:**
- Complex relationships (our task/project/tag model)
- Teams that want type safety but not raw SQL

**Decision Rationale:**
```python
# Without ORM (fragile, verbose)
cursor.execute(
    "SELECT * FROM tasks WHERE project_id = %s",
    (project_id,)
)

# With SQLAlchemy (safe, readable)
tasks = db.query(Task).filter(Task.project_id == project_id).all()
```

---

### Alembic (Database Migrations)
**Chosen over:** Manual SQL scripts, Django migrations

**Why Alembic?**
1. **Version Control for Schema:** Track database changes in Git
2. **Automatic Detection:** Detects model changes, generates migrations
3. **Rollback Support:** Undo migrations if something breaks
4. **Team Collaboration:** Everyone applies same schema changes

**Critical For:**
- Production deployments (schema changes without downtime)
- Team development (prevent "works on my machine")

---

## Frontend Stack

### React 18 (UI Framework)
**Chosen over:** Vue, Svelte, Angular, Vanilla JS

**Why React?**
1. **Ecosystem:** Largest library of components and tools
2. **Community:** Most Stack Overflow answers, tutorials
3. **Job Market:** Most in-demand skill (if hiring, easiest to find devs)
4. **Stability:** Mature (10+ years), Facebook-backed
5. **Performance:** Virtual DOM, concurrent rendering

**Perfect For:**
- Interactive UIs (our task list with real-time updates)
- Component reusability (TaskItem, TaskForm, etc.)
- Large apps (scales from small to complex)

**Not Ideal For:**
- Static sites (use Next.js or Astro)
- Tiny projects (React adds overhead)

**Our Use Case:**
- Need interactive task list with complex state
- Want component reusability (DRY)
- Plan to grow features over time

---

### TypeScript (Type System)
**Chosen over:** JavaScript, Flow

**Why TypeScript?**
1. **Catches Bugs Early:** 15-20% of bugs caught at compile time
2. **Better IDE Support:** Autocomplete, refactoring, go-to-definition
3. **Self-Documenting:** Types serve as inline documentation
4. **Refactoring Safety:** Rename variables confidently
5. **Team Collaboration:** Explicit contracts between modules

**Real Example from Our Code:**
```typescript
// TypeScript caught this bug:
const task: Task = {
  title: "Buy milk",
  priority: "urgent"  // ❌ Error: "urgent" not assignable to "low" | "medium" | "high"
}

// JavaScript would silently fail:
const task = {
  title: "Buy milk",
  priority: "urgent"  // ✅ No error, bug reaches production
}
```

**Cost vs Benefit:**
- **Cost:** Slightly slower development (write types)
- **Benefit:** Faster debugging (fewer runtime errors)
- **Verdict:** Worth it for apps with 2+ developers or 500+ lines

---

### Vite (Build Tool)
**Chosen over:** Create React App (CRA), Webpack, Parcel

**Why Vite?**
1. **Blazing Fast:** 10-100x faster than CRA (native ES modules)
2. **Hot Module Replacement:** See changes instantly without refresh
3. **Modern:** Built for modern browsers, no legacy baggage
4. **Simple Config:** Works out of the box, minimal setup
5. **Future-Proof:** Industry moving from Webpack to Vite

**Performance Comparison:**
```
Cold Start (First Run):
- CRA: 30-40 seconds
- Vite: 1-2 seconds

Hot Reload (After Change):
- CRA: 2-3 seconds
- Vite: <50ms
```

**Decision Rationale:**
- Developer experience matters (faster = more productive)
- Modern tooling for modern JavaScript
- CRA is deprecated (Meta no longer maintains it)

---

### Tailwind CSS (Styling)
**Chosen over:** CSS Modules, styled-components, Sass

**Why Tailwind?**
1. **Utility-First:** Compose styles in JSX, no context switching
2. **Consistent Design:** Built-in design system (spacing, colors)
3. **No Name Fatigue:** No need to name classes (`btn-primary-large-blue`?)
4. **Tree-Shaking:** Only includes used styles (tiny production bundle)
5. **Rapid Prototyping:** Style without leaving JSX

**Example:**
```jsx
// Tailwind (fast, colocated)
<button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
  Delete
</button>

// CSS Modules (context switching)
<button className={styles.deleteButton}>Delete</button>
// In styles.module.css:
.deleteButton {
  background-color: #2563eb;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}
.deleteButton:hover {
  background-color: #1d4ed8;
}
```

**Trade-offs:**
- **Pro:** Faster development, consistent design
- **Con:** JSX looks "cluttered" (subjective)
- **Verdict:** Benefits outweigh aesthetic concerns

---

### React Router (Client-Side Routing)
**Chosen over:** Reach Router, Tanstack Router, custom solution

**Why React Router?**
1. **Industry Standard:** Most popular React routing library
2. **Shareable URLs:** `/project/3` can be bookmarked, shared
3. **Browser Navigation:** Back/forward buttons work correctly
4. **Nested Routes:** Easy to compose complex layouts
5. **Code Splitting:** Load routes on-demand (better performance)

**Our Use Case:**
```
/                 → All Tasks
/today            → Today's Tasks
/week             → This Week's Tasks
/overdue          → Overdue Tasks
/project/:id      → Tasks for specific project
/tag/:id          → Tasks with specific tag
```

**Why Not Single Page Without Router?**
- Can't share links ("Check out my project!")
- Back button doesn't work (frustrating UX)
- Can't use browser history
- Harder to track analytics (Google Analytics needs URLs)

---

### react-hot-toast (Notifications)
**Chosen over:** Custom solution, react-toastify, Material UI Snackbar

**Why react-hot-toast?**
1. **Lightweight:** ~10KB (vs 50KB+ for alternatives)
2. **Beautiful API:** Simple, declarative
3. **Customizable:** Full control over styling
4. **Promise Support:** `toast.promise()` for async operations
5. **Accessible:** ARIA labels, keyboard navigation

**Design Decision:**
- User feedback is critical ("Did my task save?")
- Browser alerts are jarring (block entire UI)
- Toasts are non-blocking, dismissible, professional

---

### Vitest + Testing Library (Testing)
**Chosen over:** Jest, Cypress, Playwright

**Why Vitest?**
1. **Vite Integration:** Same config, same transform pipeline
2. **Fast:** Parallel test execution, instant hot reload
3. **Jest-Compatible:** Drop-in replacement (same API)
4. **Modern:** Built for ES modules, TypeScript-first

**Why Testing Library?**
1. **User-Centric:** Test behavior, not implementation
2. **Maintainable:** Tests don't break when refactoring
3. **Best Practices:** Encourages accessible code (ARIA labels)

**Testing Philosophy:**
```typescript
// BAD: Testing implementation
expect(component.state.count).toBe(5)

// GOOD: Testing behavior
expect(screen.getByText('5 tasks')).toBeInTheDocument()
```

---

## Backend Architecture Decisions

### Service Layer Pattern
**Added in Phase 4**

**Why Add a Service Layer?**

**Problem Before:**
```python
# tasks.py router (doing too much)
@router.post("")
def create_task(task: TaskCreate, db: Session):
    # Validate project exists
    if task.project_id:
        project = db.query(Project).filter(...).first()
        if not project:
            raise HTTPException(404, "Project not found")
    
    # Validate tags exist
    for tag_id in task.tag_ids:
        tag = db.query(Tag).filter(...).first()
        if not tag:
            raise HTTPException(404, "Tag not found")
    
    # Create task
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    return db_task
```

**Issues:**
1. **Fat Controllers:** Router handles validation, business logic, data access
2. **Code Duplication:** Same validation in create, update endpoints
3. **Hard to Test:** Must mock HTTP requests to test logic
4. **Poor Separation:** Business logic mixed with HTTP concerns

**Solution: Service Layer**
```python
# services/task_service.py (business logic)
class TaskService:
    def create_task(self, task: TaskCreate) -> Task:
        self._validate_project(task.project_id)
        self._validate_tags(task.tag_ids)
        return self.db.add(Task(**task.dict()))

# routers/tasks.py (HTTP handling only)
@router.post("")
def create_task(task: TaskCreate, db: Session):
    service = TaskService(db)
    return service.create_task(task)
```

**Benefits:**
1. ✅ **Thin Controllers:** Routers just handle HTTP
2. ✅ **Reusable Logic:** Service methods called from anywhere
3. ✅ **Testable:** Test business logic without HTTP layer
4. ✅ **Clear Responsibility:** Each layer has one job

**When to Use Service Layer?**
- ✅ Complex validation logic
- ✅ Multi-step operations (create task + send notification)
- ✅ Business rules (pricing, permissions, workflows)

**When NOT to Use?**
- ❌ Simple CRUD (just use `crud.py`)
- ❌ Tiny apps (<5 endpoints)

---

### Pagination Strategy

**Why Paginate?**

**Problem:**
```python
# Without pagination
@router.get("")
def list_tasks(db: Session):
    return db.query(Task).all()  # Returns 10,000 tasks!
```

**Issues:**
1. **Slow Response:** 10,000 tasks = 5MB JSON = 2-3 second load
2. **Memory Pressure:** Server loads all tasks into RAM
3. **Poor UX:** User can't see 10,000 tasks anyway

**Solution:**
```python
@router.get("")
def list_tasks(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    tasks = db.query(Task).offset(skip).limit(page_size).all()
    total = db.query(Task).count()
    
    return {
        "items": tasks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
```

**Benefits:**
1. ✅ **Fast Responses:** 50 tasks = ~50KB = <100ms
2. ✅ **Scalable:** Works with 100 or 100,000 tasks
3. ✅ **Better UX:** Scroll to load more (infinite scroll)

**Configuration:**
```python
# config.py
class Settings(BaseSettings):
    default_page_size: int = 50
    max_page_size: int = 100  # Prevent abuse
```

---

### Exception Handling Strategy

**Why Custom Exceptions?**

**Problem Before:**
```python
# Inconsistent error handling
if not task:
    raise HTTPException(404, "Task not found")
if not project:
    raise HTTPException(404, "Project not found")
# Different messages, same pattern
```

**Solution:**
```python
# exceptions.py
class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id {id} not found")

# Usage
if not task:
    raise ResourceNotFoundError("Task", task_id)
```

**Benefits:**
1. ✅ **Consistent Messages:** Same format everywhere
2. ✅ **Centralized Logic:** Change error handling in one place
3. ✅ **Type Safety:** Can't forget error details
4. ✅ **Logging:** Catch and log all errors uniformly

---

## Frontend Architecture Decisions

### Component Hierarchy

**Design Principle:** Smart vs Dumb Components

```
App (Smart - manages global state)
├── Sidebar (Dumb - receives props)
│   ├── ProjectList (Dumb)
│   └── TagList (Dumb)
└── TasksView (Smart - manages task state)
    ├── TaskForm (Dumb - form UI)
    └── TaskItem (Dumb - single task UI)
```

**Smart Components (Containers):**
- Manage state
- Fetch data from API
- Handle business logic
- Pass data down via props

**Dumb Components (Presentational):**
- Receive data via props
- Render UI
- Emit events via callbacks
- No API calls, no state (except UI state like "is editing")

**Why This Pattern?**
1. **Testability:** Dumb components are pure functions (easy to test)
2. **Reusability:** Dumb components work in any context
3. **Maintainability:** Logic in one place (smart), UI in another (dumb)

**Example:**
```typescript
// TaskItem.tsx (Dumb)
interface TaskItemProps {
  task: Task;
  onUpdate: (id: number, update: TaskUpdate) => void;
  onDelete: (id: number) => void;
}

// TasksView.tsx (Smart)
function TasksView() {
  const [tasks, setTasks] = useState<Task[]>([]);
  
  const handleUpdate = async (id: number, update: TaskUpdate) => {
    await taskApi.update(id, update);
    await loadTasks();  // Refresh
  };
  
  return tasks.map(task => (
    <TaskItem task={task} onUpdate={handleUpdate} onDelete={handleDelete} />
  ));
}
```

---

### Optimistic UI Updates

**Why Optimistic Updates?**

**Problem (Pessimistic):**
```typescript
// User clicks checkbox
// → Send API request (200ms)
// → Wait for response
// → Update UI
// Total: 200ms delay (feels sluggish)
```

**Solution (Optimistic):**
```typescript
const handleToggleComplete = async () => {
  // 1. Update UI immediately
  task.is_completed = !task.is_completed;
  
  try {
    // 2. Send API request in background
    await taskApi.update(task.id, { is_completed: task.is_completed });
  } catch (err) {
    // 3. Revert on error
    task.is_completed = !task.is_completed;
    showError("Failed to update task");
  }
};
```

**Benefits:**
1. ✅ **Instant Feedback:** UI responds immediately
2. ✅ **Feels Fast:** Perceived performance >>  actual performance
3. ✅ **Error Handling:** Revert if API fails

**When to Use?**
- ✅ High-frequency actions (toggle checkbox)
- ✅ Low failure rate (<1%)
- ✅ Easy to revert (checkbox, star, like)

**When NOT to Use?**
- ❌ Critical actions (delete, purchase)
- ❌ High failure rate
- ❌ Hard to revert (file upload)

---

### State Management: Local vs Global

**Decision:** Use local state for most things, global only when necessary.

**Local State (useState):**
```typescript
// TasksView.tsx
const [tasks, setTasks] = useState<Task[]>([]);
const [loading, setLoading] = useState(false);
```

**Global State (React Context):**
```typescript
// App.tsx
const [projects, setProjects] = useState<Project[]>([]);
const [tags, setTags] = useState<Tag[]>([]);

// Pass to children via props
<TasksView projects={projects} tags={tags} />
```

**Why Not Redux/Zustand for Everything?**
1. **YAGNI Principle:** You Aren't Gonna Need It
2. **Complexity:** Global state adds indirection
3. **Performance:** Unnecessary re-renders
4. **Simplicity:** Easier to reason about

**When to Use Global State?**
- ✅ Shared across many components (projects, tags)
- ✅ Used in distant parts of tree (avoid prop drilling)
- ✅ Needs to persist across routes

**When to Use Local State?**
- ✅ Used in single component (task list)
- ✅ Temporary (form inputs, modal open/closed)
- ✅ Easy to fetch (just call API)

**Our Approach:**
- **Global:** Projects, Tags (used in sidebar + task form)
- **Local:** Tasks (each view fetches its own filtered tasks)

---

### API Service Layer (Frontend)

**Why Centralize API Calls?**

**Problem Before:**
```typescript
// TaskItem.tsx
await fetch('/api/tasks/1', { method: 'DELETE' });

// TaskForm.tsx
await fetch('/api/tasks', { method: 'POST', body: JSON.stringify(task) });

// Issues:
// - Repeated fetch logic
// - No error handling
// - Hard to add auth headers
// - Can't mock for testing
```

**Solution:**
```typescript
// services/api.ts
export const taskApi = {
  getAll: (filters) => fetch(`/api/tasks?${new URLSearchParams(filters)}`),
  create: (task) => fetch('/api/tasks', { method: 'POST', body: JSON.stringify(task) }),
  update: (id, update) => fetch(`/api/tasks/${id}`, { method: 'PATCH', ... }),
  delete: (id) => fetch(`/api/tasks/${id}`, { method: 'DELETE' }),
};

// Components
await taskApi.delete(task.id);  // Clean!
```

**Benefits:**
1. ✅ **DRY:** API logic in one place
2. ✅ **Type Safety:** TypeScript validates requests/responses
3. ✅ **Error Handling:** Centralized retry logic, error messages
4. ✅ **Testability:** Mock `taskApi` instead of `fetch`
5. ✅ **Future-Proof:** Easy to add authentication, caching, etc.

---

# File-by-File Reference

## Backend Structure

```
backend/
├── app/
│   ├── __init__.py              # Package marker
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration settings
│   ├── database.py              # Database connection & session
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── crud.py                  # Basic CRUD operations
│   ├── exceptions.py            # Custom exception classes
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── tasks.py             # Task endpoints
│   │   ├── projects.py          # Project endpoints
│   │   ├── tags.py              # Tag endpoints
│   │   └── ai.py                # AI parsing endpoints
│   └── services/
│       ├── __init__.py
│       ├── task_service.py      # Task business logic
│       └── ai_service.py        # AI parsing logic
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_tasks.py            # Task endpoint tests
│   ├── test_projects.py         # Project endpoint tests
│   └── test_ai.py               # AI service tests
├── alembic/
│   ├── versions/                # Migration files
│   └── env.py                   # Alembic configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Test configuration
└── env.example                  # Environment variables template
```

---

### Backend Files Explained

#### `main.py` - Application Entry Point
**Purpose:** Initialize FastAPI app, register routers, configure middleware.


**Why Separate?**
- Entry point should be minimal
- Easy to see app structure at a glance
- Can add multiple entry points (admin app, worker)

**Key Decisions:**
```python
app = FastAPI(
    title="Todo API",
    version="1.0.0",
    docs_url="/api/docs"  # Swagger UI at /api/docs
)

# CORS middleware (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers (keeps main.py clean)
app.include_router(tasks.router)
app.include_router(projects.router)
app.include_router(tags.router)
app.include_router(ai.router)
```

---

#### `config.py` - Configuration Management
**Purpose:** Centralize all configuration (env vars, constants).

**Why This File?**
- DRY: One place to change settings
- Type-safe: Pydantic validates config on startup
- Testable: Easy to override in tests
- Security: Secrets in env vars, not code

**Pattern:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://..."
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100
    
    # AI
    openai_api_key: str | None = None
    
    class Config:
        env_file = ".env"  # Load from .env file

settings = Settings()  # Singleton instance
```

**Usage:**
```python
from app.config import settings

page_size = min(requested_size, settings.max_page_size)
```

---

#### `database.py` - Database Connection
**Purpose:** Create database engine, session factory, base class.

**Why Separate?**
- Reusable: Every module imports from here
- Testable: Easy to swap with test database
- Dependency Injection: FastAPI `Depends(get_db)`

**Key Pattern:**
```python
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    """Dependency: Provides DB session, auto-closes after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

#### `models.py` - ORM Models (Database Schema)
**Purpose:** Define database tables using SQLAlchemy.

**Why ORM vs Raw SQL?**
- Type-safe: `task.project.name` instead of `row[5]`
- Relationships: Auto-joins (`task.tags`)
- Migrations: Alembic detects model changes
- Portable: Works with Postgres, MySQL, SQLite

**Design Decisions:**
```python
class Task(Base):
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Required fields (nullable=False)
    title = Column(String(200), nullable=False)
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.medium)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Optional fields (nullable=True)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Relationships (ORM magic)
    project = relationship("Project", back_populates="tasks")
    tags = relationship("Tag", secondary="task_tags", back_populates="tasks")
    
    # Timestamps (auto-managed)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Why These Fields?**
- `id`: Auto-incrementing primary key (standard)
- `title`: VARCHAR(200) prevents abuse (SQLite had no limit!)
- `priority`: Enum ensures valid values only
- `is_completed`: Boolean, not status enum (YAGNI)
- `description`: TEXT for unlimited length
- `due_date`: DATE not TIMESTAMP (no time zone confusion)
- `project_id`: Nullable (tasks can exist without project)
- Timestamps: Audit trail (when created/modified)

---

#### `schemas.py` - Pydantic Models (API Contracts)
**Purpose:** Define request/response shapes, validate data.

**Why Separate from Models?**
- **Separation of Concerns:** DB schema ≠ API shape
- **Security:** Don't expose DB internals (passwords, soft-deleted)
- **Flexibility:** API can evolve without DB changes

**Pattern:**
```python
# Base schema (shared fields)
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: Priority = "medium"
    due_date: str | None = None

# Create schema (what client sends)
class TaskCreate(TaskBase):
    project_id: int | None = None
    tag_ids: list[int] = []

# Update schema (partial update)
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Priority | None = None
    # ... (all optional)

# Response schema (what API returns)
class TaskResponse(TaskBase):
    id: int
    is_completed: bool
    project: ProjectResponse | None
    tags: list[TagResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Allow ORM models
```

**Why Three Schemas?**
1. **Create:** Client doesn't provide ID (auto-generated)
2. **Update:** All fields optional (partial update)
3. **Response:** Includes computed fields (project, tags)

---

#### `crud.py` - Data Access Layer
**Purpose:** Simple CRUD operations (Create, Read, Update, Delete).

**Why This File?**
- Reusable: Called from routers and services
- Testable: Easy to unit test (just needs mock DB)
- Separation: Business logic (services) separate from data access (CRUD)

**When to Use CRUD vs Service?**
- **CRUD:** Simple operations (get task by ID, delete task)
- **Service:** Complex operations (create task + validate project + send notification)

**Example:**
```python
def get_task(db: Session, task_id: int) -> Task | None:
    """Fetch single task by ID."""
    return db.query(Task).filter(Task.id == task_id).first()

def create_task(db: Session, task: TaskCreate) -> Task:
    """Create new task."""
    db_task = Task(**task.dict(exclude={"tag_ids"}))
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
```

---

#### `routers/tasks.py` - HTTP Endpoints
**Purpose:** Handle HTTP requests/responses for tasks.

**Why Routers?**
- **Separation:** HTTP concerns separate from business logic
- **Organization:** Each resource (tasks, projects, tags) has its own file
- **RESTful:** Standard patterns (`GET /tasks`, `POST /tasks`, etc.)

**Endpoint Design:**
```python
@router.get("", response_model=List[TaskResponse])
def list_tasks(
    # Query parameters (filters)
    completed: Optional[bool] = None,
    project_id: Optional[int] = None,
    # Pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    # Dependency injection
    db: Session = Depends(get_db)
):
    """List tasks with filtering and pagination."""
    service = TaskService(db)
    return service.get_tasks_filtered(...)
```

**HTTP Method Choices:**
- `GET /tasks` - List (safe, cacheable)
- `POST /tasks` - Create (not safe, not idempotent)
- `GET /tasks/{id}` - Fetch single (safe, cacheable)
- `PATCH /tasks/{id}` - Partial update (idempotent)
- `DELETE /tasks/{id}` - Delete (idempotent)

**Why PATCH not PUT?**
- PUT = full replacement (must send all fields)
- PATCH = partial update (send only changed fields)
- Our use case: User edits title, shouldn't have to send description

---

#### `services/task_service.py` - Business Logic
**Purpose:** Complex operations, validation, orchestration.

**Why Service Layer?**
- **Reusability:** Called from web, CLI, background jobs
- **Testability:** Test logic without HTTP layer
- **Complexity:** Multi-step operations need a home

**Example:**
```python
class TaskService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, task: TaskCreate) -> Task:
        """Create task with validation."""
        # Validate project exists
        if task.project_id:
            self._validate_project(task.project_id)
        
        # Validate tags exist
        for tag_id in task.tag_ids:
            self._validate_tag(tag_id)
        
        # Create task
        db_task = crud.create_task(self.db, task)
        
        # Could add: send notification, log event, etc.
        
        return db_task
    
    def _validate_project(self, project_id: int):
        """Helper: Ensure project exists."""
        project = crud.get_project(self.db, project_id)
        if not project:
            raise ResourceNotFoundError("Project", project_id)
```

**When to Add Service Method?**
- ✅ Validates multiple resources
- ✅ Calls multiple CRUD functions
- ✅ Has complex business rules
- ❌ Simple pass-through to CRUD

---

## Frontend Structure

```
frontend/
├── public/                      # Static assets
├── src/
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Root component (routing, global state)
│   ├── index.css                # Global styles
│   ├── types/
│   │   └── index.ts             # TypeScript type definitions
│   ├── services/
│   │   └── api.ts               # API client
│   ├── components/
│   │   ├── Sidebar.tsx          # Navigation sidebar
│   │   ├── TasksView.tsx        # Task list (smart component)
│   │   ├── TaskItem.tsx         # Single task (dumb component)
│   │   ├── TaskForm.tsx         # Task creation form
│   │   ├── TaskList.tsx         # Legacy (deprecated)
│   │   └── ToastProvider.tsx    # Toast notification config
│   ├── views/
│   │   ├── AllTasksView.tsx     # Route: /
│   │   ├── TodayView.tsx        # Route: /today
│   │   ├── WeekView.tsx         # Route: /week
│   │   ├── OverdueView.tsx      # Route: /overdue
│   │   ├── ProjectView.tsx      # Route: /project/:id
│   │   └── TagView.tsx          # Route: /tag/:id
│   ├── utils/
│   │   └── toast.tsx            # Toast utility functions
│   └── test/
│       └── setup.ts             # Test configuration
├── package.json                 # Dependencies
├── vite.config.ts               # Vite configuration
├── vitest.config.ts             # Test configuration
├── tailwind.config.js           # Tailwind CSS configuration
└── tsconfig.json                # TypeScript configuration
```

---

### Frontend Files Explained

#### `main.tsx` - React Entry Point
**Purpose:** Mount React app to DOM.

**Why Minimal?**
- Separation: App logic in `App.tsx`, mounting in `main.tsx`
- Providers: Wrap app with context providers (Toast, Router)

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import ToastProvider from './components/ToastProvider.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
    <ToastProvider />
  </React.StrictMode>,
)
```

**Key Decisions:**
- `StrictMode`: Catches bugs (double-renders in dev)
- `ToastProvider`: Global toast notifications
- Order matters: App first, ToastProvider second (overlay)

---

#### `App.tsx` - Root Component
**Purpose:** Routing, global state, layout structure.

**Why This Structure?**
```typescript
function App() {
  // Global state (shared across routes)
  const [projects, setProjects] = useState<Project[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  
  // Load on mount
  useEffect(() => {
    loadProjects();
    loadTags();
  }, []);
  
  return (
    <BrowserRouter>
      <div className="flex h-screen">
        {/* Sidebar: Visible on all routes */}
        <Sidebar projects={projects} tags={tags} />
        
        {/* Main content: Changes per route */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<AllTasksView />} />
            <Route path="/today" element={<TodayView />} />
            <Route path="/project/:id" element={<ProjectView />} />
            {/* ... */}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
```

**Design Decisions:**
- **Layout:** Flexbox (sidebar + main content)
- **Global State:** Projects/Tags (needed in sidebar + task form)
- **Routing:** Client-side (fast navigation, no page reload)

---

#### `types/index.ts` - Type Definitions
**Purpose:** Centralize TypeScript types for entire app.

**Why Separate File?**
- DRY: Single source of truth
- Imports: `import { Task } from '../types'`
- Safety: Rename `Priority` → `TaskPriority` in one place

**Pattern:**
```typescript
export type Priority = 'low' | 'medium' | 'high';

export interface Task {
  id: number;
  title: string;
  description?: string;
  priority: Priority;
  due_date?: string;
  is_completed: boolean;
  project_id?: number;
  project?: Project;
  tags: Tag[];
  created_at: string;
  updated_at: string;
}

export type TaskCreate = Omit<Task, 'id' | 'created_at' | 'updated_at' | 'project' | 'tags'> & {
  project_id?: number;
  tag_ids: number[];
};

export type TaskUpdate = Partial<TaskCreate>;
```

**Why Multiple Types?**
- `Task`: Full object (from API)
- `TaskCreate`: What we send to API (no ID, no timestamps)
- `TaskUpdate`: Partial update (all fields optional)

---

#### `services/api.ts` - API Client
**Purpose:** Centralize all API calls.

**Structure:**
```typescript
// Base URL
const API_BASE = 'http://localhost:8000';

// Helper: Handle response
async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.detail || `Request failed: ${response.status}`);
  }
  
  return data;
}

// Task API
export const taskApi = {
  getAll: (filters?: TaskFilters) => 
    fetch(`${API_BASE}/api/tasks?${new URLSearchParams(filters)`)
      .then(handleResponse),
  
  create: (task: TaskCreate) =>
    fetch(`${API_BASE}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    }).then(handleResponse),
  
  // ... update, delete, etc.
};

// Project API
export const projectApi = { /* ... */ };

// Tag API
export const tagApi = { /* ... */ };
```

**Benefits:**
1. ✅ DRY: Error handling in one place
2. ✅ Type-safe: TypeScript validates usage
3. ✅ Testable: Mock `taskApi` in tests
4. ✅ Future-proof: Easy to add auth, retry, caching

---

#### `components/TasksView.tsx` - Smart Component
**Purpose:** Fetch tasks, manage state, orchestrate child components.

**Why Smart Component?**
- Single Responsibility: Manages tasks for a specific view
- Reusable: Used by AllTasksView, TodayView, ProjectView, etc.
- Testable: Can test with mocked API

**Pattern:**
```typescript
interface TasksViewProps {
  title: string;
  filters: TaskFilters;
  projects: Project[];
  tags: Tag[];
  onTaskCreated: () => void;
}

export default function TasksView({ title, filters, projects, tags, onTaskCreated }: TasksViewProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  
  // Load tasks on mount and when filters change
  useEffect(() => {
    loadTasks();
  }, [filters, page]);
  
  const loadTasks = async () => {
    setLoading(true);
    const data = await taskApi.getAll({ ...filters, page });
    setTasks(data.items);
    setLoading(false);
  };
  
  const handleUpdateTask = async (id: number, update: TaskUpdate) => {
    await taskApi.update(id, update);
    await loadTasks();  // Refresh
    showSuccess('Task updated successfully');
  };
  
  return (
    <div>
      <h1>{title}</h1>
      <TaskForm onSubmit={handleTaskCreated} projects={projects} tags={tags} />
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={handleUpdateTask}
          onDelete={handleDeleteTask}
        />
      ))}
    </div>
  );
}
```

---

#### `components/TaskItem.tsx` - Dumb Component
**Purpose:** Display single task, emit events.

**Why Dumb?**
- Reusable: Works in any context (list, search, calendar)
- Testable: Pure function (props in, UI out)
- Simple: No API calls, no complex state

**Pattern:**
```typescript
interface TaskItemProps {
  task: Task;
  onUpdate: (id: number, update: TaskUpdate) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export default function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  
  const handleToggleComplete = async () => {
    // Optimistic update
    task.is_completed = !task.is_completed;
    
    try {
      await onUpdate(task.id, { is_completed: task.is_completed });
    } catch (err) {
      task.is_completed = !task.is_completed;  // Revert
      showError('Failed to update task');
    }
  };
  
  return (
    <div className="task-item">
      <input
        type="checkbox"
        checked={task.is_completed}
        onChange={handleToggleComplete}
      />
      <span>{task.title}</span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </div>
  );
}
```

**Key Decision: Optimistic Updates**
- UI updates instantly (feels fast)
- API call happens in background
- Revert if API fails
- Trade-off: Slightly complex code for better UX

---

#### `views/AllTasksView.tsx` - Route Component
**Purpose:** Configure TasksView for specific route.

**Why Separate Views?**
- Each route has different filters
- Easy to add route-specific features later
- Clear separation of routing vs. logic

**Pattern:**
```typescript
export default function AllTasksView({ projects, tags, onTaskCreated }) {
  return (
    <TasksView
      title="All Tasks"
      filters={{ view: 'all' }}
      projects={projects}
      tags={tags}
      onTaskCreated={onTaskCreated}
    />
  );
}

// TodayView.tsx
export default function TodayView({ projects, tags, onTaskCreated }) {
  return (
    <TasksView
      title="Today"
      filters={{ view: 'today' }}
      projects={projects}
      tags={tags}
      onTaskCreated={onTaskCreated}
    />
  );
}
```

**Benefits:**
- DRY: TasksView reused across routes
- Flexibility: Each view can customize further if needed
- Routing: Each view is a React Router route

---

#### `utils/toast.tsx` - Toast Utilities
**Purpose:** Reusable toast notification functions.

**Why Separate File?**
- DRY: Call `showSuccess()` instead of repeating toast config
- Consistency: All toasts look the same
- Testable: Mock toast utilities in tests

**API:**
```typescript
export const showSuccess = (message: string) => {
  toast.success(message, { duration: 4000 });
};

export const showError = (message: string) => {
  toast.error(message, { duration: 6000 });
};

export const showDeleteConfirm = (
  itemType: string,
  itemName: string,
  onConfirm: () => Promise<void>
) => {
  toast((t) => (
    <div>
      <p>Delete {itemType} "{itemName}"?</p>
      <button onClick={async () => {
        toast.dismiss(t.id);
        await onConfirm();
        showSuccess(`${itemType} deleted`);
      }}>
        Delete
      </button>
      <button onClick={() => toast.dismiss(t.id)}>
        Cancel
      </button>
    </div>
  ));
};
```

---

# Development Workflow

## Local Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd todo-fullstack

# 2. Start database
docker-compose up -d

# 3. Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 4. Setup frontend (new terminal)
cd frontend
npm install
npm run dev

# 5. Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/api/docs
```

---

## Git Workflow

**Branch Strategy:**
```
main           (production-ready code)
  ↳ develop    (integration branch)
      ↳ feature/add-recurring-tasks
      ↳ feature/mobile-app
      ↳ bugfix/priority-sort-issue
```

**Commit Messages:**
```
feat: add recurring tasks
fix: correct priority sorting logic
docs: update API documentation
refactor: extract service layer
test: add tests for task pagination
```

---

## Testing Strategy

### Backend Testing
```bash
cd backend
pytest -v                    # Run all tests
pytest tests/test_tasks.py   # Run specific file
pytest -v --cov              # With coverage
```

**Test Structure:**
- Unit tests: Test individual functions (CRUD, services)
- Integration tests: Test API endpoints (routes)
- Fixtures: Reusable test data (conftest.py)

### Frontend Testing
```bash
cd frontend
npm test                # Run tests
npm test:ui             # Interactive UI
npm test:coverage       # Coverage report
```

**Test Philosophy:**
- Test behavior, not implementation
- Test user interactions (click, type, submit)
- Mock API calls

---

# Performance Optimizations

## Backend Optimizations

### 1. Database Indexing
```python
# models.py
class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

**Why?**
- Faster queries on filtered fields
- `WHERE project_id = 5` uses index (O(log n) instead of O(n))

---

### 2. Eager Loading (N+1 Prevention)
```python
# BAD: N+1 queries
tasks = db.query(Task).all()  # 1 query
for task in tasks:
    print(task.project.name)   # N queries!

# GOOD: Eager load
tasks = db.query(Task).options(
    joinedload(Task.project),
    joinedload(Task.tags)
).all()  # 1 query!
```

---

### 3. Pagination
- Limit response size (50 tasks per page)
- Prevents memory exhaustion
- Faster response times

---

## Frontend Optimizations

### 1. React.memo (Prevent Re-renders)
```typescript
const TaskItem = React.memo(({ task, onUpdate, onDelete }) => {
  // Only re-renders if task, onUpdate, or onDelete changes
});
```

---

### 2. Optimistic Updates
- Update UI immediately
- Send API request in background
- Feels instant (no waiting for server)

---

### 3. Code Splitting (Future)
```typescript
const AdminPanel = lazy(() => import('./views/AdminPanel'));
// Only loads when user navigates to /admin
```

---

# Conclusion

This architecture document provides a comprehensive understanding of the todo application from product strategy to implementation details. Every decision—from choosing FastAPI to structuring the file system—was made with specific goals in mind:

1. **Scalability:** Can grow from 10 to 10,000 users
2. **Maintainability:** Easy for new developers to understand
3. **Performance:** Fast for users, efficient for servers
4. **Testability:** Comprehensive test coverage
5. **Developer Experience:** Fast dev cycle, good tooling

**Next Steps:**
- Add user authentication (Firebase, Auth0, or custom)
- Mobile app (React Native reuses 80% of frontend code)
- Real-time updates (WebSockets for multi-user editing)
- Offline support (Service Workers, local storage)

---

**Questions or Clarifications?**
This document is a living artifact. As the app evolves, so should this documentation.
