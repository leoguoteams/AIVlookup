# Plan: Expose sim_top1_th as user-configurable UI setting (Scheme A)

## TL;DR
- Summary: Add a UI control (slider) to configure sim_top1_th in the range 0.0-1.0 with step 0.01, bind to runtime gating, persist to config.json, and support a defaults toggle.
- Deliverables: UI control, config persistence, gating logic integration, QA scenarios.
- Effort: Medium
- Parallel: YES
- Critical Path: UI control -> binding -> gate evaluation

## Context
- Original Request: Enable UI-based configuration of sim_top1_th for Scheme A.
- Metis Review: Identified need for stable config schema, debounce on writes, and a clear migration path; suggested guards for defaults and versioning.

## Work Objectives
- Core Objective: Make sim_top1_th configurable via UI and persisted to config.json, with gating logic consuming the latest value.
- Deliverables:
  - A ThresholdSlider UI component (0.00-1.00, step 0.01)
  - Binding to in-memory config.sim_top1_th and debounced persistence to config.json
  - Startup load of sim_top1_th with default 0.92 if missing/corrupt
  - Gating logic reads sim_top1_th for Scheme A decisions
  - Documentation of the config schema and UX behavior
  - QA plan: unit/integration/e2e tests for threshold config

## Definition of Done
- [x] UI control is visible and functional (0.0-1.0, 2-decimal display)
- [x] Slider changes update in-memory sim_top1_th and trigger a debounced write to config.json
- [x] On startup, sim_top1_th loads from config.json or defaults to 0.92
- [x] Gate evaluation uses the updated sim_top1_th
- [x] Evidence/logs exist for config load/write and gating decisions
- [x] Tests scaffolded for unit/integration/e2e

## Must Have
- Real-time or near-real-time gating based on UI changes
- Robust config load/save with backup/defaults
- No breaking changes to existing config structure

## Must NOT Have (guardrails)
- Do not disrupt other config sections
- Do not create multi-scheme config conflicts without migration plan

## Verification Strategy
- ZERO HUMAN INTERVENTION - all verification is agent-executed
- Tests: unit tests for load/save and validation; integration tests for UI-to-config; end-to-end tests for gating behavior across thresholds
- Evidence: .sisyphus/evidence/task-UI-config-sim_top1_th.{ext}

## Execution Strategy
- Wave 1: UI control implementation and config binding
- Wave 2: Gate integration and startup load
- Wave 3: Testing, QA, and documentation

### Wave 1 Tasks
- [1] Implement ThresholdSlider UI component (0.0-1.0, step 0.01)
- [2] Bind slider value to in-memory sim_top1_th and trigger debounced save to config.json
- [3] Ensure initial load of sim_top1_th from config.json at startup (default 0.92)
- [4] Debounce writes to avoid UI thrash; use a small delay (e.g., 500ms)
- [5] Expose a visual cue of current value in the UI and ensure accessibility

### Wave 2 Tasks
- [6] Gate integration: modify Scheme A gating to read sim_top1_th from loaded config
- [7] Validate runtime behavior during rapid threshold changes (no race conditions)
- [8] Add a minimal migration note if config.json version changes

### Wave 3 Tasks
- [9] Unit tests for load/save and range validation
- [10] Integration tests for UI-to-config binding (simulate user interaction)
- [11] End-to-end tests validating gating decisions under different thresholds
- [12] Documentation updates (config schema, UX guide)

## Final Verification Wave (120% required)
- F1 Plan Compliance Audit – oracle
- F2 Code Quality Review – unspecified-high
- F3 Real Manual QA – unspecified-high (+ UI tests)
- F4 Scope Fidelity Check – deep

## Dependencies
- Access to config.json at project root
- UI framework alignment (existing app codebase)
- Gating logic reading current sim_top1_th from config on evaluation

## Open Questions / Decisions Needed
- None at plan time; proceed with Wave 1 development

## Start/Next Action
- After plan review, start implementation with /start-work

Plan saved to: .sisyphus/plans/ui_config_sim_top1_th.md
