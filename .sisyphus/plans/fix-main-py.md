# Fix main.py: AI Semantic Matching Tool

## TL;DR
> **Summary**: Fix critical bugs in main.py - result collection, error handling, resource leaks, thread safety, and column indexing
> **Deliverables**: Fixed main.py with all bugs resolved, unit tests added
> **Effort**: Short
> **Parallel**: NO
> **Critical Path**: Fix result bug → Fix file naming → Fix error handling → Fix remaining issues → Tests

## Context
### Original Request
User wants to optimize main.py and confirmed: **1-to-1 matching only (top 1 result per A entry)**

### Interview Summary
- User clarified: no "一对多前3条" - only the most similar match
- All 7 identified issues to be fixed
- No existing test infrastructure

### Metis Review (gaps addressed)
- Added guardrails: scope limited to main.py fixes only
- Added edge case: handle when B table has fewer entries than top_k requested
- Added acceptance criteria: all verifiable via commands

## Work Objectives
### Core Objective
Fix all bugs in main.py to make it production-ready with correct 1-to-1 matching behavior

### Deliverables
1. Fixed result collection bug (scores now used, top-1 selected)
2. Fixed file naming (remove "一对多前3条" reference)
3. Replaced bare except clauses with specific exception handling
4. Fixed resource leak (json.load with context manager)
5. Fixed thread-unsafe GUI updates (use root.after())
6. Fixed column indexing (support multi-letter columns like "AA", "AB")
7. Connected temperature variable to API call
8. Added unit tests for core functions

### Definition of Done
- [ ] `python -c "from main import clean_text, cos_sim, col_to_idx; print('OK')"` passes
- [ ] pytest tests/ -v shows all tests pass
- [ ] No bare `except:` in code (verified via grep)
- [ ] temperature slider actually changes API payload value

### Must Have
- All 7 bugs fixed
- 1-to-1 matching behavior (top-1 only)
- Safe threading with GUI updates on main thread

### Must NOT Have
- No changes to unrelated files
- No UI layout changes (only bug fixes)
- No AI slop patterns (hardcoded values instead of config)

## Verification Strategy
- Test decision: tests-after (pytest)
- Framework: pytest with pytest-asyncio for async tests
- QA policy: Every fix has unit test
- Evidence: test output logs

## Execution Strategy
### Parallel Execution Waves
> Target: All tasks are sequential dependencies, single wave

Wave 1: All tasks in sequence (bug fixes have dependencies)

### Dependency Matrix
- Task 1 (result bug) must complete before task 4 (file naming) since task 4 depends on correct data flow

## TODOs

  - [x] 1. Fix result collection bug

  **What to do**: In `run_match()`, after LLM scoring completes, select the index with highest score and write that B entry's data to result. Remove placeholder `[a_txt, "", "", "", 0, "未匹配"]` - actually use the scored results.

  **Must NOT do**: Do not keep the placeholder pattern; do not write empty strings to result

  **Recommended Agent Profile**:
  - Category: quick - Reason: Single file, targeted fix
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: task-4 | Blocked By: none

  **References**:
  - Pattern: Lines 254-258 - current scoring loop to fix
  - Pattern: Lines 265-271 - output section that needs correct data

  **Acceptance Criteria**:
  - [ ] After fix, result row contains: [a_txt, b_name, b_spec, b_code, ai_score, status] - not empty strings

  **QA Scenarios**:
  ```
  Scenario: Top score is selected
    Tool: Bash
    Steps: Run pytest tests/test_result_collection.py -v
    Expected: Test shows highest-scored B entry is selected, not placeholder
    Evidence: .sisyphus/evidence/task-1-result-collection.{ext}

  Scenario: When all scores are 0
    Tool: Bash
    Steps: Mock LLM to return 0 for all, run matching
    Expected: Status shows "未匹配" with 0 score, no crash
    Evidence: .sisyphus/evidence/task-1-zero-scores.{ext}
  ```

  **Commit**: YES | Message: `fix: wire LLM scores into result collection for top-1 matching` | Files: ["main.py"]

- [ ] 2. Fix file naming

  **What to do**: Change output filename from "AI匹配结果_一对多前3条.xlsx" to "AI匹配结果_最匹配.xlsx" or "AI匹配结果_一对一.xlsx"

  **Must NOT do**: Do not use "前3条" or "一对多" - user confirmed 1-to-1

  **Recommended Agent Profile**:
  - Category: quick - Reason: Simple string change
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-1

  **References**:
  - Pattern: Line 265 - current filename with incorrect semantics

  **Acceptance Criteria**:
  - [ ] Output file is named with 1-to-1 semantics (no "3" or "多" in name)

  **QA Scenarios**:
  ```
  Scenario: Output filename check
    Tool: Bash
    Steps: grep "AI匹配结果" main.py
    Expected: Only one occurrence, contains "一对一" or "最匹配", no "3" or "一对多"
    Evidence: .sisyphus/evidence/task-2-filename.{ext}
  ```

  **Commit**: YES | Message: `fix: rename output file to reflect 1-to-1 matching behavior` | Files: ["main.py"]

- [ ] 3. Replace bare except clauses

  **What to do**: Replace all `except:` blocks with `except Exception as e: log_print(..., f"错误: {str(e)}")`. Locations: Lines 57, 76, 115, 231

  **Must NOT do**: Do not catch SystemExit or KeyboardInterrupt; do not swallow errors silently

  **Recommended Agent Profile**:
  - Category: quick - Reason: Mechanical replacement, low risk
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-1

  **References**:
  - Pattern: Line 57 - `except:` in get_embeddings_with_retry
  - Pattern: Line 76 - `except:` in llm_score_with_retry
  - Pattern: Line 115 - `except:` in load_config
  - Pattern: Line 231 - `except:` in run_match file reading

  **Acceptance Criteria**:
  - [ ] `grep -n "except:" main.py` returns 0 matches
  - [ ] All exception handlers log the error message

  **QA Scenarios**:
  ```
  Scenario: No bare except remain
    Tool: Bash
    Steps: grep -n "except:" main.py
    Expected: No output (exit code 1 means no matches)
    Evidence: .sisyphus/evidence/task-3-no-bare-except.{ext}

  Scenario: Exception logging works
    Tool: Bash
    Steps: Run tests/test_exception_handling.py -v
    Expected: All tests pass, errors are logged with messages
    Evidence: .sisyphus/evidence/task-3-exception-logging.{ext}
  ```

  **Commit**: YES | Message: `fix: replace bare except with specific Exception handlers` | Files: ["main.py"]

- [ ] 4. Fix resource leak in load_config

  **What to do**: Wrap json.load in context manager: `with open(CONFIG_FILE, "r", encoding="utf-8") as f: cfg = json.load(f)`

  **Must NOT do**: Do not leave file handle open; do not use json.load without context manager

  **Recommended Agent Profile**:
  - Category: quick - Reason: Simple context manager addition
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-3

  **References**:
  - Pattern: Line 113 - current `json.load(open(...))` pattern

  **Acceptance Criteria**:
  - [ ] load_config uses `with open(...)` pattern

  **QA Scenarios**:
  ```
  Scenario: Context manager used
    Tool: Bash
    Steps: grep -A2 "def load_config" main.py | grep "with open"
    Expected: Output shows "with open" is present
    Evidence: .sisyphus/evidence/task-4-resource-leak.{ext}
  ```

  **Commit**: YES | Message: `fix: use context manager for file handle in load_config` | Files: ["main.py"]

- [ ] 5. Fix thread-unsafe GUI updates

  **What to do**: Replace `self.root.update()` calls (lines 189, 263) with `self.root.after(100, lambda: None)` or use a queue pattern. Better: use `self.root.after(0, lambda: self.progress.config(...))` to update progress on main thread.

  **Must NOT do**: Do not call root.update() from background thread; do not block UI thread

  **Recommended Agent Profile**:
  - Category: quick - Reason: Threading fix, straightforward
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-4

  **References**:
  - Pattern: Line 188-189 - progress update in load_b_embedding
  - Pattern: Line 262-263 - progress update in run_match

  **Acceptance Criteria**:
  - [ ] No `self.root.update()` calls in background threads
  - [ ] Progress updates use root.after() pattern

  **QA Scenarios**:
  ```
  Scenario: No unsafe root.update in background thread
    Tool: Bash
    Steps: grep -n "root.update" main.py (check no direct calls in load_b_embedding or run_match)
    Expected: No direct root.update() calls outside of main thread context
    Evidence: .sisyphus/evidence/task-5-thread-safe.{ext}
  ```

  **Commit**: YES | Message: `fix: use root.after() for thread-safe GUI updates` | Files: ["main.py"]

- [ ] 6. Fix column indexing for multi-letter columns

  **What to do**: Add helper function `col_to_idx(col)` that converts "A"->0, "B"->1, "Z"->25, "AA"->26, "AB"->27 etc. Use openpyxl's `column_index_from_string` or implement base-26 conversion. Replace ord()-65 pattern on lines 166-168 and 227.

  **Must NOT do**: Do not use ord(col)-65 directly; do not assume single letter columns

  **Recommended Agent Profile**:
  - Category: quick - Reason: Helper function addition
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-5

  **References**:
  - Pattern: Lines 166-168 - current ord()-65 pattern for B table columns
  - Pattern: Line 227 - current ord()-65 pattern for A table column

  **Acceptance Criteria**:
  - [ ] `col_to_idx("A")` returns 0
  - [ ] `col_to_idx("Z")` returns 25
  - [ ] `col_to_idx("AA")` returns 26
  - [ ] `col_to_idx("AB")` returns 27
  - [ ] No `ord(...)-65` pattern remains for column calculation

  **QA Scenarios**:
  ```
  Scenario: Single letter columns work
    Tool: Bash
    Steps: python -c "from main import col_to_idx; assert col_to_idx('A') == 0; assert col_to_idx('B') == 1"
    Expected: No assertion errors
    Evidence: .sisyphus/evidence/task-6-col-single.{ext}

  Scenario: Multi-letter columns work
    Tool: Bash
    Steps: python -c "from main import col_to_idx; assert col_to_idx('AA') == 26; assert col_to_idx('BA') == 52"
    Expected: No assertion errors
    Evidence: .sisyphus/evidence/task-6-col-multi.{ext}
  ```

  **Commit**: YES | Message: `feat: add col_to_idx helper for multi-letter column support` | Files: ["main.py"]

- [ ] 7. Connect temperature variable to API call

  **What to do**: Read `self.temperature.get()` in llm_score_with_retry and use it in the API payload instead of hardcoded 0.1. Either pass temperature as parameter or use a global. Simplest: add temperature parameter with default.

  **Must NOT do**: Do not hardcode temperature in API call; do not leave slider disconnected

  **Recommended Agent Profile**:
  - Category: quick - Reason: Simple parameter threading
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-6

  **References**:
  - Pattern: Line 67 - hardcoded `"temperature": 0.1`
  - Pattern: Line 107 - temperature variable definition

  **Acceptance Criteria**:
  - [ ] Temperature slider changes actual API call temperature value
  - [ ] API payload uses value from self.temperature.get()

  **QA Scenarios**:
  ```
  Scenario: Temperature parameter is used
    Tool: Bash
    Steps: Check llm_score_with_retry function signature and usage
    Expected: Function accepts temperature parameter or reads from class instance
    Evidence: .sisyphus/evidence/task-7-temperature.{ext}
  ```

  **Commit**: YES | Message: `feat: connect temperature slider to API call parameter` | Files: ["main.py"]

- [ ] 8. Add unit tests

  **What to do**: Create tests/ directory with pytest tests for:
  - test_clean_text(): verify text cleaning logic
  - test_cos_sim(): verify cosine similarity calculation
  - test_col_to_idx(): verify column index conversion (A, Z, AA, AB, BA)
  - test_result_collection(): verify top-1 selection with mock scores
  - test_exception_handling(): verify errors are logged, not swallowed

  **Must NOT do**: Do not create integration tests that require API keys; unit tests only with mocks

  **Recommended Agent Profile**:
  - Category: quick - Reason: Standard test creation
  - Skills: [] - not needed
  - Omitted: [] - none

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: none | Blocked By: task-7

  **References**:
  - Pattern: Existing main.py functions to test
  - Framework: pytest (standard Python testing)

  **Acceptance Criteria**:
  - [ ] `pytest tests/ -v` runs without errors
  - [ ] All test functions pass

  **QA Scenarios**:
  ```
  Scenario: All tests pass
    Tool: Bash
    Steps: pytest tests/ -v
    Expected: 100% pass rate, no skipped tests
    Evidence: .sisyphus/evidence/task-8-tests.{ext}
  ```

  **Commit**: YES | Message: `test: add unit tests for core functions` | Files: ["tests/test_clean_text.py", "tests/test_cos_sim.py", "tests/test_col_to_idx.py", "tests/test_result_collection.py", "tests/test_exception_handling.py"]

## Final Verification Wave (MANDATORY)
> 4 review agents run in PARALLEL. ALL must APPROVE.

- [ ] F1. Plan Compliance Audit — oracle
- [ ] F2. Code Quality Review — unspecified-high
- [ ] F3. Real Manual QA — unspecified-high
- [ ] F4. Scope Fidelity Check — deep

## Commit Strategy
- Each task commits separately with descriptive messages
- Commits are small and focused for easy rollback if needed

## Success Criteria
- All 8 tasks completed
- All F1-F4 checks pass
- Output file has 1-to-1 matching semantics
- No bare except clauses in code
- Temperature slider actually controls API temperature
- All unit tests pass
