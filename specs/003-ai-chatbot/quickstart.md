# Quickstart: AI Chatbot for Todo Management

**Feature**: 003-ai-chatbot
**Date**: 2026-02-05

## Prerequisites

Before starting Phase III implementation:

1. **Phase II Complete**: Web application running with:
   - FastAPI backend on `http://localhost:8000`
   - Next.js frontend on `http://localhost:3000`
   - Neon PostgreSQL database connected
   - Better Auth authentication working

2. **API Keys**:
   - OpenAI API key (for Agents SDK)
   - OpenAI domain key (for ChatKit - get after deployment)

3. **Development Environment**:
   - Python 3.13+
   - Node.js 20+
   - UV package manager
   - Git on branch `003-ai-chatbot`

## Quick Setup

### 1. Install New Dependencies

**Backend** (from `/backend`):
```bash
uv add openai-agents mcp
```

**Frontend** (from `/frontend`):
```bash
npm install @openai/chatkit
```

### 2. Add Environment Variables

**Backend** (`.env`):
```env
# Existing Phase II variables...
OPENAI_API_KEY=sk-your-openai-api-key
CONVERSATION_HISTORY_LIMIT=20
```

**Frontend** (`.env.local`):
```env
# Existing Phase II variables...
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-your-domain-key
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000/api
```

### 3. Run Database Migration

```bash
# From /backend
python -m alembic upgrade head
# Or run migration script directly
psql $DATABASE_URL -f migrations/003_add_chat_tables.sql
```

### 4. Verify Setup

```bash
# Backend health check
curl http://localhost:8000/health

# Test chat endpoint (requires auth token)
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my tasks"}'
```

## Development Workflow

### Start Development Servers

**Terminal 1 - Backend**:
```bash
cd backend
uv run uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Run Tests

```bash
# Backend tests
cd backend
uv run pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## Key Files to Create

### Backend

| File | Purpose |
|------|---------|
| `src/models/conversation.py` | Conversation SQLModel |
| `src/models/message.py` | Message SQLModel |
| `src/services/conversation_service.py` | Conversation CRUD |
| `src/services/chat_service.py` | AI chat orchestration |
| `src/mcp/server.py` | MCP server with 5 tools |
| `src/mcp/tools.py` | Tool implementations |
| `src/api/chat.py` | Chat API endpoints |

### Frontend

| File | Purpose |
|------|---------|
| `src/components/Chat.tsx` | ChatKit wrapper component |
| `src/components/ChatMessage.tsx` | Message display component |
| `src/hooks/useChat.ts` | Chat state management |
| `src/lib/chat-api.ts` | Chat API client |
| `src/app/chat/page.tsx` | Chat page route |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  ChatKit    │───►│  useChat    │───►│  chat-api   │    │
│   │  Component  │    │    Hook     │    │   Client    │    │
│   └─────────────┘    └─────────────┘    └──────┬──────┘    │
└────────────────────────────────────────────────┼────────────┘
                                                 │ HTTP
                                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  /api/chat  │───►│   Chat      │───►│   OpenAI    │    │
│   │  Endpoint   │    │  Service    │    │   Agent     │    │
│   └─────────────┘    └─────────────┘    └──────┬──────┘    │
│                                                 │            │
│                                                 │ MCP        │
│                                                 ▼            │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │   Task      │◄───│    MCP      │◄───│    MCP      │    │
│   │  Service    │    │   Tools     │    │   Server    │    │
│   └──────┬──────┘    └─────────────┘    └─────────────┘    │
│          │                                                  │
└──────────┼──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
│   ┌─────────┐    ┌──────────────┐    ┌───────────┐         │
│   │  tasks  │    │conversations │    │  messages │         │
│   └─────────┘    └──────────────┘    └───────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow

1. **User sends message** via ChatKit UI
2. **Frontend** calls `POST /api/{user_id}/chat`
3. **Backend** validates JWT, gets user_id
4. **Chat Service** loads/creates conversation
5. **Chat Service** fetches last 20 messages for context
6. **Chat Service** stores user message in database
7. **OpenAI Agent** runs with MCP tools available
8. **Agent** interprets intent, calls appropriate MCP tool(s)
9. **MCP Tool** executes via Task Service (database)
10. **Agent** generates friendly response
11. **Chat Service** stores assistant response in database
12. **Backend** returns response with tool calls
13. **Frontend** displays response in ChatKit

## Stateless Verification

To verify stateless architecture:

1. Start chat conversation
2. Send a few messages
3. Restart backend server
4. Continue conversation (should work seamlessly)
5. All history should be preserved

## Common Commands

```bash
# Check conversation count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM conversations;"

# View recent messages
psql $DATABASE_URL -c "SELECT role, content FROM messages ORDER BY created_at DESC LIMIT 10;"

# Clear test data
psql $DATABASE_URL -c "TRUNCATE messages, conversations CASCADE;"
```

## Next Steps After Setup

1. Implement database models (Conversation, Message)
2. Create MCP server with 5 tools
3. Implement chat service with agent integration
4. Add chat API endpoint
5. Create frontend chat components
6. Test full conversation flow
7. Validate statelessness

See `tasks.md` (after running `/sp.tasks`) for detailed implementation tasks.
