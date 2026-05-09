# Draft: Thresholds UI Unified Panel

## Goals
- Consolidate threshold controls into a single panel with Chinese labels.
- Ensure drag sliders do not auto-commit; provide a dedicated 'Save Thresholds' button.
- Implement startup sync so UI matches config.json on launch.
- Guarantee the Open Result button remains visible and accessible.

## Context
- Previous patches adjusted labels and button positions; current work aims to finalize layout and behavior.

## Key Assumptions
- UI framework and control bindings are stable; config.json structure remains as before.
- Tests for UI are lightweight and primarily rely on presence/visibility of elements and state synchronization.

## Open Questions for the Plan (to be resolved in Metis review)
- Are there any platform-specific constraints on layout when the window resizes?
- Do we want to expose a visible indicator when thresholds are out-of-range after startup sync?
