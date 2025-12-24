---

description: "Task list for CLI Todo Application"
---

# Tasks: CLI Todo Application

**Input**: Design documents from `/specs/001-cli-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as specified in the feature requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan
- [X] T002 [P] Create src directory and initialize main.py file
- [X] T003 [P] Create tests directory with unit and integration subdirectories
- [X] T004 [P] Setup project configuration files (pyproject.toml, .gitignore)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [X] T005 Define Task class/data structure in src/main.py
- [X] T006 [P] Implement in-memory storage using Python list/dict in src/main.py
- [X] T007 [P] Implement unique ID generation for tasks in src/main.py
- [X] T008 [P] Setup command-line argument parsing using argparse in src/main.py
- [X] T009 Create error handling framework in src/main.py
- [X] T010 [P] Setup basic application structure with main function in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Tasks (Priority: P1) 🎯 MVP

**Goal**: Implement ability for users to add new tasks with title and description to the todo list

**Independent Test**: The application should allow a user to add a new task via command-line input, and that task should appear in the task list.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Unit test for adding tasks with title and description in tests/unit/test_main.py
- [X] T012 [P] [US1] Unit test for unique ID assignment in tests/unit/test_main.py
- [X] T013 [P] [US1] Integration test for add command in tests/integration/test_cli.py

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement add_task function in src/main.py
- [X] T015 [P] [US1] Implement command-line handler for add command in src/main.py
- [X] T016 [US1] Add validation for required title field in src/main.py
- [X] T017 [US1] Add success/error messaging for add operation in src/main.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Implement ability for users to view all tasks with their status indicators

**Independent Test**: The application should display a list of all tasks with their status (complete/incomplete) and ID.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [X] T018 [P] [US2] Unit test for viewing all tasks in tests/unit/test_main.py
- [X] T019 [P] [US2] Unit test for displaying task status indicators in tests/unit/test_main.py
- [X] T020 [P] [US2] Integration test for list command in tests/integration/test_cli.py

### Implementation for User Story 2

- [X] T021 [P] [US2] Implement list_tasks function in src/main.py
- [X] T022 [P] [US2] Implement command-line handler for list command in src/main.py
- [X] T023 [US2] Format task display with ID, title, description, and completion status in src/main.py
- [X] T024 [US2] Handle case when no tasks exist in src/main.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Tasks Complete/Incomplete (Priority: P2)

**Goal**: Implement ability for users to mark tasks as complete or incomplete by ID

**Independent Test**: The application should allow a user to mark a specific task as complete or incomplete by its ID.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [X] T025 [P] [US3] Unit test for marking tasks complete in tests/unit/test_main.py
- [X] T026 [P] [US3] Unit test for marking tasks incomplete in tests/unit/test_main.py
- [X] T027 [P] [US3] Integration test for complete/incomplete commands in tests/integration/test_cli.py

### Implementation for User Story 3

- [X] T028 [P] [US3] Implement mark_task_complete function in src/main.py
- [X] T029 [P] [US3] Implement mark_task_incomplete function in src/main.py
- [X] T030 [US3] Implement command-line handlers for complete/incomplete commands in src/main.py
- [X] T031 [US3] Add validation for valid task IDs in src/main.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Implement ability for users to update the details of existing tasks by ID

**Independent Test**: The application should allow a user to update a task's title and/or description by its ID.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

- [X] T032 [P] [US4] Unit test for updating task title in tests/unit/test_main.py
- [X] T033 [P] [US4] Unit test for updating task description in tests/unit/test_main.py
- [X] T034 [P] [US4] Unit test for handling non-existent task updates in tests/unit/test_main.py
- [X] T035 [P] [US4] Integration test for update command in tests/integration/test_cli.py

### Implementation for User Story 4

- [X] T036 [P] [US4] Implement update_task function in src/main.py
- [X] T037 [P] [US4] Implement command-line handler for update command in src/main.py
- [X] T038 [US4] Add validation for valid task IDs in src/main.py
- [X] T039 [US4] Preserve task ID and status during updates in src/main.py

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P3)

**Goal**: Implement ability for users to delete tasks by ID

**Independent Test**: The application should allow a user to delete a specific task by its ID.

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

- [X] T040 [P] [US5] Unit test for deleting existing tasks in tests/unit/test_main.py
- [X] T041 [P] [US5] Unit test for handling non-existent task deletions in tests/unit/test_main.py
- [X] T042 [P] [US5] Integration test for delete command in tests/integration/test_cli.py

### Implementation for User Story 5

- [X] T043 [P] [US5] Implement delete_task function in src/main.py
- [X] T044 [P] [US5] Implement command-line handler for delete command in src/main.py
- [X] T045 [US5] Add validation for valid task IDs in src/main.py
- [X] T046 [US5] Add appropriate success/error messaging in src/main.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Edge Cases & Error Handling

**Goal**: Handle all specified edge cases and error conditions

- [X] T047 [P] Implement validation for invalid commands in src/main.py
- [X] T048 [P] Implement handling for invalid task IDs in src/main.py
- [X] T049 [P] Implement handling for empty titles when adding tasks in src/main.py
- [X] T050 [P] Add comprehensive error messaging in src/main.py

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T051 [P] Documentation updates in src/main.py docstrings
- [X] T052 Code cleanup and refactoring
- [X] T053 [P] Additional unit tests (if requested) in tests/unit/
- [X] T054 Security hardening
- [X] T055 Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Edge Cases (Phase 8)**: Depends on all user stories being complete
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Core functionality before command-line handlers
- Validation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Unit test for adding tasks with title and description in tests/unit/test_main.py"
Task: "Unit test for unique ID assignment in tests/unit/test_main.py"
Task: "Integration test for add command in tests/integration/test_cli.py"

# Launch all implementation for User Story 1 together:
Task: "Implement add_task function in src/main.py"
Task: "Implement command-line handler for add command in src/main.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add tasks)
4. Complete Phase 4: User Story 2 (View tasks)
5. **STOP and VALIDATE**: Test User Stories 1 and 2 together
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence