# Implementation Plan: AI Chatbot for Todo Management

**Branch**: `003-ai-chatbot` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot/spec.md`

## Summary

Implement an AI-powered chatbot interface for natural language task management. Users will interact with a chat UI (OpenAI ChatKit) to manage their todos through conversation. The backend uses OpenAI Agents SDK with MCP (Model Context Protocol) tools for task operations. All conversation state persists in the database, ensuring stateless server architecture.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Official MCP SDK, OpenAI ChatKit, SQLModel
**Storage**: Neon Serverless PostgreSQL (existing) + Conversation/Message tables (new)
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Web application (existing Phase II infrastructure)
**Project Type**: Web (monorepo: backend/ + frontend/)
**Performance Goals**: p95 < 3s for chat responses, p95 < 200ms for task operations
**Constraints**: Stateless server (all state in database), user isolation enforced
**Scale/Scope**: Single-user conversations, 5 MCP tools, ~10 new backend files, ~6 new frontend files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Specification-First | ✅ PASS | spec.md complete with 6 user stories, 29 requirements |
| Declarative Architecture | ✅ PASS | API contracts defined in OpenAPI format |
| Progressive Elaboration | ✅ PASS | Building on Phase II foundation |
| AI-Agent Autonomy | ✅ PASS | Claude Code generates all code |
| Type Safety | ✅ PASS | SQLModel + Pydantic (backend), TypeScript strict (frontend) |
| Test-Driven Validation | ✅ PASS | Test cases defined in spec, tasks will include tests |
| Stateless Service Pattern | ✅ PASS | Conversation state in database, not memory |
| MCP Pattern | ✅ PASS | 5 mandatory tools defined per constitution |
| Tech Stack Compliance | ✅ PASS | OpenAI Agents SDK, MCP SDK, ChatKit per constitution |

**Constitution Gates**: All passed. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Technology decisions (complete)
├── data-model.md        # Entity definitions (complete)
├── quickstart.md        # Setup guide (complete)
├── contracts/
│   ├── chat-api.yaml    # OpenAPI specification (complete)
│   └── mcp-tools.yaml   # MCP tool definitions (complete)
├── checklists/
│   └── requirements.md  # Spec validation checklist (complete)
└── tasks.md             # Implementation tasks (pending /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Existing (Phase II)
│   │   ├── user.py          # Existing (Phase II)
│   │   ├── conversation.py  # NEW: Conversation model
│   │   └── message.py       # NEW: Message model
│   ├── services/
│   │   ├── task_service.py       # Existing (Phase II)
│   │   ├── auth_service.py       # Existing (Phase II)
│   │   ├── conversation_service.py  # NEW: Conversation CRUD
│   │   └── chat_service.py       # NEW: AI chat orchestration
│   ├── mcp/
│   │   ├── __init__.py      # NEW: MCP package
│   │   ├── server.py        # NEW: MCP server setup
│   │   └── tools.py         # NEW: 5 MCP tool implementations
│   ├── api/
│   │   ├── tasks.py         # Existing (Phase II)
│   │   ├── auth.py          # Existing (Phase II)
│   │   ├── chat.py          # NEW: Chat endpoints
│   │   └── conversations.py # NEW: Conversation endpoints
│   └── main.py              # Updated: Add new routes
├── migrations/
│   └── 003_add_chat_tables.sql  # NEW: Database migration
└── tests/
    ├── test_mcp_tools.py    # NEW: MCP tool tests
    ├── test_chat_service.py # NEW: Chat service tests
    └── test_chat_api.py     # NEW: Chat API tests

frontend/
├── src/
│   ├── components/
│   │   ├── Chat.tsx         # NEW: ChatKit wrapper
│   │   ├── ChatMessage.tsx  # NEW: Message display
│   │   └── ChatInput.tsx    # NEW: Message input
│   ├── hooks/
│   │   └── useChat.ts       # NEW: Chat state hook
│   ├── lib/
│   │   └── chat-api.ts      # NEW: Chat API client
│   └── app/
│       └── chat/
│           └── page.tsx     # NEW: Chat page route
└── tests/
    └── chat.test.tsx        # NEW: Chat component tests
```

**Structure Decision**: Web application structure (Option 2) - extending existing Phase II monorepo with new modules for chat functionality.

## Complexity Tracking

> No violations requiring justification. All design decisions align with constitution.

## Component Architecture

### Backend Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        API LAYER                                 │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │  /api/chat   │  │ /api/conversations│  │  /api/tasks     │   │
│  │  (NEW)       │  │      (NEW)        │  │  (Existing)     │   │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬────────┘   │
└─────────┼──────────────────┼─────────────────────┼──────────────┘
          │                  │                      │
          ▼                  ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │ ChatService  │  │ConversationService│ │  TaskService    │   │
│  │    (NEW)     │  │      (NEW)        │  │  (Existing)     │   │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬────────┘   │
└─────────┼──────────────────┼─────────────────────┼──────────────┘
          │                  │                      │
          │    ┌─────────────┘                      │
          │    │                                    │
          ▼    ▼                                    │
┌─────────────────────────────────────────────────────────────────┐
│                       MCP LAYER                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    MCP Server                              │  │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────────┐             │  │
│  │  │ add_task │ │list_tasks │ │complete_task │             │  │
│  │  └────┬─────┘ └─────┬─────┘ └──────┬───────┘             │  │
│  │       │             │              │                      │  │
│  │  ┌────┴─────┐ ┌─────┴────┐                               │  │
│  │  │delete_   │ │update_   │  ◄── All tools call           │  │
│  │  │task      │ │task      │      TaskService              │  │
│  │  └──────────┘ └──────────┘                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │ Conversation │  │     Message      │  │     Task        │   │
│  │   (NEW)      │  │     (NEW)        │  │   (Existing)    │   │
│  └──────────────┘  └──────────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        PAGE LAYER                                │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │  /chat       │  │   /dashboard     │  │     /           │   │
│  │  (NEW)       │  │   (Existing)     │  │   (Existing)    │   │
│  └──────┬───────┘  └──────────────────┘  └─────────────────┘   │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT LAYER                               │
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │    Chat      │  │   ChatMessage    │  │   ChatInput     │   │
│  │  (ChatKit)   │  │     (NEW)        │  │     (NEW)       │   │
│  └──────┬───────┘  └──────────────────┘  └─────────────────┘   │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      HOOK LAYER                                  │
│  ┌──────────────┐  ┌──────────────────┐                        │
│  │   useChat    │  │    useAuth       │                        │
│  │    (NEW)     │  │   (Existing)     │                        │
│  └──────┬───────┘  └──────────────────┘                        │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API LAYER                                  │
│  ┌──────────────┐  ┌──────────────────┐                        │
│  │  chat-api    │  │      api         │                        │
│  │    (NEW)     │  │   (Existing)     │                        │
│  └──────────────┘  └──────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Database & Models
1. Create database migration for Conversation and Message tables
2. Implement Conversation SQLModel
3. Implement Message SQLModel
4. Create ConversationService with CRUD operations

### Phase 2: MCP Server & Tools
1. Set up MCP server with Official MCP SDK
2. Implement add_task tool
3. Implement list_tasks tool
4. Implement complete_task tool
5. Implement delete_task tool
6. Implement update_task tool
7. Unit tests for all tools

### Phase 3: Chat Service & API
1. Implement ChatService with OpenAI Agents SDK integration
2. Create chat API endpoint (POST /api/{user_id}/chat)
3. Create conversation API endpoints (list, get, delete)
4. Integration tests for chat flow

### Phase 4: Frontend Chat UI
1. Install and configure OpenAI ChatKit
2. Create Chat component wrapper
3. Create useChat hook for state management
4. Create chat-api client
5. Create /chat page route
6. Connect to backend API

### Phase 5: Integration & Validation
1. End-to-end testing of full chat flow
2. Statelessness validation (server restart test)
3. User isolation testing
4. Performance testing (response times)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenAI API rate limits | Implement retry logic with exponential backoff |
| ChatKit domain allowlist delay | Deploy frontend first, document setup steps |
| MCP SDK compatibility | Pin versions, test integration early |
| Long AI response times | Implement streaming, show typing indicator |

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chat response time | p95 < 3s | Backend metrics |
| Task operation time | p95 < 200ms | Backend metrics |
| Intent accuracy | > 90% | Manual testing with sample phrases |
| Statelessness | 100% | Server restart test |
| Test coverage | > 90% | pytest/jest coverage reports |

## Dependencies

### External Services
- OpenAI API (Agents SDK)
- Neon PostgreSQL (existing)
- Better Auth (existing)

### New Packages
**Backend**:
- `openai-agents` - AI orchestration
- `mcp` - Official MCP SDK

**Frontend**:
- `@openai/chatkit` - Chat UI components

## Related Documents

- [Specification](./spec.md) - Feature requirements
- [Research](./research.md) - Technology decisions
- [Data Model](./data-model.md) - Entity definitions
- [Chat API Contract](./contracts/chat-api.yaml) - OpenAPI spec
- [MCP Tools Contract](./contracts/mcp-tools.yaml) - Tool definitions
- [Quickstart](./quickstart.md) - Setup guide

## Next Steps

Run `/sp.tasks` to generate detailed implementation tasks with test cases.
