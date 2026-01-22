# Changelog

All notable changes to the Todo Full-Stack Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-22

### Initial Release - MVP

This is the first release of the Todo Full-Stack Application, providing a solid foundation for task management with modern web technologies.

### Added

#### Backend
- **FastAPI Framework**: RESTful API with automatic OpenAPI documentation
- **Database Models**:
  - Task model with title, description, priority, due date, completion status
  - Project model for organizing tasks
  - Tag model for flexible categorization
  - Many-to-many relationship between tasks and tags
- **CRUD Operations**: Full create, read, update, delete for all entities
- **Advanced Filtering**:
  - Filter by completion status, project, tags
  - Search in title and description
  - Sort by created date, due date, priority, title
- **Smart Views**:
  - Today: Tasks due today
  - This Week: Tasks due in next 7 days
  - Overdue: Past due incomplete tasks
  - All: All tasks
- **Database Migrations**: Alembic setup for schema versioning
- **Testing**: Comprehensive pytest suite with 15+ tests
- **Type Safety**: Full Pydantic validation on all endpoints
- **CORS Support**: Configured for frontend integration

#### Frontend
- **React 18 with TypeScript**: Modern, type-safe component architecture
- **Vite Build Tool**: Fast HMR and optimized production builds
- **Tailwind CSS**: Utility-first responsive design
- **Components**:
  - TaskForm: Create tasks with all fields
  - TaskItem: Display and edit individual tasks with inline editing
  - TaskList: Display tasks with comprehensive filtering UI
- **Features**:
  - Real-time task updates
  - Project and tag management
  - Smart view buttons (Today, This Week, Overdue, All)
  - Search functionality
  - Multiple filter options
  - Sort by various criteria
  - Priority color coding (Red=High, Yellow=Medium, Green=Low)
  - Overdue task highlighting
  - Empty states and loading indicators
  - Error handling with user-friendly messages
- **API Integration**: Type-safe API client with error handling

#### Infrastructure
- **Docker Compose**: PostgreSQL containerization for easy development
- **Environment Configuration**: `.env` files for backend and frontend
- **Documentation**:
  - Comprehensive README files for root, backend, and frontend
  - GETTING_STARTED guide for new developers
  - API documentation at `/docs` endpoint

#### Developer Experience
- **Code Quality**:
  - TypeScript for type safety
  - Python type hints throughout
  - Pydantic schemas for validation
  - Clean code structure following DRY principles
- **Testing**:
  - Backend test suite with pytest
  - Test fixtures and factories
  - Coverage reporting
- **Git**: `.gitignore` configured for Python and Node.js projects

### Technical Stack

**Backend:**
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- PostgreSQL 16
- Alembic 1.13.1
- Pydantic 2.5.3
- Pytest 7.4.4

**Frontend:**
- React 18.2.0
- TypeScript 5.2.2
- Vite 5.0.8
- Tailwind CSS 3.4.0

### API Endpoints

#### Tasks
- `GET /api/tasks` - List with filtering
- `POST /api/tasks` - Create
- `GET /api/tasks/{id}` - Get single
- `PATCH /api/tasks/{id}` - Update
- `DELETE /api/tasks/{id}` - Delete

#### Projects
- `GET /api/projects` - List all
- `POST /api/projects` - Create
- `GET /api/projects/{id}` - Get single
- `PATCH /api/projects/{id}` - Update
- `DELETE /api/projects/{id}` - Delete
- `GET /api/projects/{id}/tasks` - Get project tasks

#### Tags
- `GET /api/tags` - List all
- `POST /api/tags` - Create
- `GET /api/tags/{id}` - Get single
- `PATCH /api/tags/{id}` - Update
- `DELETE /api/tags/{id}` - Delete
- `GET /api/tags/{id}/tasks` - Get tag tasks

### Known Limitations

- **Single User**: No authentication or user management (planned for Phase 2)
- **No Subtasks**: Tasks cannot have subtasks yet (planned for Phase 2)
- **No Bulk Operations**: Cannot select and operate on multiple tasks at once (planned for Phase 2)
- **No Recurring Tasks**: Tasks cannot recur automatically (planned for Phase 2)
- **No File Attachments**: Cannot attach files to tasks (planned for Phase 2)
- **No Notifications**: No email or push notifications (planned for Phase 2)

### Future Roadmap (Phase 2)

Planned features for future releases:

**High Priority:**
- User authentication (JWT tokens)
- Subtasks/checklist items
- Bulk operations
- Drag-and-drop custom ordering
- Recurring tasks

**Medium Priority:**
- File attachments
- Reminders and notifications
- Calendar view
- Dark mode theme
- Task templates

**Nice to Have:**
- Task dependencies
- Time tracking
- Productivity analytics
- Mobile apps
- Browser extension
- Import/export functionality
- Offline support

### Deployment

Currently configured for local development. Production deployment considerations documented in backend README.

### Contributors

Initial development and architecture.

### License

MIT License

---

## Guidelines for Future Updates

### Version Numbering

- **MAJOR** (x.0.0): Breaking API changes, major feature overhauls
- **MINOR** (1.x.0): New features, backward-compatible
- **PATCH** (1.0.x): Bug fixes, small improvements

### Changelog Format

For each version:
1. **Added**: New features
2. **Changed**: Changes to existing functionality
3. **Deprecated**: Soon-to-be removed features
4. **Removed**: Removed features
5. **Fixed**: Bug fixes
6. **Security**: Security improvements

### Example Future Entry

```markdown
## [1.1.0] - YYYY-MM-DD

### Added
- User authentication with JWT tokens
- Login and registration endpoints
- Protected routes requiring authentication
- User-specific task filtering

### Changed
- Task model now includes user_id foreign key
- API endpoints now require authentication

### Fixed
- Task search now case-insensitive across all databases
- Tag color validation now properly accepts all hex formats
```
