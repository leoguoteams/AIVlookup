# Draft: Wave 1 Task B — Startup loading plan (sim_top1_th)

## Objective
- Define startup bootstrap steps to load sim_top1_th from config.json and populate in-memory config.

## Deliverables
- Startup loader contract (pseudo-code) and integration points
- Validation criteria: version, scheme, sim_top1_th present; default to 0.92 if missing/malformed

## Data & Interfaces
- Config.json fields: { "version": 1, "scheme": "A", "sim_top1_th": 0.92 }
- In-memory representation: config.sim_top1_th

## Acceptance Criteria
- [ ] On startup, sim_top1_th is loaded with default 0.92 if missing
- [ ] Gate logic is ready to use the in-memory value from first operation after startup

## Risks & Mitigations
- Malformed config: fallback to defaults; log warning
- Migration: include schema version to support future changes

## Next Steps
- Wave 2: Wire the loaded value into gating path
