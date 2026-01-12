# Tasks: Phase I - In-Memory Python Console Todo Application

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks included per constitution requirement for 90%+ coverage and Test-Driven Validation pillar.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md (src/models, src/services, src/cli, tests/unit, tests/integration)
- [x] T002 Initialize Python project with UV and pyproject.toml (dependencies: pydantic>=2.0, dev: pytest>=8.0, pytest-cov>=4.0)
- [x] T003 [P] Configure pytest in pyproject.toml (testpaths, coverage requirements 90%+)
- [x] T004 [P] Create .gitignore for Python project (**pycache**, .pytest_cache, htmlcov, .coverage)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and exceptions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create Task model in src/models/task.py with Pydantic (id: int, title: str 1-200 chars, description: str 0-1000 chars, completed: bool default False)
- [x] T006 [P] Create custom exceptions in src/services/task_service.py (TaskNotFoundError, ValidationError)
- [x] T007 [P] Create module-level storage in src/services/task_service.py (\_tasks: list[Task] = [], \_next_id: int = 1)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks with title/description and view all tasks in a list. This is the minimum viable product.

**Independent Test**: Add one or more tasks and verify they appear in the task list with ID, status, title, description.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Unit test for Task model creation in tests/unit/test_task_model.py (valid task, default completed=False, empty description default)
- [x] T009 [P] [US1] Unit test for Task validation in tests/unit/test_task_model.py (empty title fails, title >200 chars fails, description >1000 chars fails)
- [x] T010 [P] [US1] Unit test for add_task in tests/unit/test_task_service.py (adds to list, assigns sequential ID, returns Task)
- [x] T011 [P] [US1] Unit test for get_all_tasks in tests/unit/test_task_service.py (returns empty list, returns all tasks)
- [x] T012 [P] [US1] Integration test for add and view workflow in tests/integration/test_full_workflow.py (add task with full details, add task with title only, view empty list, view tasks)

### Implementation for User Story 1

- [x] T013 [US1] Implement add_task(title, description) in src/services/task_service.py (creates Task, appends to \_tasks, increments \_next_id, returns Task)
- [x] T014 [US1] Implement get_all_tasks() in src/services/task_service.py (returns copy of \_tasks list)
- [x] T015 [US1] Create display_task_list(tasks) in src/cli/display.py (table format with ID, Status []/[X], Title, Description, handle empty list)
- [x] T016 [US1] Implement add_task_menu() in src/cli/menu.py (prompt for title, prompt for description, call task_service.add_task, display success or error)
- [x] T017 [US1] Implement view_tasks_menu() in src/cli/menu.py (call task_service.get_all_tasks, call display.display_task_list)
- [x] T018 [US1] Create main menu loop in src/main.py (display warning on startup, show menu options 1-6, handle option 1 and 2, exit on option 6)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can add and view tasks

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can toggle task completion status to track progress

**Independent Test**: Create tasks and toggle their completion status. Verify status changes and visual indicators update.

### Tests for User Story 2

- [x] T019 [P] [US2] Unit test for get_task_by_id in tests/unit/test_task_service.py (returns Task when found, returns None when not found)
- [x] T020 [P] [US2] Unit test for toggle_task_completion in tests/unit/test_task_service.py (toggles False→True, toggles True→False, raises TaskNotFoundError for invalid ID)
- [x] T021 [P] [US2] Integration test for mark complete workflow in tests/integration/test_full_workflow.py (mark incomplete task complete, mark complete task incomplete, error on invalid ID)

### Implementation for User Story 2

- [x] T022 [P] [US2] Implement get_task_by_id(task_id) in src/services/task_service.py (linear search in \_tasks, return Task or None)
- [x] T023 [US2] Implement toggle_task_completion(task_id) in src/services/task_service.py (find task, raise TaskNotFoundError if not found, toggle completed field, return Task)
- [x] T024 [US2] Implement toggle_completion_menu() in src/cli/menu.py (prompt for task ID, validate numeric input, call task_service.toggle_task_completion, display success or error)
- [x] T025 [US2] Integrate toggle_completion_menu into main menu loop in src/main.py (option 5)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - add, view, and mark complete

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can update task title and/or description to correct mistakes

**Independent Test**: Create a task, then modify its title and/or description. Verify updates apply correctly.

### Tests for User Story 3

- [x] T026 [P] [US3] Unit test for update_task in tests/unit/test_task_service.py (update both fields, update title only, update description only, raises TaskNotFoundError for invalid ID, validates constraints)
- [x] T027 [P] [US3] Integration test for update workflow in tests/integration/test_full_workflow.py (update both fields, partial updates, error on invalid ID)

### Implementation for User Story 3

- [x] T028 [US3] Implement update_task(task_id, title=None, description=None) in src/services/task_service.py (find task, raise TaskNotFoundError if not found, update provided fields only, return Task)
- [x] T029 [US3] Implement update_task_menu() in src/cli/menu.py (prompt for task ID, validate numeric, prompt for new title with "leave empty to keep", prompt for new description with "leave empty to keep", call task_service.update_task, display success or error)
- [x] T030 [US3] Integrate update_task_menu into main menu loop in src/main.py (option 3)

**Checkpoint**: User Stories 1, 2, AND 3 all functional - add, view, mark complete, and update

---

## Phase 6: User Story 4 - Delete Unwanted Tasks (Priority: P4)

**Goal**: Users can delete tasks to keep their list clean and focused

**Independent Test**: Create tasks, delete specific ones, verify they're removed and no longer appear

### Tests for User Story 4

- [x] T031 [P] [US4] Unit test for delete_task in tests/unit/test_task_service.py (removes task from list, raises TaskNotFoundError for invalid ID, verify task not in list after deletion)
- [x] T032 [P] [US4] Integration test for delete workflow in tests/integration/test_full_workflow.py (delete existing task, verify removed, error on invalid ID, verify other tasks remain)

### Implementation for User Story 4

- [x] T033 [US4] Implement delete_task(task_id) in src/services/task_service.py (find task, raise TaskNotFoundError if not found, remove from \_tasks list)
- [x] T034 [US4] Implement delete_task_menu() in src/cli/menu.py (prompt for task ID, validate numeric, prompt for confirmation y/n, call task_service.delete_task if confirmed, display success or cancellation or error)
- [x] T035 [US4] Integrate delete_task_menu into main menu loop in src/main.py (option 4)

**Checkpoint**: All 4 user stories functional - complete Phase I feature set (add, view, update, delete, mark complete)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and finalize the application

- [x] T036 [P] Add input validation helper in src/cli/menu.py (validate_numeric_id, validate_non_empty_string)
- [x] T037 [P] Add error message constants in src/cli/menu.py (ERROR_TASK_NOT_FOUND, ERROR_INVALID_ID, ERROR_TITLE_REQUIRED, etc.)
- [x] T038 [P] Create README.md with setup instructions (prerequisites Python 3.13+/UV, install: uv sync, run: uv run python src/main.py, test: uv run pytest)
- [x] T039 Run full test suite and verify 90%+ coverage (uv run pytest --cov=src --cov-report=term-missing)
- [x] T040 Run quickstart.md validation scenarios (manual testing of all acceptance criteria from spec.md)
- [x] T041 Fix any failing tests or coverage gaps
- [x] T042 [P] Add docstrings to all public functions (Google style per constitution)
- [x] T043 [P] Run Black formatter on all source files (black src/ tests/ --line-length 100)
- [x] T044 Final integration test for complete workflow in tests/integration/test_full_workflow.py (add→view→mark complete→update→delete→view, verify <45 seconds per SC-007)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational (Phase 2) completion
  - User stories CAN proceed in parallel if team capacity allows
  - OR sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3) → US4 (P4)
- **Polish (Phase 7)**: Depends on all user stories (Phase 3-6) being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational - No dependencies on other stories - **This is the MVP**
- **User Story 2 (P2)**: Depends on Foundational - Uses get_task_by_id (task T022) - Independent from US1 but integrates into same menu
- **User Story 3 (P3)**: Depends on Foundational - Uses get_task_by_id (task T022 from US2) - Can reuse if US2 complete, or implement independently
- **User Story 4 (P4)**: Depends on Foundational - Uses get_task_by_id (task T022 from US2) - Can reuse if US2 complete, or implement independently

**Note on get_task_by_id**: This helper function is introduced in US2 but is needed by US3 and US4. If implementing stories in parallel, US3 and US4 should wait for T022 completion, or duplicate the function.

### Within Each User Story

**Red-Green-Refactor Cycle**:

1. Tests MUST be written and FAIL before implementation (Red)
2. Implement minimum code to pass tests (Green)
3. Refactor if needed (Refactor)

**Execution Order**:

- Tests before implementation
- Models before services (US1: T005 before T013-T014)
- Services before CLI (US1: T013-T014 before T015-T018)
- Core implementation before integration (service layer before menu integration)

### Parallel Opportunities

**Setup Phase (Phase 1)**:

- T003 and T004 can run in parallel (both marked [P])

**Foundational Phase (Phase 2)**:

- T005, T006, T007 can all run in parallel (all marked [P])

**User Story 1 (Phase 3)**:

- Tests T008, T009, T010, T011, T012 can all run in parallel (all marked [P])
- Implementation: No parallel tasks (sequential dependencies)

**User Story 2 (Phase 4)**:

- Tests T019, T020, T021 can run in parallel (all marked [P])
- Implementation: T022 can run in parallel with menu work, but T023 depends on T022

**User Story 3 (Phase 5)**:

- Tests T026, T027 can run in parallel (all marked [P])

**User Story 4 (Phase 6)**:

- Tests T031, T032 can run in parallel (all marked [P])

**Polish Phase (Phase 7)**:

- T036, T037, T038, T042, T043 can all run in parallel (all marked [P])

**Cross-Story Parallelism**:

- If team has capacity, after Foundational phase (Phase 2) completes:
  - One developer can work on US1 (T008-T018)
  - Another can work on US2 (T019-T025) in parallel
  - Note: US2 needs get_task_by_id which is part of US2 work, so no US1 dependency
  - US3 and US4 should wait for US2's T022 (get_task_by_id) or implement it independently

---

## Parallel Example: User Story 1 (MVP)

```bash
# After Foundational Phase completes, run US1 tests in parallel
uv run pytest tests/unit/test_task_model.py::test_task_creation &
uv run pytest tests/unit/test_task_model.py::test_task_validation &
uv run pytest tests/unit/test_task_service.py::test_add_task &
uv run pytest tests/unit/test_task_service.py::test_get_all_tasks &
uv run pytest tests/integration/test_full_workflow.py::test_add_and_view &
wait

# Then implement US1 tasks sequentially (due to dependencies)
# T013 → T014 → T015 → T016 → T017 → T018
```

---

## Parallel Example: All User Stories (if team capacity allows)

```bash
# After Foundational Phase completes

# Developer 1: Implement US1 (MVP)
# Tasks T008-T018

# Developer 2: Implement US2 (Mark Complete) - can run in parallel with US1
# Tasks T019-T025

# After US2's T022 completes, US3 and US4 can start:

# Developer 3: Implement US3 (Update Tasks) - depends on T022
# Tasks T026-T030

# Developer 4: Implement US4 (Delete Tasks) - depends on T022
# Tasks T031-T035
```

---

## Implementation Strategy

### Minimum Viable Product (MVP)

**MVP Scope**: User Story 1 only (Phase 1 → Phase 2 → Phase 3)

**Tasks**: T001-T018 (18 tasks)

**Deliverable**: Users can add tasks and view them - basic task tracker functional

**Validation**:

- User can add task with title and description
- User can add task with title only
- User can view all tasks with ID, status, title, description
- Empty list shows "No tasks found"

### Incremental Delivery

**Iteration 1 (MVP)**: Setup + Foundational + US1 = Basic task list (T001-T018)

**Iteration 2**: Add US2 = Task completion tracking (T019-T025)

**Iteration 3**: Add US3 = Task editing (T026-T030)

**Iteration 4**: Add US4 = Task deletion (T031-T035)

**Iteration 5 (Polish)**: Finalize with documentation, full tests, validation (T036-T044)

### Testing Strategy

**Test Coverage Target**: 90%+ (per constitution requirement)

**Test Pyramid**:

- Unit tests (tests/unit/): Fast, isolated tests for models and services
- Integration tests (tests/integration/): Full workflow tests for user journeys
- No E2E tests needed for Phase I (console app)

**Red-Green-Refactor**:

- Write tests first (Red)
- Implement to pass tests (Green)
- Refactor if needed (Refactor)

**Coverage Validation**:

```bash
uv run pytest --cov=src --cov-report=term-missing --cov-report=html
open htmlcov/index.html
```

---

## Task Summary

**Total Tasks**: 44

**Task Count by Phase**:

- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (US1 - Add/View): 11 tasks (6 tests + 5 implementation)
- Phase 4 (US2 - Mark Complete): 7 tasks (3 tests + 4 implementation)
- Phase 5 (US3 - Update): 5 tasks (2 tests + 3 implementation)
- Phase 6 (US4 - Delete): 5 tasks (2 tests + 3 implementation)
- Phase 7 (Polish): 9 tasks

**Task Count by User Story**:

- US1 (P1 - MVP): 11 tasks
- US2 (P2): 7 tasks
- US3 (P3): 5 tasks
- US4 (P4): 5 tasks
- Infrastructure/Polish: 16 tasks

**Parallel Opportunities**: 21 tasks marked [P] can run in parallel with other [P] tasks in same phase

**Independent Test Criteria**:

- US1: Add and view tasks → Verify tasks appear with ID, status, title, description
- US2: Mark complete → Verify status toggles and visual indicators update
- US3: Update tasks → Verify title/description update correctly
- US4: Delete tasks → Verify tasks removed and don't appear in list

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1 only) = 18 tasks = Basic functional task tracker

---

## Next Steps

1. Review this tasks.md for completeness
2. Approve task breakdown before proceeding
3. Run `/sp.implement` to begin implementation following Red-Green-Refactor cycle
4. Start with MVP (US1) for fastest time to value
5. Incrementally add US2, US3, US4 in priority order
6. Complete with Polish phase for production readiness
