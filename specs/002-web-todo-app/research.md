# Research & Technology Decisions: Phase II Web Application

**Feature**: 002-web-todo-app
**Date**: 2026-01-12
**Status**: Complete

## Overview

This document captures research findings and technology decisions for Phase II implementation. All decisions align with the constitution's Phase II governance and technical standards.

---

## Decision 1: Monorepo Structure

**Decision**: Use monorepo with `backend/` and `frontend/` directories at repository root

**Rationale**:
- Simplifies dependency management across frontend and backend
- Enables code sharing for type definitions (shared TypeScript types for API contracts)
- Single CI/CD pipeline for both applications
- Easier to maintain consistency across stack
- Aligns with constitution's Phase II governance requiring separate deployments but coordinated development

**Alternatives Considered**:
- **Separate repositories**: Rejected because it complicates type sharing and versioning, increases deployment complexity
- **Nested monorepo with packages/**: Rejected as overkill for 2 applications; adds unnecessary abstraction
- **Backend-first with embedded frontend**: Rejected because constitution requires separate deployments (Vercel + cloud provider)

**Implementation Details**:
- `backend/` - FastAPI application with Python 3.13+, UV package manager
- `frontend/` - Next.js 16+ application with App Router, TypeScript strict mode
- Shared types can be generated from backend OpenAPI schema

---

## Decision 2: Database Schema & ORM

**Decision**: Use SQLModel with Alembic migrations for PostgreSQL schema management

**Rationale**:
- Constitution mandates SQLModel as the ORM (combines SQLAlchemy + Pydantic)
- Alembic is the standard SQLAlchemy migration tool
- Type-safe models aligned with Pydantic validation from Phase I
- Automatic OpenAPI schema generation from SQLModel models
- Neon PostgreSQL supports standard PostgreSQL migrations

**Alternatives Considered**:
- **Raw SQL migrations**: Rejected because it lacks type safety and constitution requires SQLModel
- **Django ORM**: Rejected because constitution mandates FastAPI, not Django
- **Prisma ORM**: Rejected because it's Node.js-based, not Python

**Implementation Details**:
- SQLModel models inherit from `SQLModel, table=True`
- Alembic for migration generation and application
- Migration strategy: auto-generate from model changes, review before applying
- Connection pooling via SQLAlchemy engine
- Async database operations using `asyncpg` driver

---

## Decision 3: Authentication Implementation with Better Auth

**Decision**: Use Better Auth library with JWT tokens stored in HTTP-only cookies

**Rationale**:
- Constitution mandates Better Auth for authentication
- Better Auth supports both Next.js and FastAPI backends
- JWT tokens provide stateless authentication (constitutional requirement)
- HTTP-only cookies prevent XSS attacks
- 7-day token expiry aligns with constitution security standards

**Alternatives Considered**:
- **Session-based auth**: Rejected because constitution requires stateless services (Pillar 8: Cloud-Native)
- **OAuth2 only**: Rejected because spec requires email/password registration (FR-001)
- **Custom JWT implementation**: Rejected because Better Auth provides tested, secure implementation

**Implementation Details**:
- Better Auth server SDK in FastAPI backend
- Better Auth client SDK in Next.js frontend
- JWT payload: `user_id`, `email`, `exp` (expiration)
- Token refresh strategy: sliding expiration (refresh on each request)
- Password hashing: bcrypt with cost factor 12
- CSRF protection via double-submit cookie pattern

**Authentication Flow**:
1. User submits email + password to `/api/auth/register` or `/api/auth/login`
2. Backend validates credentials, generates JWT
3. JWT stored in HTTP-only cookie (`Set-Cookie` header)
4. Frontend sends cookie automatically on each request
5. Backend middleware validates JWT on protected routes
6. Invalid/expired tokens redirect to login page

---

## Decision 4: API Design - RESTful with OpenAPI

**Decision**: RESTful API with 6 core endpoints, OpenAPI 3.1 specification

**Rationale**:
- REST is industry standard, simple, and well-understood
- FastAPI generates OpenAPI schema automatically from route definitions
- Aligns with constitution's declarative architecture principle
- Supports CRUD operations cleanly with HTTP verbs
- Easy to test and document

**Alternatives Considered**:
- **GraphQL**: Rejected as overkill for simple CRUD operations; adds complexity without clear benefit
- **gRPC**: Rejected because web browsers don't natively support gRPC; requires proxy
- **JSON-RPC**: Rejected because REST is more idiomatic for CRUD operations

**API Endpoints**:
1. `POST /api/auth/register` - User registration
2. `POST /api/auth/login` - User login
3. `POST /api/auth/logout` - User logout (clears cookie)
4. `GET /api/tasks` - List all tasks (with pagination)
5. `POST /api/tasks` - Create new task
6. `GET /api/tasks/{id}` - Get single task details
7. `PUT /api/tasks/{id}` - Update task (title, description)
8. `PATCH /api/tasks/{id}/complete` - Toggle completion status
9. `DELETE /api/tasks/{id}` - Delete task

**Total**: 9 endpoints (3 auth + 6 task operations)

**API Standards**:
- HTTP status codes: 200 (success), 201 (created), 400 (validation), 401 (unauthorized), 404 (not found), 500 (server error)
- JSON request/response bodies
- Pagination: `?page=1&limit=50` query parameters
- Error format: `{"detail": "Error message", "field": "field_name"}`
- CORS enabled for frontend origin

---

## Decision 5: Frontend Architecture with Next.js App Router

**Decision**: Next.js 16+ App Router with React Server Components by default, Client Components only for interactivity

**Rationale**:
- Constitution mandates Next.js 16+ with App Router
- Server Components reduce JavaScript bundle size
- Improved performance with server-side rendering
- Simplified data fetching with async components
- Type-safe routing with TypeScript

**Alternatives Considered**:
- **Pages Router**: Rejected because constitution explicitly requires App Router
- **Client-only SPA**: Rejected because it sacrifices SEO and initial load performance
- **Static Site Generation only**: Rejected because tasks require dynamic, user-specific data

**Frontend Structure**:
```
frontend/src/
├── app/                    # App Router pages
│   ├── layout.tsx          # Root layout with auth provider
│   ├── page.tsx            # Landing/login page
│   ├── register/page.tsx   # Registration page
│   ├── dashboard/          # Protected routes
│   │   ├── layout.tsx      # Dashboard layout with nav
│   │   └── page.tsx        # Task list (Server Component)
│   └── api/                # API route handlers (if needed for BFF pattern)
├── components/             # Reusable UI components
│   ├── ui/                 # Shadcn UI components
│   ├── TaskList.tsx        # Task display (Client Component)
│   ├── TaskForm.tsx        # Task creation form (Client Component)
│   └── TaskItem.tsx        # Single task card (Client Component)
├── lib/
│   ├── api.ts              # API client for backend calls
│   ├── auth.ts             # Better Auth client setup
│   └── types.ts            # TypeScript types (generated from OpenAPI)
└── hooks/
    ├── useTasks.ts         # Task data fetching hook
    └── useAuth.ts          # Authentication state hook
```

**Component Strategy**:
- Server Components: Layouts, static pages, initial data fetching
- Client Components: Forms, interactive lists, modals, real-time updates
- Use `"use client"` directive only when necessary

---

## Decision 6: State Management Strategy

**Decision**: React Server Components for server state, Zustand for client state (if needed)

**Rationale**:
- Server Components eliminate need for complex client-side data fetching
- Constitution prefers React Server Components by default (Frontend Standards)
- Zustand is lightweight, TypeScript-friendly, and approved by constitution
- Avoid over-engineering with Redux for simple task management

**Alternatives Considered**:
- **Redux Toolkit**: Rejected as overkill for current requirements; adds boilerplate
- **React Context only**: May be used for auth state, but Zustand preferred for complex client state
- **TanStack Query**: Considered but unnecessary with Server Components handling server state

**Implementation**:
- Server Components fetch data directly from backend API
- Auth state managed by Better Auth provider (React Context)
- Task list state refreshed via server actions or page revalidation
- Client-side optimistic updates for task completion toggle (Zustand if needed)

---

## Decision 7: UI Component Library - Shadcn UI + Tailwind CSS

**Decision**: Use Shadcn UI components with Tailwind CSS for styling

**Rationale**:
- Constitution mandates Tailwind CSS and Shadcn UI (Frontend Standards)
- Shadcn provides accessible, customizable components
- Components are copied into project (not external dependency) - full control
- Tailwind enables rapid UI development with utility classes
- No prop drilling with Shadcn's composition pattern

**Alternatives Considered**:
- **Material UI**: Rejected because constitution specifies Shadcn
- **Ant Design**: Rejected because constitution specifies Shadcn
- **Custom CSS**: Rejected because constitution mandates Tailwind

**Component Usage**:
- Button, Input, Card, Dialog, Form components from Shadcn
- Custom task components built on Shadcn primitives
- Tailwind utility classes for spacing, colors, responsive design
- Dark mode support via Tailwind's dark: variant (optional for Phase II)

---

## Decision 8: Testing Strategy

**Decision**: pytest for backend unit/integration tests, 90%+ coverage; optional E2E tests with Playwright

**Rationale**:
- Constitution mandates pytest with 90%+ coverage
- Unit tests for business logic (services, models)
- Integration tests for API endpoints with test database
- E2E tests ensure user workflows work end-to-end
- Aligns with Test-Driven Validation pillar

**Alternatives Considered**:
- **unittest**: Rejected because pytest is more powerful and constitution-mandated
- **Jest for backend**: Rejected because backend is Python, not Node.js
- **Cypress for E2E**: Rejected in favor of Playwright (better for Next.js App Router)

**Testing Structure**:
```
backend/tests/
├── unit/
│   ├── test_models.py       # SQLModel model tests
│   ├── test_services.py     # Business logic tests
│   └── test_auth.py         # Authentication logic tests
├── integration/
│   ├── test_auth_api.py     # Auth endpoint tests
│   └── test_tasks_api.py    # Task endpoint tests
└── conftest.py              # Pytest fixtures (test DB, test client)

frontend/tests/ (optional)
├── components/
│   ├── TaskList.test.tsx
│   └── TaskForm.test.tsx
└── e2e/
    ├── auth.spec.ts         # Registration/login flow
    └── tasks.spec.ts        # Task CRUD workflow
```

**Test Database Strategy**:
- Separate test database or in-memory SQLite for unit tests
- PostgreSQL Docker container for integration tests
- Database reset between tests using transactions or fixtures

---

## Decision 9: Deployment Architecture

**Decision**: Separate deployments - Vercel (frontend), Railway/Render (backend), Neon (database)

**Rationale**:
- Constitution Phase II governance mandates separate frontend/backend deployments
- Vercel is optimal for Next.js (official hosting partner)
- Railway/Render provide free tiers with PostgreSQL support
- Neon Serverless PostgreSQL free tier supports development
- Separate deployments enable independent scaling

**Alternatives Considered**:
- **Single container with both**: Rejected because constitution requires separate deployments
- **AWS EC2**: Rejected because free tier is complex; Railway/Render simpler
- **Heroku**: Considered but deprecated free tier; Railway/Render are better alternatives

**Deployment Strategy**:
1. **Database**: Neon PostgreSQL (connection string in env vars)
2. **Backend**: Railway or Render
   - Dockerfile for containerization
   - Environment variables: `DATABASE_URL`, `JWT_SECRET`, `FRONTEND_URL`
   - Health check endpoint: `GET /health`
3. **Frontend**: Vercel
   - Automatic deployments from Git push
   - Environment variables: `NEXT_PUBLIC_API_URL`
   - Edge functions for API routes (if using BFF pattern)

**Environment Variables**:
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@neon.tech:5432/tododb
JWT_SECRET=<generated-secret>
CORS_ORIGINS=https://frontend.vercel.app
FRONTEND_URL=https://frontend.vercel.app

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://backend.railway.app
```

---

## Decision 10: Development Environment Setup

**Decision**: UV for Python backend, npm/pnpm for Next.js frontend, Docker Compose for local database

**Rationale**:
- UV is faster than pip and mandated by constitution
- npm/pnpm are standard for Next.js projects (pnpm is faster)
- Docker Compose simplifies local PostgreSQL setup
- Consistent across developer machines

**Alternatives Considered**:
- **Conda**: Rejected because UV is constitution-mandated and faster
- **Yarn**: Considered but pnpm is more efficient
- **Local PostgreSQL install**: Rejected because Docker ensures consistency

**Setup Commands**:
```bash
# Backend
cd backend
uv sync --extra dev
uv run alembic upgrade head
uv run uvicorn src.main:app --reload

# Frontend
cd frontend
pnpm install
pnpm dev

# Database (Docker Compose)
docker-compose up -d postgres
```

---

## Summary of Key Technologies

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | Next.js 16+ (App Router) | Constitution-mandated, React Server Components |
| **Frontend UI** | Shadcn UI + Tailwind CSS | Constitution-mandated, accessible components |
| **Frontend State** | Server Components + Zustand | Constitution-preferred, minimal client state |
| **Backend** | FastAPI | Constitution-mandated, async Python framework |
| **ORM** | SQLModel + Alembic | Constitution-mandated, type-safe ORM |
| **Database** | Neon PostgreSQL | Constitution-mandated, serverless, free tier |
| **Authentication** | Better Auth + JWT | Constitution-mandated, stateless auth |
| **API Design** | REST + OpenAPI 3.1 | Industry standard, FastAPI auto-generation |
| **Testing** | pytest + Playwright | Constitution-mandated 90%+ coverage |
| **Package Mgmt** | UV (Python), pnpm (Node) | Constitution-mandated UV, efficient pnpm |
| **Deployment** | Vercel + Railway/Render | Constitution-required separate deployments |

---

## Open Questions

✅ All questions resolved during research phase. No NEEDS CLARIFICATION items remain.

---

## Constitution Alignment Checklist

- [x] Next.js 16+ with App Router (Frontend Standards)
- [x] FastAPI for backend (Python Standards)
- [x] SQLModel for ORM (Database Standards)
- [x] Neon PostgreSQL (Database Standards)
- [x] Better Auth with JWT tokens (Authentication requirement)
- [x] UV package manager (Python Standards)
- [x] TypeScript strict mode (Frontend Standards)
- [x] Pydantic models for validation (Python Standards)
- [x] pytest with 90%+ coverage (Testing Standards)
- [x] Stateless service architecture (Pillar 8: Cloud-Native)
- [x] Type safety as contract (Pillar 5)
- [x] Test-driven validation (Pillar 6)
- [x] Separate deployments (Phase II Governance)
- [x] RESTful API contracts (Phase II Governance)

**Status**: ✅ All constitution requirements satisfied
