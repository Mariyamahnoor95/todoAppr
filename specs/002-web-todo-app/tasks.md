# Tasks: Phase II Web Application with Persistent Storage

**Input**: Design documents from `/specs/002-web-todo-app/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Following Test-Driven Development (TDD) as mandated by constitution Pillar 6. All test tasks follow Red-Green-Refactor cycle.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

**Monorepo structure** (from plan.md):
- Backend: `backend/src/`, `backend/tests/`
- Frontend: `frontend/src/`, `frontend/tests/`
- Database: PostgreSQL via Alembic migrations in `backend/alembic/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and monorepo structure

- [x] T001 Create monorepo directory structure (backend/, frontend/, docker-compose.yml)
- [x] T002 [P] Initialize backend Python project with pyproject.toml (UV, FastAPI, SQLModel, Alembic, pytest dependencies)
- [x] T003 [P] Initialize frontend Next.js project with package.json (Next.js 16+, TypeScript, Tailwind, Shadcn UI, pnpm)
- [x] T004 [P] Create backend/.env.example with DATABASE_URL, JWT_SECRET, CORS_ORIGINS, FRONTEND_URL
- [x] T005 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL
- [x] T006 [P] Create docker-compose.yml for local PostgreSQL development database
- [x] T007 [P] Configure backend linting (Ruff) and formatting (Black) in pyproject.toml
- [x] T008 [P] Configure frontend linting (ESLint) and formatting (Prettier) in frontend/
- [x] T009 [P] Create backend/.gitignore (exclude .env, __pycache__, .pytest_cache, htmlcov/)
- [x] T010 [P] Create frontend/.gitignore (exclude .env.local, .next/, node_modules/)
- [x] T011 Update root .gitignore for monorepo patterns

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T012 Create backend/src/config.py for environment variable configuration (load from .env)
- [x] T013 Create backend/src/db.py for SQLAlchemy engine and session management (async engine)
- [x] T014 Initialize Alembic in backend/alembic/ with env.py configuration for SQLModel
- [x] T015 Create backend/src/main.py with FastAPI app initialization, CORS middleware, health endpoint
- [x] T016 [P] Create backend/src/middleware/__init__.py
- [x] T017 [P] Create backend/src/models/__init__.py
- [x] T018 [P] Create backend/src/services/__init__.py
- [x] T019 [P] Create backend/src/api/__init__.py
- [x] T020 Create backend/src/api/deps.py for dependency injection (get_db, get_current_user stubs)
- [x] T021 [P] Create backend/tests/conftest.py with pytest fixtures (test database, test client, async session)

### Frontend Foundation

- [x] T022 Create frontend/src/app/layout.tsx as root layout with metadata
- [x] T023 Create frontend/src/app/globals.css with Tailwind directives
- [x] T024 Configure frontend/tailwind.config.ts with Shadcn UI theme
- [x] T025 Create frontend/src/lib/utils.ts with cn() utility for className merging
- [x] T026 Create frontend/src/lib/store.ts with Zustand stores for auth and task state
- [x] T027 Create frontend/src/lib/api.ts with base API client (fetch wrapper with credentials: 'include')
- [x] T028 [P] Create Shadcn UI components (Button, Input) in frontend/src/components/ui/

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration & Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to register accounts, login securely with JWT tokens in HTTP-only cookies, and logout

**Independent Test**: Create account → login → access protected route → logout → verify session cleared

### Unit Tests for User Story 1 (Red Phase - Write FIRST, ensure they FAIL)

- [x] T029 [P] [US1] Write unit test for User model validation (email format, password hash) in backend/tests/unit/test_user_model.py
- [x] T030 [P] [US1] Write unit test for AuthService.register (happy path + duplicate email) in backend/tests/unit/test_auth_service.py
- [x] T031 [P] [US1] Write unit test for AuthService.login (valid credentials + invalid) in backend/tests/unit/test_auth_service.py
- [x] T032 [P] [US1] Write unit test for JWT token generation and validation in backend/tests/unit/test_auth_service.py

### Implementation for User Story 1 (Green Phase - Make tests PASS)

- [x] T033 [US1] Create User SQLModel in backend/src/models/user.py (id, email unique, password_hash, created_at)
- [x] T034 [US1] Generate Alembic migration for users table in backend/alembic/versions/001_create_users_table.py
- [x] T035 [US1] Apply migration: `uv run alembic upgrade head` to create users table in database
- [x] T036 [US1] Implement AuthService in backend/src/services/auth_service.py (register, login, hash_password, verify_password, create_jwt_token, verify_jwt_token)
- [x] T037 [US1] Implement POST /api/auth/register endpoint in backend/src/api/auth.py (calls AuthService.register, returns user + sets JWT cookie)
- [x] T038 [US1] Implement POST /api/auth/login endpoint in backend/src/api/auth.py (calls AuthService.login, returns user + sets JWT cookie)
- [x] T039 [US1] Implement POST /api/auth/logout endpoint in backend/src/api/auth.py (clears JWT cookie with Max-Age=0)
- [x] T040 [US1] Implement JWT validation middleware in backend/src/middleware/auth_middleware.py (extracts user_id from cookie)
- [x] T041 [US1] Update backend/src/api/deps.py with get_current_user dependency (uses auth_middleware)
- [x] T042 [US1] Register auth routes in backend/src/main.py

### Integration Tests for User Story 1 (Validate End-to-End)

- [ ] T043 [US1] Write integration test for register → login → logout flow in backend/tests/integration/test_auth_api.py
- [ ] T044 [US1] Write integration test for duplicate email registration error in backend/tests/integration/test_auth_api.py
- [ ] T045 [US1] Write integration test for invalid login credentials in backend/tests/integration/test_auth_api.py
- [ ] T046 [US1] Write integration test for protected route access without authentication in backend/tests/integration/test_auth_api.py

### Frontend for User Story 1

- [x] T047 [P] [US1] Create frontend/src/app/page.tsx as login page (Server Component with login form)
- [x] T048 [P] [US1] Create frontend/src/app/register/page.tsx as registration page
- [x] T049 [US1] Implement auth API methods in frontend/src/lib/api.ts (register, login, logout)
- [x] T050 [US1] Create frontend/src/components/AuthForm.tsx as reusable login/register form (Client Component)
- [x] T051 [US1] Create frontend/src/hooks/useAuth.ts for authentication state management
- [x] T052 [US1] Update frontend/src/app/layout.tsx to include auth provider context

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and logout with JWT cookies

---

## Phase 4: User Story 2 - View Tasks in Web Interface (Priority: P2)

**Goal**: Authenticated users can view all their tasks in a modern web interface with status indicators

**Independent Test**: Login → view empty task list → create tasks via backend/database → refresh → see tasks displayed

### Unit Tests for User Story 2 (Red Phase)

- [ ] T053 [P] [US2] Write unit test for Task model validation (title 1-200 chars, description 0-1000 chars) in backend/tests/unit/test_task_model.py
- [ ] T054 [P] [US2] Write unit test for Task model foreign key relationship with User in backend/tests/unit/test_task_model.py
- [ ] T055 [P] [US2] Write unit test for TaskService.get_tasks with user isolation in backend/tests/unit/test_task_service.py
- [ ] T056 [P] [US2] Write unit test for TaskService.get_tasks pagination in backend/tests/unit/test_task_service.py

### Implementation for User Story 2 (Green Phase)

- [x] T057 [US2] Create Task SQLModel in backend/src/models/task.py (id, user_id FK, title, description, completed, created_at, updated_at)
- [x] T058 [US2] Generate Alembic migration for tasks table in backend/alembic/versions/002_create_tasks_table.py
- [x] T059 [US2] Apply migration: `uv run alembic upgrade head` to create tasks table with foreign key to users
- [x] T060 [US2] Implement TaskService.get_tasks in backend/src/services/task_service.py (fetch tasks for user_id with pagination)
- [x] T061 [US2] Implement TaskService.get_task_by_id in backend/src/services/task_service.py (fetch single task with user ownership check)
- [x] T062 [US2] Implement GET /api/tasks endpoint in backend/src/api/tasks.py (returns paginated task list for current user)
- [x] T063 [US2] Implement GET /api/tasks/{id} endpoint in backend/src/api/tasks.py (returns single task if owned by user)
- [x] T064 [US2] Register task routes in backend/src/main.py

### Integration Tests for User Story 2

- [ ] T065 [US2] Write integration test for GET /api/tasks with empty list in backend/tests/integration/test_tasks_api.py
- [ ] T066 [US2] Write integration test for GET /api/tasks with user isolation (User A cannot see User B's tasks) in backend/tests/integration/test_tasks_api.py
- [ ] T067 [US2] Write integration test for GET /api/tasks pagination in backend/tests/integration/test_tasks_api.py
- [ ] T068 [US2] Write integration test for GET /api/tasks/{id} with 404 for non-existent task in backend/tests/integration/test_tasks_api.py

### Frontend for User Story 2

- [x] T069 [US2] Create frontend/src/app/dashboard/layout.tsx for authenticated dashboard layout
- [x] T070 [US2] Create frontend/src/app/dashboard/page.tsx for task list page (Server Component fetches tasks)
- [x] T071 [US2] Implement task API methods in frontend/src/lib/api.ts (listTasks with pagination)
- [x] T072 [P] [US2] Create frontend/src/components/TaskList.tsx to display tasks (Client Component)
- [x] T073 [P] [US2] Create frontend/src/components/TaskItem.tsx for single task card with status indicator
- [x] T074 [US2] Create frontend/src/hooks/useTasks.ts for task data fetching and state management

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can login and view their tasks

---

## Phase 5: User Story 3 - Add Tasks via Web Interface (Priority: P3)

**Goal**: Authenticated users can create new tasks with title and optional description through web form

**Independent Test**: Login → open task form → submit valid task → see task in list → submit invalid task → see validation error

### Unit Tests for User Story 3 (Red Phase)

- [ ] T075 [P] [US3] Write unit test for TaskService.create_task (happy path) in backend/tests/unit/test_task_service.py
- [ ] T076 [P] [US3] Write unit test for TaskService.create_task with validation errors (empty title, title too long) in backend/tests/unit/test_task_service.py
- [ ] T077 [P] [US3] Write unit test for TaskService.create_task with description validation in backend/tests/unit/test_task_service.py

### Implementation for User Story 3 (Green Phase)

- [x] T078 [US3] Implement TaskService.create_task in backend/src/services/task_service.py (create task with user_id, validate title/description)
- [x] T079 [US3] Implement POST /api/tasks endpoint in backend/src/api/tasks.py (calls TaskService.create_task, returns created task)
- [x] T080 [US3] Add Pydantic request model for CreateTaskRequest in backend/src/api/tasks.py (title required, description optional)

### Integration Tests for User Story 3

- [ ] T081 [US3] Write integration test for POST /api/tasks with valid data in backend/tests/integration/test_tasks_api.py
- [ ] T082 [US3] Write integration test for POST /api/tasks with empty title (400 error) in backend/tests/integration/test_tasks_api.py
- [ ] T083 [US3] Write integration test for POST /api/tasks with title exceeding 200 characters (400 error) in backend/tests/integration/test_tasks_api.py
- [ ] T084 [US3] Write integration test for POST /api/tasks with description exceeding 1000 characters (400 error) in backend/tests/integration/test_tasks_api.py
- [ ] T085 [US3] Write integration test for POST /api/tasks without authentication (401 error) in backend/tests/integration/test_tasks_api.py

### Frontend for User Story 3

- [x] T086 [US3] Create frontend/src/components/TaskForm.tsx for task creation form (Client Component with Zod validation)
- [x] T087 [US3] Implement createTask API method in frontend/src/lib/api.ts
- [x] T088 [US3] Update frontend/src/app/dashboard/page.tsx to include TaskForm component
- [x] T089 [US3] Add form validation logic to TaskForm.tsx (title 1-200 chars, description max 1000 chars)
- [x] T090 [US3] Add success message and form reset after task creation in TaskForm.tsx

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should work - users can login, view tasks, and create new tasks

---

## Phase 6: User Story 4 - Update, Complete, and Delete Tasks (Priority: P4)

**Goal**: Full CRUD capabilities - mark tasks complete/incomplete, edit task details, delete tasks with confirmation

**Independent Test**: Login → create task → mark complete → edit title/description → mark incomplete → delete with confirmation → verify removal

### Unit Tests for User Story 4 (Red Phase)

- [ ] T091 [P] [US4] Write unit test for TaskService.update_task (happy path) in backend/tests/unit/test_task_service.py
- [ ] T092 [P] [US4] Write unit test for TaskService.update_task with validation errors in backend/tests/unit/test_task_service.py
- [ ] T093 [P] [US4] Write unit test for TaskService.toggle_completion in backend/tests/unit/test_task_service.py
- [ ] T094 [P] [US4] Write unit test for TaskService.delete_task in backend/tests/unit/test_task_service.py
- [ ] T095 [P] [US4] Write unit test for TaskService operations with non-existent task (TaskNotFoundError) in backend/tests/unit/test_task_service.py

### Implementation for User Story 4 (Green Phase)

- [x] T096 [P] [US4] Implement TaskService.update_task in backend/src/services/task_service.py (update title and/or description, check user ownership)
- [x] T097 [P] [US4] Implement TaskService.toggle_completion in backend/src/services/task_service.py (toggle completed boolean, update updated_at)
- [x] T098 [P] [US4] Implement TaskService.delete_task in backend/src/services/task_service.py (delete task after ownership check)
- [x] T099 [US4] Create TaskNotFoundError exception in backend/src/services/task_service.py
- [x] T100 [US4] Implement PUT /api/tasks/{id} endpoint in backend/src/api/tasks.py (calls TaskService.update_task)
- [x] T101 [US4] Implement PATCH /api/tasks/{id}/complete endpoint in backend/src/api/tasks.py (calls TaskService.toggle_completion)
- [x] T102 [US4] Implement DELETE /api/tasks/{id} endpoint in backend/src/api/tasks.py (calls TaskService.delete_task)
- [x] T103 [US4] Add Pydantic request model for UpdateTaskRequest in backend/src/api/tasks.py (title and description optional)

### Integration Tests for User Story 4

- [ ] T104 [US4] Write integration test for PUT /api/tasks/{id} with valid data in backend/tests/integration/test_tasks_api.py
- [ ] T105 [US4] Write integration test for PUT /api/tasks/{id} with user isolation (cannot update other user's task) in backend/tests/integration/test_tasks_api.py
- [ ] T106 [US4] Write integration test for PATCH /api/tasks/{id}/complete toggling in backend/tests/integration/test_tasks_api.py
- [ ] T107 [US4] Write integration test for DELETE /api/tasks/{id} in backend/tests/integration/test_tasks_api.py
- [ ] T108 [US4] Write integration test for operations on non-existent task (404 error) in backend/tests/integration/test_tasks_api.py

### Frontend for User Story 4

- [x] T109 [P] [US4] Add edit mode to TaskItem.tsx with inline editing (Client Component)
- [x] T110 [P] [US4] Add complete/incomplete toggle button to TaskItem.tsx
- [x] T111 [P] [US4] Add delete button with confirmation dialog to TaskItem.tsx
- [x] T112 [US4] Implement updateTask API method in frontend/src/lib/api.ts
- [x] T113 [US4] Implement toggleComplete API method in frontend/src/lib/api.ts
- [x] T114 [US4] Implement deleteTask API method in frontend/src/lib/api.ts
- [x] T115 [US4] Add optimistic UI updates for toggle completion in TaskItem.tsx
- [x] T116 [US4] Add error handling and rollback for failed operations in TaskItem.tsx

**Checkpoint**: At this point, all CRUD operations work - users can create, read, update, delete, and toggle tasks

---

## Phase 7: User Story 5 - Persistent Storage and Data Integrity (Priority: P5)

**Goal**: All task data persists across sessions, server restarts, and user logins with proper data integrity

**Independent Test**: Create tasks → logout → restart backend server → login → verify all tasks remain → test concurrent operations

### Unit Tests for User Story 5 (Red Phase)

- [ ] T117 [P] [US5] Write unit test for database transaction rollback on error in backend/tests/unit/test_task_service.py
- [ ] T118 [P] [US5] Write unit test for concurrent task updates (last write wins) in backend/tests/unit/test_task_service.py
- [ ] T119 [P] [US5] Write unit test for cascade delete (user deletion deletes tasks) in backend/tests/unit/test_task_model.py

### Implementation for User Story 5 (Green Phase)

- [ ] T120 [US5] Add database transaction handling to TaskService methods in backend/src/services/task_service.py
- [ ] T121 [US5] Add error handling for database connection failures in backend/src/db.py
- [ ] T122 [US5] Add retry logic for transient database errors in backend/src/db.py
- [ ] T123 [US5] Verify foreign key constraints are enabled in Alembic migration (CASCADE delete)
- [ ] T124 [US5] Add database connection pooling configuration in backend/src/db.py (pool size 5-10)

### Integration Tests for User Story 5

- [ ] T125 [US5] Write integration test for data persistence across sessions in backend/tests/integration/test_full_workflow.py
- [ ] T126 [US5] Write integration test for server restart scenario (manual test documented) in backend/tests/integration/test_full_workflow.py
- [ ] T127 [US5] Write integration test for concurrent task creation by same user in backend/tests/integration/test_full_workflow.py
- [ ] T128 [US5] Write integration test for user deletion cascading to tasks in backend/tests/integration/test_full_workflow.py

### Additional Validations for User Story 5

- [ ] T129 [US5] Add database indexes validation (verify indexes exist on email, user_id, composite) in backend tests
- [ ] T130 [US5] Add stress test for pagination with large dataset (1000+ tasks) in backend/tests/integration/test_tasks_api.py
- [ ] T131 [US5] Add test for special characters and emojis in title/description in backend/tests/integration/test_tasks_api.py

**Checkpoint**: All user stories complete - application is production-ready with full persistence and data integrity

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Documentation

- [ ] T132 [P] Create backend/README.md with setup instructions, API documentation link, deployment guide
- [ ] T133 [P] Create frontend/README.md with setup instructions, component structure, deployment guide
- [ ] T134 [P] Update root README.md with project overview, quickstart, architecture diagram
- [ ] T135 [P] Generate TypeScript types from OpenAPI spec in frontend/src/lib/types.ts

### Code Quality

- [ ] T136 [P] Run Ruff linter on backend and fix all issues: `uv run ruff check backend/src/ --fix`
- [ ] T137 [P] Run Black formatter on backend: `uv run black backend/src/`
- [ ] T138 [P] Run mypy type checker on backend: `uv run mypy backend/src/` (ensure 100% type coverage)
- [ ] T139 [P] Run ESLint on frontend and fix issues: `pnpm lint --fix`
- [ ] T140 [P] Run Prettier on frontend: `pnpm format`
- [ ] T141 [P] Run TypeScript compiler check: `pnpm tsc --noEmit` (ensure no type errors)

### Testing & Coverage

- [ ] T142 Run full backend test suite: `uv run pytest backend/tests/` (ensure all 48+ tests pass)
- [ ] T143 Generate coverage report: `uv run pytest --cov=backend/src --cov-report=html` (ensure 90%+ coverage)
- [ ] T144 Review coverage report and add missing tests for uncovered code paths
- [ ] T145 [P] Add frontend component tests (optional) in frontend/tests/components/

### Security Hardening

- [ ] T146 [P] Verify all API endpoints use authentication middleware (except /health and /auth/*)
- [ ] T147 [P] Verify JWT secret is strong (32+ characters) and documented in .env.example
- [ ] T148 [P] Verify CORS origins are restricted to frontend URL (not wildcard)
- [ ] T149 [P] Verify HTTP-only cookie attributes (HttpOnly, Secure, SameSite=Strict)
- [ ] T150 [P] Add rate limiting middleware for auth endpoints (optional, document for Phase III)

### Performance Optimization

- [ ] T151 [P] Verify database indexes are used in queries (EXPLAIN ANALYZE on slow queries)
- [ ] T152 [P] Add database query logging for development in backend/src/db.py
- [ ] T153 [P] Verify pagination is working correctly (test with 100+ tasks)
- [ ] T154 [P] Add response compression middleware in backend/src/main.py

### Deployment Preparation

- [ ] T155 Create backend Dockerfile for production deployment
- [ ] T156 Create backend startup script with Alembic migration runner
- [ ] T157 [P] Document environment variables in backend/README.md
- [ ] T158 [P] Document environment variables in frontend/README.md
- [ ] T159 Test local deployment with Docker Compose (backend + frontend + postgres)
- [ ] T160 Run quickstart.md validation (follow guide and ensure 5-minute setup works)

### Final Validation

- [ ] T161 Manual testing of complete user journey (register → login → create → view → update → delete → logout)
- [ ] T162 Verify all acceptance criteria from spec.md are met (all 29 scenarios across 5 user stories)
- [ ] T163 Verify all success criteria from spec.md are met (SC-001 to SC-010)
- [ ] T164 Run constitution compliance check (verify 27/27 requirements still satisfied)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - MVP foundation
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) + User Story 1 models (Task model needs User FK)
- **User Story 3 (Phase 5)**: Depends on User Story 2 (uses Task model and list infrastructure)
- **User Story 4 (Phase 6)**: Depends on User Story 2 and 3 (extends CRUD operations)
- **User Story 5 (Phase 7)**: Depends on User Stories 1-4 (validates all features persist correctly)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Auth)**: Foundation for all other stories (provides User model and authentication)
- **User Story 2 (P2 - View)**: Depends on US1 (needs User model for Task FK), provides Task model
- **User Story 3 (P3 - Add)**: Depends on US2 (uses Task model and list UI)
- **User Story 4 (P4 - Update/Delete)**: Depends on US2-3 (extends existing CRUD)
- **User Story 5 (P5 - Persistence)**: Depends on US1-4 (validates all features persist)

### Within Each User Story (TDD Cycle)

1. **Red Phase**: Write unit tests FIRST, ensure they FAIL
2. **Green Phase**: Implement code to make tests PASS
3. **Integration Tests**: Write integration tests, ensure they PASS
4. **Frontend**: Build UI components using working backend
5. **Refactor**: Clean up code (Phase 8)

### Parallel Opportunities

**Within Setup (Phase 1)**: All [P] tasks can run in parallel (T002-T011)

**Within Foundational (Phase 2)**:
- Backend foundation tasks [P]: T016-T019 (create __init__.py files)
- Frontend foundation tasks [P]: T028 (install Shadcn components)

**Within User Story 1**:
- Unit tests [P]: T029-T032 (different test files)
- Frontend pages [P]: T047-T048 (different page files)

**Within User Story 2**:
- Unit tests [P]: T053-T056 (different test aspects)
- Frontend components [P]: T072-T073 (TaskList and TaskItem)

**Within User Story 3**:
- Unit tests [P]: T075-T077 (different test cases)

**Within User Story 4**:
- Unit tests [P]: T091-T095 (different operations)
- Service methods [P]: T096-T098 (different operations)
- Frontend features [P]: T109-T111 (edit, toggle, delete UI)

**Within User Story 5**:
- Unit tests [P]: T117-T119 (different persistence aspects)

**Within Polish (Phase 8)**:
- Documentation [P]: T132-T135
- Code quality [P]: T136-T141
- Security checks [P]: T146-T150
- Performance checks [P]: T151-T154
- Deployment docs [P]: T157-T158

**Across User Stories** (after Foundational complete):
- With 2 developers: Dev1 works on US1, Dev2 prepares US2 tests
- With 3 developers: Dev1=US1, Dev2=US2, Dev3=US3 (sequential execution within each story)

---

## Parallel Example: User Story 1

```bash
# Phase: Unit Tests (Red) - Run in parallel
Task T029: "Write unit test for User model validation in backend/tests/unit/test_user_model.py"
Task T030: "Write unit test for AuthService.register in backend/tests/unit/test_auth_service.py"
Task T031: "Write unit test for AuthService.login in backend/tests/unit/test_auth_service.py"
Task T032: "Write unit test for JWT token generation in backend/tests/unit/test_auth_service.py"

# Phase: Frontend Pages - Run in parallel
Task T047: "Create frontend/src/app/page.tsx as login page"
Task T048: "Create frontend/src/app/register/page.tsx as registration page"
```

---

## Parallel Example: User Story 2

```bash
# Phase: Unit Tests (Red) - Run in parallel
Task T053: "Write unit test for Task model validation in backend/tests/unit/test_task_model.py"
Task T054: "Write unit test for Task FK relationship in backend/tests/unit/test_task_model.py"
Task T055: "Write unit test for TaskService.get_tasks in backend/tests/unit/test_task_service.py"
Task T056: "Write unit test for pagination in backend/tests/unit/test_task_service.py"

# Phase: Frontend Components - Run in parallel
Task T072: "Create frontend/src/components/TaskList.tsx"
Task T073: "Create frontend/src/components/TaskItem.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Complete Phase 1**: Setup (T001-T011) → Monorepo structure ready
2. **Complete Phase 2**: Foundational (T012-T028) → Backend + Frontend foundations ready
3. **Complete Phase 3**: User Story 1 (T029-T052) → Authentication working
4. **STOP and VALIDATE**: Test registration, login, logout independently
5. **Deploy/Demo**: MVP with authentication is production-ready

**MVP Deliverable**: Secure multi-user authentication system (no task management yet)

### Incremental Delivery (Recommended)

1. **Foundation**: Setup (Phase 1) + Foundational (Phase 2) → T001-T028 complete
2. **MVP (US1)**: User Story 1 (Phase 3) → T029-T052 complete → **Deploy/Demo Auth System**
3. **Add Viewing (US2)**: User Story 2 (Phase 4) → T053-T074 complete → **Deploy/Demo Task Viewing**
4. **Add Creation (US3)**: User Story 3 (Phase 5) → T075-T090 complete → **Deploy/Demo Task Creation**
5. **Full CRUD (US4)**: User Story 4 (Phase 6) → T091-T116 complete → **Deploy/Demo Full Task Management**
6. **Production Ready (US5)**: User Story 5 (Phase 7) → T117-T131 complete → **Deploy/Demo Persistent Storage**
7. **Polish**: Phase 8 → T132-T164 complete → **Final Production Deployment**

Each deployment is independently valuable and doesn't break previous features.

### Parallel Team Strategy

**With 2 Developers**:
1. Both complete Setup + Foundational together (T001-T028)
2. Dev1: User Story 1 (T029-T052)
3. Dev2: User Story 2 tests (T053-T056) while Dev1 works on US1
4. After US1 complete: Dev1 moves to US3, Dev2 completes US2
5. Continue alternating stories

**With 3 Developers**:
1. All complete Setup + Foundational together (T001-T028)
2. After Foundational:
   - Dev1: User Story 1 (T029-T052)
   - Dev2: User Story 2 (T053-T074) - starts tests, waits for US1 User model
   - Dev3: User Story 3 tests (T075-T077) - prepares for US3
3. Stories integrate as they complete

---

## Task Count Summary

- **Phase 1 (Setup)**: 11 tasks (T001-T011)
- **Phase 2 (Foundational)**: 17 tasks (T012-T028)
- **Phase 3 (User Story 1 - Auth)**: 24 tasks (T029-T052)
  - Tests: 4 unit + 4 integration = 8 tests
  - Implementation: 16 tasks
- **Phase 4 (User Story 2 - View)**: 22 tasks (T053-T074)
  - Tests: 4 unit + 4 integration = 8 tests
  - Implementation: 14 tasks
- **Phase 5 (User Story 3 - Add)**: 15 tasks (T075-T090)
  - Tests: 3 unit + 5 integration = 8 tests
  - Implementation: 7 tasks
- **Phase 6 (User Story 4 - Update/Delete)**: 26 tasks (T091-T116)
  - Tests: 5 unit + 5 integration = 10 tests
  - Implementation: 16 tasks
- **Phase 7 (User Story 5 - Persistence)**: 15 tasks (T117-T131)
  - Tests: 3 unit + 4 integration = 7 tests
  - Implementation: 8 tasks
- **Phase 8 (Polish)**: 33 tasks (T132-T164)

**Total**: 164 tasks
- **Test tasks**: 41 tests (25% of total)
- **Implementation tasks**: 123 tasks (75% of total)
- **Parallel opportunities**: 47 tasks marked [P] (29% can run in parallel)

---

## Notes

- **[P] marker**: Tasks with different files and no dependencies - can run in parallel
- **[Story] label**: Maps task to user story for traceability (US1-US5)
- **TDD Cycle**: Red (write failing tests) → Green (make tests pass) → Refactor (Phase 8)
- **Independent Stories**: Each user story should be independently completable and testable
- **Checkpoints**: Stop after each phase to validate story works independently
- **Commit Strategy**: Commit after each task or logical group of [P] tasks
- **MVP Strategy**: Stop after User Story 1 for minimal viable product (authentication only)
- **Constitution Compliance**: All 27 requirements verified in plan.md, maintained throughout implementation
- **Coverage Target**: 90%+ for backend/src/models and backend/src/services (per constitution)
- **Test Database**: Use PostgreSQL Docker container for integration tests (not SQLite)

---

**Status**: Ready for `/sp.implement` to execute Red-Green-Refactor TDD cycle
**Last Updated**: 2026-01-12
**Version**: 2.0.0
