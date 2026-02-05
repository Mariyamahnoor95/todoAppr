# Research: AI Chatbot for Todo Management

**Feature**: 003-ai-chatbot
**Date**: 2026-02-05
**Status**: Complete

## Technology Decisions

### 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK for AI orchestration with MCP tool integration

**Rationale**:
- Native support for tool calling (function calling)
- Conversation context management built-in
- Streaming support for real-time responses
- Well-documented Python SDK

**Alternatives Considered**:
- LangChain: More complex, introduces additional abstraction layers
- Direct OpenAI API: Would require manual tool orchestration
- Anthropic Claude SDK: Constitution mandates OpenAI Agents SDK

**Implementation Approach**:
```python
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# Agent with MCP server connection
agent = Agent(
    name="TodoBot",
    instructions="You are a helpful todo assistant...",
    mcp_servers=[MCPServerStdio(command="python", args=["mcp_server.py"])]
)
```

### 2. MCP Server Architecture

**Decision**: Implement MCP server using Official MCP SDK with 5 stateless tools

**Rationale**:
- Constitution mandates Official MCP SDK
- Stateless design enables horizontal scaling
- Clear tool boundaries for each CRUD operation
- User isolation enforced at tool level

**Tools Specification**:

| Tool | Input Schema | Output Schema |
|------|--------------|---------------|
| `add_task` | `{user_id: str, title: str, description?: str}` | `{task_id: str, status: str, title: str}` |
| `list_tasks` | `{user_id: str, status?: "all"\|"pending"\|"completed"}` | `{tasks: Task[], count: int}` |
| `complete_task` | `{user_id: str, task_id: str}` | `{task_id: str, status: str, title: str}` |
| `delete_task` | `{user_id: str, task_id: str}` | `{task_id: str, status: str, title: str}` |
| `update_task` | `{user_id: str, task_id: str, title?: str, description?: str}` | `{task_id: str, status: str, title: str}` |

**Implementation Approach**:
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("todo-mcp")

@server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    # Create task in database
    task = await task_service.create_task(user_id, title, description)
    return {"task_id": str(task.id), "status": "created", "title": task.title}
```

### 3. Frontend Chat Interface

**Decision**: Use OpenAI ChatKit for the chat UI component

**Rationale**:
- Constitution mandates OpenAI ChatKit
- Pre-built React components for chat interfaces
- Handles message rendering, input, typing indicators
- Integrates well with Next.js

**Alternatives Considered**:
- Custom chat UI: More development effort, less polished
- Vercel AI SDK Chat: Good but not mandated by constitution

**Implementation Notes**:
- Requires domain allowlisting at `platform.openai.com/settings/organization/security/domain-allowlist`
- Environment variable: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
- Works with Server-Sent Events for streaming

### 4. Conversation Persistence Model

**Decision**: Database-backed conversation history with Message and Conversation tables

**Rationale**:
- Constitution requires stateless servers
- Enables conversation resumption across sessions
- Supports conversation context for AI responses
- Horizontal scaling (any server handles any request)

**Schema Design**:
```
Conversation:
  - id: UUID (primary key)
  - user_id: string (Better Auth user ID)
  - created_at: timestamp
  - updated_at: timestamp

Message:
  - id: UUID (primary key)
  - conversation_id: UUID (foreign key)
  - role: enum("user", "assistant")
  - content: text
  - created_at: timestamp
```

**Request Cycle**:
1. Receive user message
2. Fetch/create conversation from database
3. Load conversation history (last N messages)
4. Build context for AI agent
5. Store user message
6. Run agent with MCP tools
7. Store assistant response
8. Return response to client

### 5. Chat API Endpoint Design

**Decision**: Single POST endpoint per user for chat interactions

**Endpoint**: `POST /api/{user_id}/chat`

**Request**:
```json
{
  "conversation_id": "optional-uuid",
  "message": "Add a task to buy groceries"
}
```

**Response**:
```json
{
  "conversation_id": "uuid",
  "response": "I've added 'Buy groceries' to your tasks.",
  "tool_calls": [
    {"tool": "add_task", "result": {"task_id": "123", "title": "Buy groceries"}}
  ]
}
```

### 6. Natural Language Understanding Strategy

**Decision**: Rely on OpenAI model's built-in NLU with detailed agent instructions

**Rationale**:
- Modern LLMs excel at intent classification
- Tool descriptions guide model to appropriate actions
- No need for custom NLU pipeline
- Constitution specifies agent behavior mappings

**Agent Instructions Pattern**:
```
You are a helpful todo assistant. You help users manage their tasks through conversation.

When a user wants to:
- Add/create/remember something → use add_task tool
- See/show/list tasks → use list_tasks tool
- Complete/finish/done → use complete_task tool
- Delete/remove/cancel → use delete_task tool
- Change/update/rename → use update_task tool

Always confirm actions with friendly messages.
Handle errors gracefully and offer alternatives.
```

### 7. Error Handling Strategy

**Decision**: Graceful degradation with user-friendly error messages

**Error Categories**:

| Error Type | Response Pattern |
|------------|-----------------|
| Task not found | "I couldn't find task {id}. Would you like to see your current tasks?" |
| Ambiguous input | "I found multiple matching tasks: {list}. Which one did you mean?" |
| AI service error | "I'm having trouble processing your request. Please try again." |
| Empty message | "I didn't catch that. Could you please tell me what you'd like to do?" |
| Rate limit | "I'm receiving too many requests. Please wait a moment." |

### 8. Context Window Management

**Decision**: Load last 20 messages for context, with configurable limit

**Rationale**:
- Balances context quality with token usage
- Typical conversations are shorter than 20 exchanges
- Older messages less relevant for current intent
- Configurable via environment variable

**Implementation**:
```python
CONVERSATION_HISTORY_LIMIT = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "20"))

async def get_conversation_context(conversation_id: str) -> list[dict]:
    messages = await db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(CONVERSATION_HISTORY_LIMIT)
        .all()
    return [{"role": m.role, "content": m.content} for m in reversed(messages)]
```

## Dependencies

### Backend Dependencies (to add to pyproject.toml)

```toml
[project.dependencies]
# Existing Phase II dependencies...
openai-agents = "^0.1.0"  # OpenAI Agents SDK
mcp = "^1.0.0"            # Official MCP SDK
```

### Frontend Dependencies (to add to package.json)

```json
{
  "dependencies": {
    "@openai/chatkit": "^1.0.0"
  }
}
```

### Environment Variables

**Backend**:
```
OPENAI_API_KEY=sk-...
CONVERSATION_HISTORY_LIMIT=20
```

**Frontend**:
```
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk-...
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8000/api
```

## Security Considerations

### 1. User Isolation
- All MCP tools require `user_id` parameter
- user_id extracted from JWT, not user input
- Conversation/Message records scoped to user

### 2. Input Validation
- Message length limit (1000 characters)
- Conversation ID format validation (UUID)
- Sanitize user input before AI processing

### 3. Rate Limiting
- Per-user rate limits on chat endpoint
- OpenAI API rate limits handled with retries
- Error responses don't leak internal details

### 4. Content Safety
- OpenAI moderation API for inappropriate content
- Log and monitor for abuse patterns
- Clear escalation path for safety issues

## Performance Considerations

### 1. Response Time Target
- p95 < 3 seconds for typical operations
- Streaming reduces perceived latency
- Database queries indexed for conversation lookup

### 2. Database Optimization
- Index on (conversation_id, created_at) for message retrieval
- Index on (user_id) for conversation lookup
- Connection pooling (existing from Phase II)

### 3. Caching Strategy
- Conversation metadata cached for active sessions
- MCP tool definitions cached at startup
- JWKS cache (existing from Phase II)

## Testing Strategy

### Unit Tests
- MCP tool functions in isolation
- Message/Conversation model operations
- Natural language to tool mapping

### Integration Tests
- Chat endpoint with mock OpenAI responses
- Conversation persistence across requests
- User isolation verification

### E2E Tests (Optional)
- Full conversation flows with real AI
- Error recovery scenarios
- Multi-turn conversations

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| OpenAI Agents SDK version | Use latest stable (^0.1.0) |
| MCP SDK integration pattern | Use MCPServerStdio for subprocess communication |
| ChatKit domain setup | Deploy first, then add to allowlist |
| Conversation context limit | 20 messages (configurable) |
| Tool error format | Return structured error with suggestion |
