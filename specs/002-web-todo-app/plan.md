# Implementation Plan: Phase II Web Application with Persistent Storage

**Branch**: `002-web-todo-app` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-web-todo-app/spec.md`

## Summary

Phase II transforms the Phase I console application into a full-stack web application with persistent storage, user authentication, and modern web interface. Users can register accounts, login securely, and manage their tasks through a responsive web UI. All task data persists in PostgreSQL database across sessions.

**Primary Requirement**: Multi-user web application with authentication and persistent task storage

**Technical Approach**:
- **Monorepo structure** with separate `backend/` (FastAPI + Python 3.13) and `frontend/` (Next.js 16+ + TypeScript)
- **Authentication** via Better Auth with JWT tokens in HTTP-only cookies
- **Database** using Neon PostgreSQL with SQLModel ORM and Alembic migrations
- **API** with 9 RESTful endpoints (3 auth + 6 task operations)
- **Deployment** to Vercel (frontend) and Railway/Render (backend)
- **Testing** with pytest (90%+ coverage) and optional Playwright E2E tests

---

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ with UV package manager
- Frontend: TypeScript 5+ (strict mode), Node.js 20+

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, Alembic, Better Auth, passlib (bcrypt), python-jose (JWT)
- Frontend: Next.js 16+ (App Router), React 19+, Tailwind CSS, Shadcn UI, Zustand

**Storage**: Neon Serverless PostgreSQL (production), PostgreSQL Docker container (development)

**Testing**:
- Backend: pytest, pytest-asyncio, pytest-cov (90%+ coverage requirement)
- Frontend: Jest, React Testing Library, Playwright (E2E)

**Target Platform**:
- Backend: Linux server (Docker container on Railway/Render)
- Frontend: Vercel Edge Network (serverless)
- Database: Neon PostgreSQL (serverless, multi-region)

**Project Type**: Web application (monorepo with backend + frontend)

**Performance Goals**:
- API response time: <500ms at p95 for CRUD operations
- Frontend load time: <2 seconds for initial page load
- Database queries: <100ms at p95
- Support 100 concurrent users without degradation

**Constraints**:
- JWT token expiry: 7 days maximum (constitution requirement)
- Password: bcrypt with cost factor 12
- Task title: 1-200 characters
- Task description: 0-1000 characters
- Pagination: 50 tasks per page (max 100)
- HTTP-only cookies for JWT (no localStorage)

**Scale/Scope**:
- Expected users: 100-10,000 in Phase II
- Tasks per user: 1-10,000 (typical: 10-100)
- Total tasks: 1,000-100,000
- API endpoints: 9 (3 auth + 6 task operations)
- Database tables: 2 (users, tasks)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase II Governance Requirements

- [x] **Next.js 16+ with App Router** (Frontend Standards) → Using Next.js 16+ with App Router, React Server Components
- [x] **FastAPI backend** (Python Standards) → Using FastAPI with async/await
- [x] **Neon PostgreSQL database** (Database Standards) → Using Neon PostgreSQL serverless
- [x] **Better Auth authentication** (Authentication requirement) → Using Better Auth with JWT tokens
- [x] **UV package manager** (Python Standards) → Using UV for backend dependency management
- [x] **TypeScript strict mode** (Frontend Standards) → TypeScript with strict: true in tsconfig
- [x] **SQLModel ORM** (Database Standards) → Using SQLModel for type-safe database models
- [x] **pytest with 90%+ coverage** (Testing Standards) → pytest with coverage requirement
- [x] **Stateless service architecture** (Pillar 8: Cloud-Native) → JWT tokens, no server-side sessions
- [x] **Type safety as contract** (Pillar 5) → Pydantic models, TypeScript strict mode
- [x] **Test-driven validation** (Pillar 6) → Tests defined before implementation
- [x] **Separate deployments** (Phase II Governance) → Vercel (frontend), Railway/Render (backend)
- [x] **RESTful API contracts** (Phase II Governance) → OpenAPI 3.1 specification

### Code Quality Standards

- [x] **Type hints on all Python functions** → SQLModel and Pydantic provide type safety
- [x] **No `any` types in TypeScript** → strict mode enforces this
- [x] **Pydantic validation** → All request/response models use Pydantic
- [x] **Docstrings (Google style)** → Required for all public functions
- [x] **Black formatter + Ruff linter** (Python) → Configured in pyproject.toml
- [x] **Prettier + ESLint** (TypeScript) → Configured in frontend

### Security Standards

- [x] **Password hashing with bcrypt** → passlib[bcrypt] with cost factor 12
- [x] **JWT tokens in HTTP-only cookies** → Better Auth configuration
- [x] **CSRF protection** → SameSite=Strict cookies
- [x] **User isolation enforced** → All queries filter by user_id
- [x] **No secrets in code/version control** → .env files (gitignored)

### Database Standards

- [x] **Foreign key constraints** → tasks.user_id references users.id with CASCADE
- [x] **Indexes on frequently queried columns** → Indexed on email, user_id, (user_id, created_at)
- [x] **Timestamps on all tables** → created_at, updated_at fields
- [x] **Migrations tracked and versioned** → Alembic for schema management

**Status**: ✅ All constitution requirements satisfied, no violations

---

## Project Structure

### Documentation (this feature)

```text
specs/002-web-todo-app/
├── spec.md              # Feature specification (5 user stories, 20 requirements)
├── plan.md              # This file (implementation architecture)
├── research.md          # Technology decisions and rationale
├── data-model.md        # Entity definitions (User, Task)
├── quickstart.md        # Setup and development guide
├── contracts/           # API contracts
│   ├── openapi.yaml     # OpenAPI 3.1 specification
│   └── API-ENDPOINTS.md # Endpoint reference guide
├── checklists/
│   └── requirements.md  # Specification quality checklist (16/16 passed)
└── tasks.md             # Task breakdown (generated by /sp.tasks command)
```

### Source Code (repository root)

**Monorepo structure** with separate backend and frontend:

```text
todoAppr/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Configuration (env vars, settings)
│   │   ├── db.py                # Database connection and session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User SQLModel (id, email, password_hash, created_at)
│   │   │   └── task.py          # Task SQLModel (id, user_id, title, description, completed, timestamps)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Authentication logic (register, login, JWT)
│   │   │   └── task_service.py  # Task CRUD business logic
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependency injection (get_db, get_current_user)
│   │   │   ├── auth.py          # Auth endpoints (register, login, logout)
│   │   │   └── tasks.py         # Task endpoints (CRUD + toggle completion)
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── auth_middleware.py  # JWT validation middleware
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures (test DB, test client)
│   │   ├── unit/
│   │   │   ├── test_user_model.py
│   │   │   ├── test_task_model.py
│   │   │   ├── test_auth_service.py
│   │   │   └── test_task_service.py
│   │   └── integration/
│   │       ├── test_auth_api.py    # Auth endpoint integration tests
│   │       ├── test_tasks_api.py   # Task endpoint integration tests
│   │       └── test_full_workflow.py  # End-to-end API workflow
│   ├── alembic/
│   │   ├── versions/            # Database migration files
│   │   │   └── 001_initial_schema.py
│   │   ├── env.py               # Alembic environment configuration
│   │   └── script.py.mako       # Migration template
│   ├── alembic.ini              # Alembic configuration
│   ├── pyproject.toml           # UV dependencies and project metadata
│   ├── .env                     # Environment variables (gitignored)
│   ├── .env.example             # Example environment variables
│   └── README.md                # Backend setup instructions
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout with auth provider
│   │   │   ├── page.tsx         # Landing/login page (Server Component)
│   │   │   ├── register/
│   │   │   │   └── page.tsx     # Registration page
│   │   │   ├── dashboard/
│   │   │   │   ├── layout.tsx   # Dashboard layout with nav
│   │   │   │   └── page.tsx     # Task list page (Server Component)
│   │   │   └── globals.css      # Global styles (Tailwind)
│   │   ├── components/
│   │   │   ├── ui/              # Shadcn UI components (Button, Input, Card, Dialog, etc.)
│   │   │   ├── TaskList.tsx     # Task list display (Client Component)
│   │   │   ├── TaskForm.tsx     # Task creation/edit form (Client Component)
│   │   │   ├── TaskItem.tsx     # Single task card (Client Component)
│   │   │   └── AuthForm.tsx     # Login/register form (Client Component)
│   │   ├── lib/
│   │   │   ├── api.ts           # API client (fetch wrapper with credentials)
│   │   │   ├── auth.ts          # Better Auth client setup
│   │   │   ├── types.ts         # TypeScript types (User, Task, API responses)
│   │   │   └── utils.ts         # Utility functions (cn, formatDate, etc.)
│   │   └── hooks/
│   │       ├── useTasks.ts      # Task data fetching and mutations
│   │       └── useAuth.ts       # Authentication state and actions
│   ├── public/
│   │   └── favicon.ico
│   ├── tests/
│   │   ├── components/
│   │   │   ├── TaskList.test.tsx
│   │   │   └── TaskForm.test.tsx
│   │   └── e2e/
│   │       ├── auth.spec.ts     # E2E auth flow (register, login, logout)
│   │       └── tasks.spec.ts    # E2E task CRUD workflow
│   ├── package.json             # npm dependencies
│   ├── tsconfig.json            # TypeScript configuration (strict mode)
│   ├── tailwind.config.ts       # Tailwind CSS configuration
│   ├── next.config.js           # Next.js configuration
│   ├── .env.local               # Environment variables (gitignored)
│   ├── .env.example             # Example environment variables
│   └── README.md                # Frontend setup instructions
│
├── docker-compose.yml           # Local PostgreSQL for development
├── .gitignore                   # Git ignore (includes .env files)
└── README.md                    # Project overview and quickstart
```

**Structure Decision**:
- **Option 2 (Web application)** selected due to separate frontend and backend requirements
- Monorepo simplifies type sharing (generate TypeScript types from OpenAPI schema)
- Clear separation of concerns: backend handles auth/data/business logic, frontend handles UI/UX
- Each application has independent tests, dependencies, and deployment pipeline
- Shared documentation in `specs/002-web-todo-app/` directory

---

## Complexity Tracking

No constitution violations detected. All requirements satisfied:
- ✅ Monorepo structure (not explicitly forbidden, aligns with Phase II governance)
- ✅ Separate deployments (Vercel + Railway/Render as mandated)
- ✅ All approved technologies used (FastAPI, Next.js 16+, Neon PostgreSQL, Better Auth)
- ✅ Type safety enforced (SQLModel + Pydantic + TypeScript strict)
- ✅ Stateless architecture (JWT tokens, no server sessions)

**Complexity Justifications**: None required - design follows constitutional principles.

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Next.js 16+ Frontend (Vercel)             │   │
│  │  - React Server Components + Client Components       │   │
│  │  - Tailwind CSS + Shadcn UI                          │   │
│  │  - Better Auth Client SDK                            │   │
│  └───────────────────────┬──────────────────────────────┘   │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTPS (credentials: include)
                             │ JWT in HTTP-only cookie
                             ▼
┌─────────────────────────────────────────────────────────────┐
│        FastAPI Backend (Railway/Render, Docker)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Auth Middleware (JWT validation)                    │   │
│  └───────────────────────┬──────────────────────────────┘   │
│  ┌───────────────────────┴──────────────────────────────┐   │
│  │  API Endpoints (9 routes)                            │   │
│  │  - POST /api/auth/register                           │   │
│  │  - POST /api/auth/login                              │   │
│  │  - POST /api/auth/logout                             │   │
│  │  - GET /api/tasks (paginated)                        │   │
│  │  - POST /api/tasks                                   │   │
│  │  - GET /api/tasks/{id}                               │   │
│  │  - PUT /api/tasks/{id}                               │   │
│  │  - PATCH /api/tasks/{id}/complete                    │   │
│  │  - DELETE /api/tasks/{id}                            │   │
│  └───────────────────────┬──────────────────────────────┘   │
│  ┌───────────────────────┴──────────────────────────────┐   │
│  │  Services Layer (Business Logic)                     │   │
│  │  - auth_service: register, login, hash passwords     │   │
│  │  - task_service: CRUD operations with user isolation │   │
│  └───────────────────────┬──────────────────────────────┘   │
│  ┌───────────────────────┴──────────────────────────────┐   │
│  │  SQLModel ORM (Type-safe models)                     │   │
│  │  - User model                                        │   │
│  │  - Task model                                        │   │
│  └───────────────────────┬──────────────────────────────┘   │
└────────────────────────────┼────────────────────────────────┘
                             │ PostgreSQL protocol (asyncpg)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│         Neon PostgreSQL (Serverless Database)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tables:                                             │   │
│  │  - users (id, email, password_hash, created_at)      │   │
│  │  - tasks (id, user_id, title, description,           │   │
│  │           completed, created_at, updated_at)         │   │
│  │  Foreign Key: tasks.user_id → users.id (CASCADE)     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Authentication Flow

```
User Registration:
1. User submits email + password → POST /api/auth/register
2. Backend validates email (unique check)
3. Backend hashes password (bcrypt, cost=12)
4. Backend creates user record in database
5. Backend generates JWT token (user_id, email, exp)
6. Backend sets JWT in HTTP-only cookie (Max-Age=604800)
7. Backend returns user data (id, email, created_at)
8. Frontend stores user state, redirects to dashboard

User Login:
1. User submits email + password → POST /api/auth/login
2. Backend queries user by email
3. Backend verifies password (bcrypt compare)
4. Backend generates JWT token
5. Backend sets JWT in HTTP-only cookie
6. Backend returns user data
7. Frontend stores user state, redirects to dashboard

Authenticated Request:
1. Frontend makes API request (browser sends cookie automatically)
2. Backend auth middleware extracts JWT from cookie
3. Backend validates JWT signature and expiration
4. Backend extracts user_id from payload
5. Backend attaches user to request context
6. Endpoint handler uses user_id to filter user's data
7. Backend returns user-specific data

User Logout:
1. User clicks logout → POST /api/auth/logout
2. Backend sets cookie with Max-Age=0 (clears cookie)
3. Frontend clears user state, redirects to login
```

### Data Flow for Task Operations

**Create Task**:
```
User Input (form) → Frontend validation (Zod schema)
  → POST /api/tasks {title, description}
  → Backend auth middleware (extract user_id from JWT)
  → task_service.create_task(user_id, title, description)
  → SQLModel insert → PostgreSQL
  → Return Task object
  → Frontend updates UI (optimistic or refetch)
```

**List Tasks (Paginated)**:
```
Page load → GET /api/tasks?page=1&limit=50
  → Backend auth middleware (extract user_id)
  → task_service.get_tasks(user_id, page, limit)
  → SQLModel query with WHERE user_id = :user_id
  → PostgreSQL returns tasks
  → Backend calculates pagination metadata (total, pages)
  → Return {items, page, limit, total, pages}
  → Frontend renders TaskList component
```

**Toggle Completion**:
```
User clicks complete button → PATCH /api/tasks/{id}/complete
  → Backend auth middleware (extract user_id)
  → task_service.toggle_completion(task_id, user_id)
  → SQLModel query: WHERE id = :task_id AND user_id = :user_id
  → Update task.completed = !task.completed
  → Update task.updated_at = now()
  → SQLModel commit → PostgreSQL
  → Return updated Task object
  → Frontend updates UI (optimistic update or refetch)
```

---

## API Design

### Endpoint Summary

| Method | Endpoint | Auth | Description | Success Code |
|--------|----------|------|-------------|--------------|
| POST | `/api/auth/register` | No | Register new user | 201 Created |
| POST | `/api/auth/login` | No | User login | 200 OK |
| POST | `/api/auth/logout` | Yes | User logout | 200 OK |
| GET | `/api/tasks` | Yes | List tasks (paginated) | 200 OK |
| POST | `/api/tasks` | Yes | Create task | 201 Created |
| GET | `/api/tasks/{id}` | Yes | Get single task | 200 OK |
| PUT | `/api/tasks/{id}` | Yes | Update task | 200 OK |
| PATCH | `/api/tasks/{id}/complete` | Yes | Toggle completion | 200 OK |
| DELETE | `/api/tasks/{id}` | Yes | Delete task | 200 OK |
| GET | `/health` | No | Health check | 200 OK |

**Total**: 10 endpoints (3 auth + 6 task + 1 health)

### Request/Response Formats

All requests and responses use `application/json` content type.

**Authentication**: JWT token in `cookie` header (HTTP-only, Secure, SameSite=Strict)

**Error Format** (consistent across all endpoints):
```json
{
  "detail": "Human-readable error message",
  "field": "field_name"
}
```

### Complete OpenAPI Specification

See `contracts/openapi.yaml` for full OpenAPI 3.1 specification with:
- All endpoint definitions
- Request/response schemas
- Validation rules
- Error responses
- Examples

---

## Database Schema

### Tables

**users**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
```

**tasks**:
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000) NOT NULL DEFAULT '',
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);
```

### Relationships

- **users** 1:N **tasks** (one user has many tasks)
- Foreign key constraint: `tasks.user_id REFERENCES users.id`
- Delete cascade: When user deleted, all their tasks are deleted

### Migrations

- **Tool**: Alembic (SQLAlchemy migration tool)
- **Strategy**: Auto-generate from SQLModel changes, review before applying
- **Initial migration**: `001_initial_schema.py` creates users and tasks tables

---

## Testing Strategy

### Backend Testing (pytest)

**Unit Tests** (tests/unit/):
- `test_user_model.py`: User model validation, email uniqueness
- `test_task_model.py`: Task model validation, title/description length
- `test_auth_service.py`: Password hashing, JWT generation, user registration
- `test_task_service.py`: CRUD operations, user isolation

**Integration Tests** (tests/integration/):
- `test_auth_api.py`: Register, login, logout endpoints with real database
- `test_tasks_api.py`: Task CRUD endpoints with authentication
- `test_full_workflow.py`: Complete user journey (register → create tasks → update → delete)

**Coverage Requirement**: 90%+ for models and services (per constitution)

**Test Database**: PostgreSQL Docker container or in-memory SQLite for unit tests

### Frontend Testing (optional in Phase II)

**Component Tests** (Jest + React Testing Library):
- TaskList component rendering
- TaskForm validation and submission
- TaskItem interactions (complete, edit, delete)

**E2E Tests** (Playwright):
- Full authentication flow
- Complete task management workflow
- Error handling and edge cases

---

## Deployment Strategy

### Development Environment

**Backend**:
```bash
cd backend
uv sync --extra dev
uv run uvicorn src.main:app --reload
# Running at http://localhost:8000
```

**Frontend**:
```bash
cd frontend
pnpm install
pnpm dev
# Running at http://localhost:3000
```

**Database**:
```bash
docker-compose up -d postgres
# PostgreSQL at localhost:5432
```

### Production Deployment

**Database** (Neon PostgreSQL):
- Create project at neon.tech
- Get connection string: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/db?sslmode=require`
- Set as `DATABASE_URL` in backend environment

**Backend** (Railway or Render):
- Connect GitHub repository
- Set root directory: `backend/`
- Build command: `uv sync`
- Start command: `uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- Environment variables: `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `FRONTEND_URL`
- Run migrations: `uv run alembic upgrade head` (via startup script or CLI)

**Frontend** (Vercel):
- Import GitHub repository
- Set root directory: `frontend/`
- Framework preset: Next.js
- Build command: `pnpm build`
- Environment variable: `NEXT_PUBLIC_API_URL` (backend URL from Railway/Render)
- Auto-deploy on push to main branch

---

## Security Considerations

### Authentication Security

- **Password Hashing**: bcrypt with cost factor 12 (balance security and performance)
- **JWT Tokens**: HTTP-only cookies prevent XSS attacks
- **Token Expiry**: 7 days maximum (per constitution)
- **CSRF Protection**: SameSite=Strict cookies prevent cross-site request forgery

### Authorization

- **User Isolation**: All database queries filter by `user_id`
- **Endpoint Protection**: Auth middleware validates JWT on all protected routes
- **Ownership Verification**: Task endpoints verify task belongs to current user

### Input Validation

- **API Layer**: Pydantic models validate all inputs
- **Database Layer**: Constraints enforce data integrity
- **Frontend Layer**: Zod schemas validate before submission

### Secrets Management

- **Environment Variables**: All secrets in `.env` files (gitignored)
- **JWT Secret**: Generated with `secrets.token_urlsafe(32)`
- **Database Credentials**: Never committed to repository
- **Production**: Use platform-provided secret management (Vercel Secrets, Railway Variables)

---

## Performance Optimization

### Database Optimization

- **Indexes**: Primary keys, unique email, foreign keys, composite (user_id, created_at)
- **Pagination**: Limit query results to 50 items per page
- **Connection Pooling**: SQLAlchemy engine with pool size 5-10
- **Query Optimization**: Use `select()` instead of `session.query()` for async support

### Frontend Optimization

- **Server Components**: Reduce JavaScript bundle size, server-side rendering
- **Code Splitting**: Automatic with Next.js App Router
- **Image Optimization**: Next.js `<Image>` component (if needed for future phases)
- **Caching**: Server Component caching, API route caching

### API Optimization

- **Async/Await**: All database operations use async functions
- **Response Compression**: Gzip compression via FastAPI middleware
- **CORS**: Configured for specific origin (not wildcard)

---

## Migration from Phase I

### Data Migration

**Phase I → Phase II**:
- Phase I has no persistent data (in-memory only)
- No data migration required
- Fresh database start with user registration

**Optional**: Export Phase I in-memory tasks to JSON, import into Phase II after user creation

---

## Next Steps

1. **Run `/sp.tasks` command** to generate task breakdown from this plan
2. **Review tasks.md** for implementation order and test cases
3. **Execute `/sp.implement`** to begin Red-Green-Refactor TDD cycle
4. **Validate** against spec acceptance criteria and success criteria

---

## References

- **Specification**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **API Contracts**: [contracts/openapi.yaml](./contracts/openapi.yaml), [contracts/API-ENDPOINTS.md](./contracts/API-ENDPOINTS.md)
- **Quickstart Guide**: [quickstart.md](./quickstart.md)
- **Constitution**: [../../.specify/memory/constitution.md](../../.specify/memory/constitution.md)

---

**Version**: 2.0.0
**Status**: Complete and ready for `/sp.tasks` phase
**Last Updated**: 2026-01-12
