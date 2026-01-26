# API Endpoints Reference

**Feature**: 002-web-todo-app
**Version**: 2.0.0
**Base URL**: `http://localhost:8000` (development), `https://api.example.com` (production)
**Authentication**: JWT tokens in HTTP-only cookies

---

## Quick Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | User login |
| POST | `/api/auth/logout` | Yes | User logout |
| GET | `/api/tasks` | Yes | List all user's tasks (paginated) |
| POST | `/api/tasks` | Yes | Create new task |
| GET | `/api/tasks/{id}` | Yes | Get single task |
| PUT | `/api/tasks/{id}` | Yes | Update task |
| PATCH | `/api/tasks/{id}/complete` | Yes | Toggle task completion |
| DELETE | `/api/tasks/{id}` | Yes | Delete task |
| GET | `/health` | No | Health check |

**Total**: 10 endpoints (3 auth + 6 task operations + 1 health check)

---

## Authentication Endpoints

### 1. Register User

**Endpoint**: `POST /api/auth/register`

**Description**: Create a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Validation**:
- Email: Valid email format, max 255 characters, unique
- Password: Minimum 8 characters

**Success Response** (201 Created):
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-01-12T10:30:00Z"
}
```

**Headers**:
```
Set-Cookie: token=eyJhbGc...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Error Responses**:
- `400 Bad Request`: Email already exists, invalid email format, or weak password
  ```json
  {
    "detail": "Email already registered",
    "field": "email"
  }
  ```

---

### 2. Login User

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticate user and receive JWT token

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-01-12T10:30:00Z"
}
```

**Headers**:
```
Set-Cookie: token=eyJhbGc...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
  ```json
  {
    "detail": "Invalid email or password"
  }
  ```

---

### 3. Logout User

**Endpoint**: `POST /api/auth/logout`

**Description**: Clear JWT token and end session

**Authentication**: Required (JWT cookie)

**Success Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

**Headers**:
```
Set-Cookie: token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0
```

---

## Task Endpoints

### 4. List Tasks

**Endpoint**: `GET /api/tasks`

**Description**: Retrieve paginated list of tasks for authenticated user

**Authentication**: Required (JWT cookie)

**Query Parameters**:
- `page` (optional): Page number, default 1, minimum 1
- `limit` (optional): Items per page, default 50, max 100

**Example Request**:
```
GET /api/tasks?page=1&limit=50
```

**Success Response** (200 OK):
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-12T10:30:00Z",
      "updated_at": "2026-01-12T10:30:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "title": "Call dentist",
      "description": "",
      "completed": true,
      "created_at": "2026-01-11T15:20:00Z",
      "updated_at": "2026-01-12T09:00:00Z"
    }
  ],
  "page": 1,
  "limit": 50,
  "total": 237,
  "pages": 5
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated

---

### 5. Create Task

**Endpoint**: `POST /api/tasks`

**Description**: Create a new task for authenticated user

**Authentication**: Required (JWT cookie)

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Validation**:
- Title: Required, 1-200 characters
- Description: Optional, max 1000 characters

**Success Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error
  ```json
  {
    "detail": "Title must be between 1 and 200 characters",
    "field": "title"
  }
  ```
- `401 Unauthorized`: Not authenticated

---

### 6. Get Task

**Endpoint**: `GET /api/tasks/{id}`

**Description**: Retrieve details of a specific task

**Authentication**: Required (JWT cookie)

**Path Parameters**:
- `id`: Task ID (integer)

**Example Request**:
```
GET /api/tasks/1
```

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Task not found or not owned by user
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

### 7. Update Task

**Endpoint**: `PUT /api/tasks/{id}`

**Description**: Update task title and/or description

**Authentication**: Required (JWT cookie)

**Path Parameters**:
- `id`: Task ID (integer)

**Request Body**:
```json
{
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, cheese"
}
```

**Notes**:
- At least one field (title or description) must be provided
- Omitted fields remain unchanged
- Pass `null` to explicitly set description to empty string

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, cheese",
  "completed": false,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:35:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error or no fields provided
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Task not found

---

### 8. Toggle Task Completion

**Endpoint**: `PATCH /api/tasks/{id}/complete`

**Description**: Toggle task completion status (complete ↔ incomplete)

**Authentication**: Required (JWT cookie)

**Path Parameters**:
- `id`: Task ID (integer)

**Request Body**: None (empty)

**Success Response** (200 OK):
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": true,
  "created_at": "2026-01-12T10:30:00Z",
  "updated_at": "2026-01-12T10:40:00Z"
}
```

**Behavior**:
- If `completed=false`, sets to `true`
- If `completed=true`, sets to `false`
- Updates `updated_at` timestamp

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Task not found

---

### 9. Delete Task

**Endpoint**: `DELETE /api/tasks/{id}`

**Description**: Permanently delete a task

**Authentication**: Required (JWT cookie)

**Path Parameters**:
- `id`: Task ID (integer)

**Success Response** (200 OK):
```json
{
  "message": "Task deleted successfully"
}
```

**Note**: Deletion is permanent (hard delete). Task cannot be recovered.

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Task not found

---

## System Endpoints

### 10. Health Check

**Endpoint**: `GET /health`

**Description**: Check if API is running

**Authentication**: Not required

**Success Response** (200 OK):
```json
{
  "status": "ok"
}
```

---

## Authentication Flow

### Cookie-Based JWT Authentication

1. **Registration/Login**:
   - User submits credentials to `/api/auth/register` or `/api/auth/login`
   - Backend validates credentials
   - Backend generates JWT token with user_id, email, exp
   - Backend sets JWT in HTTP-only cookie via `Set-Cookie` header
   - Frontend receives user data in response body

2. **Authenticated Requests**:
   - Browser automatically sends cookie with each request
   - Backend middleware extracts JWT from cookie
   - Backend validates JWT signature and expiration
   - Backend extracts user_id from JWT payload
   - Backend uses user_id to filter user's data

3. **Logout**:
   - User calls `/api/auth/logout`
   - Backend sets cookie with `Max-Age=0` to clear it
   - Frontend redirects to login page

### JWT Token Structure

**Payload**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "exp": 1736784600
}
```

**Cookie Attributes**:
- `HttpOnly`: Prevents JavaScript access (XSS protection)
- `Secure`: HTTPS only in production
- `SameSite=Strict`: CSRF protection
- `Max-Age=604800`: 7 days (per constitution)

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Human-readable error message",
  "field": "field_name"
}
```

**Fields**:
- `detail` (required): Error message describing what went wrong
- `field` (optional): Name of the field that caused validation error

**Common HTTP Status Codes**:
- `200 OK`: Successful GET, PUT, PATCH, DELETE
- `201 Created`: Successful POST (resource created)
- `400 Bad Request`: Validation error or malformed request
- `401 Unauthorized`: Authentication required or invalid token
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Unexpected server error

---

## CORS Configuration

**Development**:
- Allow origin: `http://localhost:3000` (Next.js dev server)
- Allow credentials: `true` (for cookies)
- Allow methods: `GET, POST, PUT, PATCH, DELETE, OPTIONS`
- Allow headers: `Content-Type, Authorization`

**Production**:
- Allow origin: `https://frontend.vercel.app` (actual frontend URL)
- Same settings as development

---

## Rate Limiting (Optional for Phase II)

**Recommendation** (not implemented in Phase II):
- Registration: 5 attempts per hour per IP
- Login: 10 attempts per hour per IP/email
- Task operations: 100 requests per minute per user

**Implementation**: Can be added in Phase III with Redis or in-memory store

---

## Request/Response Examples

### Complete Task Creation Flow

**1. Register User**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}' \
  -c cookies.txt
```

**2. Create Task** (using saved cookie):
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}'
```

**3. List Tasks**:
```bash
curl -X GET http://localhost:8000/api/tasks?page=1&limit=50 \
  -b cookies.txt
```

**4. Toggle Completion**:
```bash
curl -X PATCH http://localhost:8000/api/tasks/1/complete \
  -b cookies.txt
```

**5. Logout**:
```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -b cookies.txt
```

---

## Frontend Integration

### API Client Setup (TypeScript)

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    credentials: 'include', // Send cookies
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  auth: {
    register: (email: string, password: string) =>
      apiFetch('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    login: (email: string, password: string) =>
      apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    logout: () =>
      apiFetch('/api/auth/logout', { method: 'POST' }),
  },
  tasks: {
    list: (page = 1, limit = 50) =>
      apiFetch(`/api/tasks?page=${page}&limit=${limit}`),
    create: (title: string, description = '') =>
      apiFetch('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({ title, description }),
      }),
    get: (id: number) =>
      apiFetch(`/api/tasks/${id}`),
    update: (id: number, data: { title?: string; description?: string }) =>
      apiFetch(`/api/tasks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    toggleComplete: (id: number) =>
      apiFetch(`/api/tasks/${id}/complete`, { method: 'PATCH' }),
    delete: (id: number) =>
      apiFetch(`/api/tasks/${id}`, { method: 'DELETE' }),
  },
};
```

---

## Security Considerations

### Input Validation
- All inputs validated at API layer (Pydantic models)
- SQL injection prevented by SQLModel (parameterized queries)
- XSS prevention: Sanitize user input before rendering in frontend

### Authentication Security
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens in HTTP-only cookies (not localStorage)
- CSRF protection via SameSite=Strict cookies
- Token expiration after 7 days

### Authorization
- Every task endpoint verifies user_id matches task owner
- Users can only access their own tasks
- Database queries always filter by `user_id`

---

## Testing Endpoints

### Unit Tests (pytest)
- Test each endpoint with valid and invalid inputs
- Test authentication middleware
- Test user isolation (user A cannot access user B's tasks)
- Test pagination logic

### Integration Tests (pytest)
- Test full workflows (register → login → create task → update → delete)
- Test with real database (PostgreSQL Docker container)
- Test CORS headers
- Test cookie handling

### E2E Tests (Playwright - optional)
- Test complete user journeys through frontend
- Test authentication flow
- Test task CRUD operations

---

## OpenAPI Documentation

Full OpenAPI 3.1 specification available at:
- **File**: `specs/002-web-todo-app/contracts/openapi.yaml`
- **Interactive docs** (when backend running): `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)

FastAPI automatically generates interactive API documentation from the OpenAPI spec.
