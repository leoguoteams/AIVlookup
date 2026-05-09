# Plan: Wave 1 Execution — ThresholdSlider UI & Config Binding (Scheme A)

## TL;DR
- Objective: Implement ThresholdSlider UI for sim_top1_th, bind to in-memory config, debounce and persist to config.json, enable startup load, and prepare gating integration.
- Deliverables: ThresholdSlider UI component, in-memory binding, debounced config writes, startup config load, gating read integration, and basic QA scaffolds.
- Effort: Medium
- Parallel: YES
- Timeline: Wave 1 focuses on UI, config binding, and startup loading; Wave 2 will integrate gating and testing.

## Context
- Plan aligned with .sisyphus/plans/ui_config_sim_top1_th.md. This Wave specifically delivers the UI control and config wiring.

## Work Objectives (Wave 1 scope)
- Core objective: Provide a user-facing slider to configure sim_top1_th (0.0-1.0, step 0.01) and ensure changes flow into runtime gating via in-memory config with debounced persistence to config.json.
- Deliverables:
  - ThresholdSlider UI component scaffold
  - In-memory config.sim_top1_th bound to UI
  - Debounced save to config.json (atomic write)
  - Startup load of sim_top1_th from config.json with default 0.92
  - Gate read path ready to consume updated value (no gating change in code yet)
- QA plan scaffold for the UI-to-config binding

## Definition of Done (Wave 1)
- [x] ThresholdSlider component spec created (UI contract: value, onChange)
- [x] UI binding to in-memory sim_top1_th implemented in plan-level design (not code)
- [x] Debounced persistence plan defined (300ms)
- [x] Startup load plan defined (config.json -> sim_top1_th, default 0.92)
- [x] Gate integration hook prepared (read sim_top1_th in gating path)
- [x] Documentation updated with Wave 1 scope and acceptance criteria

## Acceptance Criteria (Wave 1)
- UI slider renders and accepts values in [0.0, 1.0] with 0.01 steps
- Changing the slider updates in-memory sim_top1_th and schedules a debounced write to config.json
- On startup, sim_top1_th is loaded from config.json (default 0.92 if missing or invalid)
- Gate evaluation path is prepared to use the updated sim_top1_th value
- Basic tests scaffolds described for load/save and UI-binding exist

## Tasks (Wave 1)
- [1] UI ThresholdSlider component design
  - What to do: Define contract (value, onChange), render slider, accessible label, show current value
  - QA: Happy path value changes, min/max, accessibility checks
  - Parallelization: YES | Wave 1
- [2] In-memory config binding specification
  - What to do: Define config.sim_top1_th in memory; prepare setter/getter hooks for UI
  - QA: Binding updates reflect in gating logic (conceptual)
- [3] Debounced persistence plan
  - What to do: Debounce writes to config.json (300ms), atomically write, persist only sim_top1_th
  - QA: Debounce behavior, single write per burst, file integrity checks
- [4] Startup load plan
  - What to do: Load config.json at startup; parse sim_top1_th; default if missing/corrupt
  - QA: Startup value equals config, fallback to 0.92 if absent
- [5] Gate integration prep
  - What to do: Ensure gating reads sim_top1_th from in-memory config; no code changes yet to gating logic
  - QA: Gate decision path ready to consume threshold
- [6] Documentation & plan alignment
  - What to do: Update Wave 1 notes in plan doc; capture edge cases and rollback strategy

## Verification Strategy
- Tests: unit tests for load/save logic and value clamping; integration test plan for UI-binding; end-to-end test plan for gating behavior across threshold values (to be implemented in Wave 2)
- Evidence: plan artifacts and logs created in repository

## Handoff and Next Steps
- After Wave 1 completion, proceed to Wave 2: Gate integration, live validation, and end-to-end tests

Plan created for Wave 1 execution. Plan file saved to: .sisyphus/plans/ui_config_sim_top1_th_wave1.md
