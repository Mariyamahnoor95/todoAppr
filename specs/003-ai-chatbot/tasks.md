# Tasks: AI Chatbot for Todo Management

**Input**: Design documents from `/specs/003-ai-chatbot/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/ (complete)

**Tests**: Included as per constitution requirement (Test-Driven Validation principle)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`
- **Migrations**: `backend/migrations/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and database setup

- [x] T001 Install backend dependencies (openai-agents, mcp) in backend/pyproject.toml
- [ ] T002 Install frontend dependencies (@openai/chatkit) in frontend/package.json
- [x] T003 [P] Add OPENAI_API_KEY and CONVERSATION_HISTORY_LIMIT to backend/.env.example
- [x] T004 [P] Add NEXT_PUBLIC_CHAT_API_URL to frontend/.env.example
- [x] T005 Create database migration script in backend/migrations/003_add_chat_tables.sql

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Data Models

- [x] T006 [P] Create Conversation SQLModel in backend/src/models/conversation.py
- [x] T007 [P] Create Message SQLModel with MessageRole enum in backend/src/models/message.py
- [x] T008 Update backend/src/models/__init__.py to export Conversation and Message

### MCP Server Infrastructure

- [x] T009 Create MCP package init in backend/src/mcp/__init__.py
- [x] T010 Implement MCP server setup with Official MCP SDK in backend/src/mcp/server.py
- [x] T011 Create MCP tools module structure in backend/src/mcp/tools.py

### Services Infrastructure

- [x] T012 Create ConversationService with CRUD operations in backend/src/services/conversation_service.py

### API Infrastructure

- [x] T013 Create chat request/response Pydantic schemas in backend/src/api/schemas.py (append to existing)
- [x] T014 Update backend/src/main.py to include new chat and conversation routes

### Tests Infrastructure

- [x] T015 [P] Create MCP tools test file structure in backend/tests/test_mcp_tools.py
- [x] T016 [P] Create chat service test file structure in backend/tests/test_chat_service.py
- [x] T017 [P] Create chat API test file structure in backend/tests/test_chat_api.py

**Checkpoint**: Foundation ready - MCP server and data models in place, user story implementation can begin

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1) MVP

**Goal**: Users can add tasks by typing natural language commands like "Add a task to buy groceries"

**Independent Test**: Send message "Add a task to buy groceries" via POST /api/{user_id}/chat, verify task is created and chatbot confirms

### Tests for User Story 1

- [x] T018 [P] [US1] Write unit test for add_task MCP tool in backend/tests/test_mcp_tools.py
- [x] T019 [P] [US1] Write integration test for "Add task" chat flow in backend/tests/test_chat_api.py

### Implementation for User Story 1

- [x] T020 [US1] Implement add_task MCP tool in backend/src/mcp/tools.py
- [x] T021 [US1] Create ChatService with OpenAI Agents SDK integration in backend/src/services/chat_service.py
- [x] T022 [US1] Implement POST /api/{user_id}/chat endpoint in backend/src/api/chat.py
- [x] T023 [US1] Add chat router to main.py routes in backend/src/main.py
- [x] T024 [US1] Run tests and verify add_task flow works end-to-end

**Checkpoint**: User Story 1 complete - Users can add tasks via chat

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1) MVP

**Goal**: Users can ask to see their tasks with commands like "Show me all my tasks" or "What's pending?"

**Independent Test**: Send message "Show me my tasks" via POST /api/{user_id}/chat, verify chatbot responds with task list

### Tests for User Story 2

- [x] T025 [P] [US2] Write unit test for list_tasks MCP tool in backend/tests/test_mcp_tools.py
- [x] T026 [P] [US2] Write integration test for "List tasks" chat flow in backend/tests/test_chat_api.py

### Implementation for User Story 2

- [x] T027 [US2] Implement list_tasks MCP tool with status filter in backend/src/mcp/tools.py
- [x] T028 [US2] Update ChatService to handle list_tasks responses in backend/src/services/chat_service.py
- [x] T029 [US2] Run tests and verify list_tasks flow works end-to-end

**Checkpoint**: User Stories 1 & 2 complete - Core add/view functionality working

---

## Phase 5: User Story 3 - Complete Task via Natural Language (Priority: P2)

**Goal**: Users can mark tasks complete with commands like "Mark task 1 as complete"

**Independent Test**: Send message "Mark task 1 as complete" via POST /api/{user_id}/chat, verify task status changes

### Tests for User Story 3

- [x] T030 [P] [US3] Write unit test for complete_task MCP tool in backend/tests/test_mcp_tools.py
- [ ] T031 [P] [US3] Write integration test for "Complete task" chat flow in backend/tests/test_chat_api.py

### Implementation for User Story 3

- [x] T032 [US3] Implement complete_task MCP tool in backend/src/mcp/tools.py
- [x] T033 [US3] Run tests and verify complete_task flow works end-to-end

**Checkpoint**: User Story 3 complete - Users can complete tasks via chat

---

## Phase 6: User Story 4 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can delete tasks with commands like "Delete task 2" or "Remove the grocery task"

**Independent Test**: Send message "Delete task 2" via POST /api/{user_id}/chat, verify task is removed

### Tests for User Story 4

- [x] T034 [P] [US4] Write unit test for delete_task MCP tool in backend/tests/test_mcp_tools.py
- [ ] T035 [P] [US4] Write integration test for "Delete task" chat flow in backend/tests/test_chat_api.py

### Implementation for User Story 4

- [x] T036 [US4] Implement delete_task MCP tool in backend/src/mcp/tools.py
- [x] T037 [US4] Run tests and verify delete_task flow works end-to-end

**Checkpoint**: User Story 4 complete - Users can delete tasks via chat

---

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P2)

**Goal**: Users can update tasks with commands like "Change task 1 to 'Buy organic groceries'"

**Independent Test**: Send message "Change task 1 to 'Buy organic groceries'" via POST /api/{user_id}/chat, verify task is updated

### Tests for User Story 5

- [x] T038 [P] [US5] Write unit test for update_task MCP tool in backend/tests/test_mcp_tools.py
- [ ] T039 [P] [US5] Write integration test for "Update task" chat flow in backend/tests/test_chat_api.py

### Implementation for User Story 5

- [x] T040 [US5] Implement update_task MCP tool in backend/src/mcp/tools.py
- [x] T041 [US5] Run tests and verify update_task flow works end-to-end

**Checkpoint**: All 5 MCP tools complete - Full task CRUD via chat available

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P3)

**Goal**: Conversation history is preserved across sessions so users can continue where they left off

**Independent Test**: Start conversation, close browser, return, verify previous messages are displayed

### Tests for User Story 6

- [x] T042 [P] [US6] Write unit test for ConversationService CRUD in backend/tests/test_conversation_service.py
- [ ] T043 [P] [US6] Write integration test for conversation persistence in backend/tests/test_chat_api.py

### Implementation for User Story 6

- [ ] T044 [US6] Implement conversation history loading in ChatService in backend/src/services/chat_service.py
- [ ] T045 [US6] Implement GET /api/{user_id}/conversations endpoint in backend/src/api/conversations.py
- [ ] T046 [US6] Implement GET /api/{user_id}/conversations/{conversation_id} endpoint in backend/src/api/conversations.py
- [ ] T047 [US6] Implement DELETE /api/{user_id}/conversations/{conversation_id} endpoint in backend/src/api/conversations.py
- [ ] T048 [US6] Add conversations router to main.py routes in backend/src/main.py
- [ ] T049 [US6] Run tests and verify conversation persistence works across requests

**Checkpoint**: User Story 6 complete - Conversation history persists in database

---

## Phase 9: Frontend Chat UI

**Goal**: Users have a chat interface to interact with the AI chatbot

**Independent Test**: Navigate to /chat, send a message, see response displayed

### Frontend Components

- [x] T050 [P] Create chat API client in frontend/src/lib/chat-api.ts
- [x] T051 [P] Create useChat hook for state management in frontend/src/hooks/useChat.ts
- [x] T052 [P] Create ChatMessage component in frontend/src/components/ChatMessage.tsx
- [x] T053 [P] Create ChatInput component in frontend/src/components/ChatInput.tsx
- [x] T054 Create Chat component wrapper with ChatKit in frontend/src/components/Chat.tsx
- [x] T055 Create /chat page route in frontend/src/app/chat/page.tsx
- [x] T056 Add chat navigation link to dashboard in frontend/src/app/dashboard/page.tsx
- [x] T057 Create frontend chat component tests in frontend/src/__tests__/chat.test.tsx

**Checkpoint**: Frontend complete - Users can interact with chatbot via web UI

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Integration validation, error handling, and documentation

### Integration & Validation

- [ ] T058 Run full end-to-end test: add, list, complete, delete, update tasks via chat
- [ ] T059 Validate statelessness: restart server mid-conversation, verify no data loss
- [ ] T060 Validate user isolation: User A cannot access User B's conversations
- [ ] T061 Test error handling: empty messages, invalid conversation IDs, task not found

### Error Handling & Edge Cases

- [x] T062 [P] Implement empty message validation in chat endpoint
- [x] T063 [P] Implement long message handling (>1000 chars)
- [x] T064 [P] Implement AI service unavailable error handling
- [ ] T065 [P] Implement ambiguous command clarification (ask user to specify)

### Documentation

- [ ] T066 Update backend README with chat API documentation
- [ ] T067 Update frontend README with chat UI setup instructions
- [ ] T068 Document ChatKit domain allowlist setup process

### Performance & Security

- [ ] T069 [P] Add rate limiting to chat endpoint
- [ ] T070 [P] Add input sanitization for chat messages
- [ ] T071 Verify test coverage meets 90% requirement

**Checkpoint**: Core Phase III AI Chatbot feature complete

---

## Phase 11: Reusable Intelligence (Constitution Pillar 9)

**Purpose**: Capture reusable patterns, skills, and blueprints for future phases

### Reusable Backend Patterns

- [ ] T072 [P] Create MCPServerBlueprint base class in backend/src/mcp/blueprint.py
- [ ] T073 [P] Create ConversationManager reusable class in backend/src/services/conversation_manager.py
- [ ] T074 [P] Create agent instructions builder in backend/src/mcp/agent_instructions.py
- [ ] T075 [P] Create MCPToolTestBase in backend/tests/base/test_mcp_base.py
- [ ] T076 [P] Create ChatAPITestBase in backend/tests/base/test_chat_base.py

### Reusable Frontend Patterns

- [ ] T077 [P] Extract reusable useChat hook interface in frontend/src/hooks/useChat.ts
- [ ] T078 [P] Create ChatConfig type definitions in frontend/src/types/chat.ts

### Claude Code Skills

- [ ] T079 [P] Create implement-chat-feature skill in .specify/skills/implement-chat-feature.skill.yaml
- [ ] T080 [P] Create implement-mcp-tool skill in .specify/skills/implement-mcp-tool.skill.yaml

### Documentation & Templates

- [ ] T081 Document reusable patterns in specs/003-ai-chatbot/reusable-patterns.md (complete)
- [ ] T082 [P] Create MCP tool template in .specify/templates/mcp-tool-template.py
- [ ] T083 [P] Create chat service template in .specify/templates/chat-service-template.py
- [ ] T084 Update constitution with Phase III lessons learned in .specify/memory/constitution.md

**Checkpoint**: Phase III complete with reusable intelligence captured

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 but can run in parallel
  - US3, US4, US5 are P2 and can run in parallel after US1/US2
  - US6 is P3 and can run in parallel with other stories
- **Frontend (Phase 9)**: Can start after Foundational; integrates with completed backend
- **Polish (Phase 10)**: Depends on User Stories and Frontend being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational - Independently testable
- **User Story 4 (P2)**: Can start after Foundational - Independently testable
- **User Story 5 (P2)**: Can start after Foundational - Independently testable
- **User Story 6 (P3)**: Can start after Foundational - Independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- MCP tool before ChatService integration
- ChatService before API endpoint
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T006, T007 (models) can run in parallel
- T015, T016, T017 (test structures) can run in parallel

**Phase 3-8 (User Stories)**:
- All test tasks marked [P] within a story can run in parallel
- US1 and US2 can be developed in parallel (both P1)
- US3, US4, US5 can be developed in parallel (all P2)
- US6 can be developed in parallel with US3-US5

**Phase 9 (Frontend)**:
- T050, T051, T052, T053 (independent components) can run in parallel

**Phase 10 (Polish)**:
- T062, T063, T064, T065 (error handling) can run in parallel
- T069, T070 (security) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all models in parallel:
Task: "Create Conversation SQLModel in backend/src/models/conversation.py"
Task: "Create Message SQLModel with MessageRole enum in backend/src/models/message.py"

# Launch all test structures in parallel:
Task: "Create MCP tools test file structure in backend/tests/test_mcp_tools.py"
Task: "Create chat service test file structure in backend/tests/test_chat_service.py"
Task: "Create chat API test file structure in backend/tests/test_chat_api.py"
```

---

## Parallel Example: User Story 1 & 2 (P1 Stories)

```bash
# Both P1 stories can start simultaneously after Phase 2:

# Developer A - User Story 1:
Task: "Write unit test for add_task MCP tool in backend/tests/test_mcp_tools.py"
Task: "Implement add_task MCP tool in backend/src/mcp/tools.py"

# Developer B - User Story 2:
Task: "Write unit test for list_tasks MCP tool in backend/tests/test_mcp_tools.py"
Task: "Implement list_tasks MCP tool in backend/src/mcp/tools.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test add/view tasks independently
6. Deploy/demo if ready - users can add and view tasks via chat

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test → MVP Core (add tasks)
3. Add User Story 2 → Test → MVP Complete (add + view tasks)
4. Add User Stories 3-5 → Test → Full CRUD via chat
5. Add User Story 6 → Test → Conversation persistence
6. Add Frontend → Test → Full user experience
7. Polish → Production ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + 3 (add + complete)
   - Developer B: User Story 2 + 4 (view + delete)
   - Developer C: User Story 5 + 6 (update + persistence)
   - Developer D: Frontend (after Phase 2)
3. Stories complete and integrate independently

---

## Summary

| Phase | Tasks | Stories Covered |
|-------|-------|-----------------|
| Phase 1: Setup | T001-T005 (5 tasks) | - |
| Phase 2: Foundational | T006-T017 (12 tasks) | - |
| Phase 3: US1 Add Task | T018-T024 (7 tasks) | P1 |
| Phase 4: US2 View Tasks | T025-T029 (5 tasks) | P1 |
| Phase 5: US3 Complete Task | T030-T033 (4 tasks) | P2 |
| Phase 6: US4 Delete Task | T034-T037 (4 tasks) | P2 |
| Phase 7: US5 Update Task | T038-T041 (4 tasks) | P2 |
| Phase 8: US6 Persistence | T042-T049 (8 tasks) | P3 |
| Phase 9: Frontend | T050-T057 (8 tasks) | All |
| Phase 10: Polish | T058-T071 (14 tasks) | All |
| Phase 11: Reusable Intelligence | T072-T084 (13 tasks) | Pillar 9 |

**Total Tasks**: 84
**MVP Scope**: Phases 1-4 (29 tasks) - Users can add and view tasks via chat
**Full Feature**: Phases 1-10 (71 tasks) - Complete AI chatbot with frontend
**With Reusable Patterns**: All 84 tasks - Full feature + reusable intelligence captured

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MCP tools are stateless - all state in database
- ChatService orchestrates AI agent and MCP tool calls
- Phase 11 ensures patterns are captured for future reuse (Constitution Pillar 9)
