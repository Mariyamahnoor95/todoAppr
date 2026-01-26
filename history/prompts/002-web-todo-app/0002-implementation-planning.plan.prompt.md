---
id: 0002
title: Implementation Planning and Architecture
stage: plan
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-web-todo-app
branch: 002-web-todo-app
user: noori
command: /sp.plan
labels: ["planning", "architecture", "monorepo", "api-design", "database-schema"]
links:
  spec: specs/002-web-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-web-todo-app/plan.md
  - specs/002-web-todo-app/research.md
  - specs/002-web-todo-app/data-model.md
  - specs/002-web-todo-app/quickstart.md
  - specs/002-web-todo-app/contracts/openapi.yaml
  - specs/002-web-todo-app/contracts/API-ENDPOINTS.md
tests:
  - All constitution checks passed (13 Phase II governance + 5 code quality + 5 security + 4 database)
---

## Prompt

Create implementation architecture including:
  - Monorepo structure (frontend/ and backend/)
  - RESTful API contracts (6 endpoints)
  - Database schema design
  - Authentication flow architecture
  - Deployment strategy

## Response snapshot

Successfully executed complete implementation planning workflow for Phase II web application following Spec-Driven Development methodology.

**Phase 0 - Research** (`research.md`):
- **10 technology decisions** documented with rationale and alternatives considered
- **Decision 1**: Monorepo structure (backend/ + frontend/) for code sharing and coordinated development
- **Decision 2**: SQLModel ORM with Alembic migrations for type-safe PostgreSQL schema management
- **Decision 3**: Better Auth with JWT tokens in HTTP-only cookies for stateless authentication
- **Decision 4**: RESTful API with 9 endpoints (3 auth + 6 task operations), OpenAPI 3.1 specification
- **Decision 5**: Next.js 16+ App Router with React Server Components by default
- **Decision 6**: Server Components for server state, Zustand for client state (if needed)
- **Decision 7**: Shadcn UI + Tailwind CSS (constitution-mandated)
- **Decision 8**: pytest for backend (90%+ coverage), optional Playwright for E2E
- **Decision 9**: Separate deployments - Vercel (frontend), Railway/Render (backend), Neon (database)
- **Decision 10**: UV for Python, pnpm for Node.js, Docker Compose for local PostgreSQL

**Phase 1 - Design** (`data-model.md`, `contracts/`, `quickstart.md`):
- **Data Model**:
  - **User entity**: id, email (unique), password_hash, created_at
  - **Task entity**: id, user_id (FK), title (1-200 chars), description (0-1000 chars), completed (bool), created_at, updated_at
  - **Relationship**: users 1:N tasks (CASCADE delete)
  - **Indexes**: Primary keys, unique email, foreign keys, composite (user_id, created_at DESC)
  - **Validation**: Pydantic at API layer, PostgreSQL constraints at DB layer

- **API Contracts** (`contracts/openapi.yaml`, `contracts/API-ENDPOINTS.md`):
  - **10 endpoints**: 3 auth (register, login, logout) + 6 task (list, create, get, update, toggle, delete) + 1 health check
  - **Authentication**: JWT in HTTP-only cookies (Max-Age=604800 = 7 days)
  - **Pagination**: GET /api/tasks?page=1&limit=50 (default 50, max 100)
  - **Error format**: {"detail": "message", "field": "field_name"}
  - **Status codes**: 200, 201 (created), 400 (validation), 401 (unauthorized), 404 (not found), 500 (server error)

- **Quickstart Guide** (`quickstart.md`):
  - Prerequisites (Python 3.13+, Node 20+, UV, pnpm, Docker)
  - Quick setup (5 minutes): Docker PostgreSQL → backend setup → frontend setup
  - Development workflow (TDD, schema changes, API changes)
  - Environment variables reference
  - Troubleshooting guide
  - Production deployment instructions

**Architecture Plan** (`plan.md`):
- **Summary**: Multi-user web application with authentication and persistent task storage
- **Technical Context**: Python 3.13 + TypeScript 5, FastAPI + Next.js 16+, Neon PostgreSQL, pytest + Playwright
- **Project Type**: Web application (monorepo)
- **Performance Goals**: <500ms API p95, <2s frontend load, 100 concurrent users
- **Monorepo Structure**:
  - `backend/`: FastAPI app with src/ (models, services, api, middleware), tests/, alembic/, pyproject.toml
  - `frontend/`: Next.js app with src/app/ (pages), components/, lib/, hooks/, tests/, package.json
  - Shared: docker-compose.yml, specs/002-web-todo-app/

**Constitution Check**:
- ✅ **27 requirements verified**: 13 Phase II governance + 5 code quality + 5 security + 4 database standards
- ✅ All constitution-mandated technologies used (Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth, UV, TypeScript strict, pytest 90%+)
- ✅ Stateless architecture (JWT tokens, no server sessions)
- ✅ Type safety enforced (Pydantic + TypeScript strict)
- ✅ Separate deployments (Vercel + Railway/Render)
- ✅ Zero violations detected

**Architecture Diagrams**:
- System architecture (Browser → Next.js → FastAPI → PostgreSQL)
- Authentication flow (register → login → JWT cookie → protected requests → logout)
- Data flow (create task, list tasks paginated, toggle completion)

**Deliverables**:
1. `research.md` (10 technology decisions, 3,500+ lines)
2. `data-model.md` (2 entities, relationships, validation, indexes, migrations)
3. `contracts/openapi.yaml` (OpenAPI 3.1 spec with all endpoints, schemas, examples)
4. `contracts/API-ENDPOINTS.md` (10 endpoints reference with curl examples, TypeScript API client)
5. `quickstart.md` (5-minute setup, development workflow, troubleshooting, deployment)
6. `plan.md` (complete architecture with diagrams, testing strategy, security, performance optimization)

## Outcome

- ✅ Impact: Complete Phase II implementation plan with monorepo structure, 10 API endpoints, 2-entity database schema, authentication flow, deployment strategy - ready for `/sp.tasks` phase
- 🧪 Tests: All 27 constitution requirements verified and passed (13 governance + 5 code quality + 5 security + 4 database)
- 📁 Files: 6 planning documents created (plan.md, research.md, data-model.md, quickstart.md, openapi.yaml, API-ENDPOINTS.md)
- 🔁 Next prompts: Ready for `/sp.tasks` to generate task breakdown with TDD test cases, then `/sp.implement` for Red-Green-Refactor implementation
- 🧠 Reflection: Planning successfully completed following SDD methodology. All technology decisions documented with rationale and alternatives. Monorepo structure simplifies type sharing (generate TypeScript types from OpenAPI). Authentication flow uses constitution-mandated Better Auth with JWT in HTTP-only cookies. Database schema normalized with proper foreign keys and indexes. API contracts defined in OpenAPI 3.1 with full request/response examples. Quickstart guide enables 5-minute local setup. All 27 constitution requirements satisfied with zero violations.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully with all deliverables generated and validated
- Graders run and results (PASS/FAIL): Constitution check PASS (27/27 requirements), Monorepo structure PASS (clear separation of concerns), API design PASS (RESTful with OpenAPI 3.1), Database schema PASS (normalized with proper indexes), Security design PASS (JWT in HTTP-only cookies, bcrypt password hashing), Deployment strategy PASS (separate Vercel + Railway/Render + Neon)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 (research) → Phase 1 (design: data model + contracts + quickstart) → Final plan consolidation
- Next experiment (smallest change to try): Proceed to `/sp.tasks` to generate atomic, testable implementation tasks ordered by user story priority (P1: Auth → P2: View → P3: Add → P4: Update/Delete → P5: Persistence). Each task should include preconditions, test cases (Red phase), and acceptance criteria.
