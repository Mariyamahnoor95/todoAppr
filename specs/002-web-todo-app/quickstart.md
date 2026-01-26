# Quickstart Guide: Phase II Web Application

**Feature**: 002-web-todo-app
**Date**: 2026-01-12

## Overview

This quickstart guide helps you set up the Phase II web application development environment and run the application locally.

**Architecture**: Monorepo with separate frontend (Next.js) and backend (FastAPI)
**Database**: PostgreSQL (Neon serverless or local Docker)

---

## Prerequisites

Install these tools before starting:

- **Python 3.13+**: [python.org](https://www.python.org/downloads/)
- **Node.js 20+**: [nodejs.org](https://nodejs.org/)
- **UV** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **pnpm** (Node package manager): `npm install -g pnpm`
- **Docker** (for local database): [docker.com](https://www.docker.com/)
- **Git**: [git-scm.com](https://git-scm.com/)

**Optional**:
- **PostgreSQL** (if not using Docker): [postgresql.org](https://www.postgresql.org/)

---

## Quick Setup (5 minutes)

### 1. Clone and Navigate

```bash
cd /path/to/todoAppr
git checkout 002-web-todo-app
```

### 2. Start Database (Docker)

```bash
# Create docker-compose.yml if not exists
cat > docker-compose.yml <<EOF
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: todouser
      POSTGRES_PASSWORD: todopass
      POSTGRES_DB: tododb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

# Start PostgreSQL
docker-compose up -d postgres
```

**Alternative**: Use Neon PostgreSQL (skip Docker, get connection string from [neon.tech](https://neon.tech))

### 3. Setup Backend

```bash
cd backend

# Install dependencies
uv sync --extra dev

# Create .env file
cat > .env <<EOF
DATABASE_URL=postgresql://todouser:todopass@localhost:5432/tododb
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000
EOF

# Run migrations
uv run alembic upgrade head

# Start backend server
uv run uvicorn src.main:app --reload
```

**Backend running at**: `http://localhost:8000`
**API Docs**: `http://localhost:8000/docs`

### 4. Setup Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
pnpm install

# Create .env.local file
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Start development server
pnpm dev
```

**Frontend running at**: `http://localhost:3000`

### 5. Test the Application

1. Open browser to `http://localhost:3000`
2. Register a new account
3. Create, view, update, and delete tasks
4. Test authentication (login/logout)

---

## Detailed Setup Instructions

### Backend Setup

#### Step 1: Install Dependencies

```bash
cd backend

# Install all dependencies including dev tools
uv sync --extra dev

# Verify installation
uv run python --version  # Should show Python 3.13+
```

**Dependencies Installed**:
- `fastapi`: Web framework
- `uvicorn[standard]`: ASGI server
- `sqlmodel`: ORM (SQLAlchemy + Pydantic)
- `psycopg2-binary`: PostgreSQL driver
- `alembic`: Database migrations
- `python-jose[cryptography]`: JWT handling
- `passlib[bcrypt]`: Password hashing
- `python-multipart`: Form data handling
- `pytest`, `pytest-asyncio`, `pytest-cov`: Testing tools

#### Step 2: Configure Environment Variables

Create `backend/.env`:

```env
# Database connection
DATABASE_URL=postgresql://todouser:todopass@localhost:5432/tododb

# For Neon PostgreSQL, use format:
# DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/tododb?sslmode=require

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=your-secret-key-here-change-in-production

# CORS configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Frontend URL (for redirects)
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Important**: Generate a new JWT_SECRET for each environment. Never commit secrets to Git.

#### Step 3: Initialize Database

```bash
cd backend

# Create first migration (if not exists)
uv run alembic revision --autogenerate -m "Initial schema"

# Apply migrations
uv run alembic upgrade head

# Verify database
uv run python -c "from src.db import engine; print('Database connected!')"
```

#### Step 4: Run Backend Server

```bash
# Development mode (auto-reload on changes)
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
uv run python -m src.main
```

**Verify Backend**:
- Health check: `curl http://localhost:8000/health`
- API docs: Open `http://localhost:8000/docs` in browser

---

### Frontend Setup

#### Step 1: Install Dependencies

```bash
cd frontend

# Install dependencies
pnpm install

# Verify installation
pnpm next --version  # Should show Next.js 16+
```

**Dependencies Installed**:
- `next`: Next.js framework
- `react`, `react-dom`: React library
- `typescript`: TypeScript support
- `tailwindcss`: Utility-first CSS
- `@shadcn/ui`: UI component library
- `zustand`: State management (if needed)
- `zod`: Schema validation

#### Step 2: Configure Environment Variables

Create `frontend/.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production, use actual backend URL:
# NEXT_PUBLIC_API_URL=https://api.example.com
```

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

#### Step 3: Run Development Server

```bash
cd frontend

# Start Next.js dev server
pnpm dev

# Or specify port
pnpm dev --port 3000
```

**Verify Frontend**:
- Open `http://localhost:3000` in browser
- Should see login/registration page

---

## Project Structure

```
todoAppr/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User SQLModel
│   │   │   └── task.py          # Task SQLModel
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Authentication logic
│   │   │   └── task_service.py  # Task CRUD logic
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   └── tasks.py         # Task endpoints
│   │   ├── db.py                # Database setup
│   │   ├── config.py            # Configuration
│   │   └── main.py              # FastAPI app
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── register/page.tsx
│   │   │   └── dashboard/
│   │   │       └── page.tsx     # Task dashboard
│   │   ├── components/
│   │   │   ├── ui/              # Shadcn components
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskForm.tsx
│   │   │   └── TaskItem.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   ├── auth.ts          # Auth helpers
│   │   │   └── types.ts         # TypeScript types
│   │   └── hooks/
│   │       ├── useTasks.ts
│   │       └── useAuth.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── .env.local
│
├── docker-compose.yml
└── specs/002-web-todo-app/
    ├── spec.md
    ├── plan.md
    ├── research.md
    ├── data-model.md
    ├── quickstart.md (this file)
    └── contracts/
```

---

## Common Tasks

### Running Tests

**Backend Tests**:
```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_task_service.py

# Run with verbose output
uv run pytest -v
```

**Frontend Tests** (optional):
```bash
cd frontend

# Run Jest tests
pnpm test

# Run E2E tests with Playwright
pnpm test:e2e
```

### Database Management

**Create New Migration**:
```bash
cd backend
uv run alembic revision --autogenerate -m "Add new column"
```

**Apply Migrations**:
```bash
uv run alembic upgrade head
```

**Rollback Migration**:
```bash
uv run alembic downgrade -1
```

**Reset Database** (development only):
```bash
# Drop all tables
uv run alembic downgrade base

# Reapply all migrations
uv run alembic upgrade head
```

### Code Quality

**Backend Linting**:
```bash
cd backend

# Run Ruff linter
uv run ruff check src/

# Auto-fix issues
uv run ruff check src/ --fix

# Format with Black
uv run black src/
```

**Frontend Linting**:
```bash
cd frontend

# Run ESLint
pnpm lint

# Auto-fix issues
pnpm lint --fix

# Format with Prettier
pnpm format
```

### Type Checking

**Backend**:
```bash
cd backend
uv run mypy src/
```

**Frontend**:
```bash
cd frontend
pnpm tsc --noEmit
```

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Make sure you're running commands with `uv run` from the `backend/` directory.

---

**Issue**: `Could not connect to database`

**Solution**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check connection string in .env
cat .env | grep DATABASE_URL

# Test connection manually
psql -h localhost -U todouser -d tododb
```

---

**Issue**: `Alembic can't locate revision`

**Solution**:
```bash
# Regenerate migration
uv run alembic revision --autogenerate -m "Regenerate schema"

# Or reset alembic
rm -rf alembic/versions/*.py
uv run alembic revision --autogenerate -m "Initial schema"
```

---

### Frontend Issues

**Issue**: `Failed to fetch` or CORS errors

**Solution**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS_ORIGINS in backend `.env` includes `http://localhost:3000`

---

**Issue**: `Authentication not working`

**Solution**:
- Check browser console for errors
- Verify JWT_SECRET is set in backend `.env`
- Check cookies in browser DevTools (Application → Cookies)
- Verify `credentials: 'include'` in fetch options

---

### Database Issues

**Issue**: Docker PostgreSQL won't start

**Solution**:
```bash
# Check logs
docker-compose logs postgres

# Remove and recreate
docker-compose down -v
docker-compose up -d postgres
```

---

**Issue**: Port 5432 already in use

**Solution**:
```bash
# Stop local PostgreSQL
sudo service postgresql stop

# Or change Docker port in docker-compose.yml
ports:
  - "5433:5432"  # Use port 5433 instead

# Update DATABASE_URL to use port 5433
```

---

## Development Workflow

### 1. Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Write tests (TDD)
cd backend
# Edit tests/unit/test_my_feature.py

# 3. Run tests (should fail - Red)
uv run pytest tests/unit/test_my_feature.py

# 4. Implement feature
# Edit src/...

# 5. Run tests (should pass - Green)
uv run pytest tests/unit/test_my_feature.py

# 6. Refactor if needed

# 7. Commit
git add .
git commit -m "feat: add my feature"
```

### 2. Database Schema Changes

```bash
# 1. Update SQLModel models
# Edit backend/src/models/*.py

# 2. Generate migration
cd backend
uv run alembic revision --autogenerate -m "Add new field"

# 3. Review migration in alembic/versions/

# 4. Apply migration
uv run alembic upgrade head

# 5. Test with updated schema
uv run pytest
```

### 3. API Changes

```bash
# 1. Update OpenAPI spec
# Edit specs/002-web-todo-app/contracts/openapi.yaml

# 2. Implement backend endpoint
# Edit backend/src/api/*.py

# 3. Update frontend API client
# Edit frontend/src/lib/api.ts

# 4. Test integration
# Manual testing or E2E tests
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `JWT_SECRET` | Yes | Secret key for JWT signing | `your-secret-key-here` |
| `CORS_ORIGINS` | Yes | Allowed frontend origins (comma-separated) | `http://localhost:3000` |
| `FRONTEND_URL` | Yes | Frontend URL for redirects | `http://localhost:3000` |
| `ENVIRONMENT` | No | Environment name | `development`, `production` |

### Frontend (.env.local)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API base URL | `http://localhost:8000` |

---

## Production Deployment

### Backend (Railway/Render)

1. **Create account** on [Railway.app](https://railway.app) or [Render.com](https://render.com)

2. **Create new project** → Deploy from GitHub

3. **Add environment variables**:
   - `DATABASE_URL`: Get from Neon PostgreSQL
   - `JWT_SECRET`: Generate new secret
   - `CORS_ORIGINS`: Frontend production URL
   - `FRONTEND_URL`: Frontend production URL

4. **Set build command**: `cd backend && uv sync`

5. **Set start command**: `cd backend && uv run uvicorn src.main:app --host 0.0.0.0 --port $PORT`

6. **Apply migrations** (via CLI or startup script):
   ```bash
   uv run alembic upgrade head
   ```

### Frontend (Vercel)

1. **Create account** on [Vercel.com](https://vercel.com)

2. **Import project** from GitHub

3. **Configure project**:
   - Framework: Next.js
   - Root directory: `frontend`
   - Build command: `pnpm build`
   - Output directory: `.next`

4. **Add environment variable**:
   - `NEXT_PUBLIC_API_URL`: Backend production URL (from Railway/Render)

5. **Deploy** → Automatic on every push to main branch

### Database (Neon)

1. **Create account** on [Neon.tech](https://neon.tech)

2. **Create new project** → Choose region

3. **Get connection string** from dashboard

4. **Update backend** `DATABASE_URL` with Neon connection string

---

## Next Steps

After completing quickstart:

1. **Explore API docs**: `http://localhost:8000/docs`
2. **Run tests**: `cd backend && uv run pytest`
3. **Review spec**: `specs/002-web-todo-app/spec.md`
4. **Check tasks**: `specs/002-web-todo-app/tasks.md` (after running `/sp.tasks`)
5. **Start implementing**: Follow TDD workflow above

---

## Support

For issues or questions:
- **Spec**: `specs/002-web-todo-app/spec.md`
- **Plan**: `specs/002-web-todo-app/plan.md`
- **Research**: `specs/002-web-todo-app/research.md`
- **Data Model**: `specs/002-web-todo-app/data-model.md`
- **API Contracts**: `specs/002-web-todo-app/contracts/`
- **Constitution**: `.specify/memory/constitution.md`

---

**Last Updated**: 2026-01-12
**Version**: 2.0.0
