# Draft: Wave 1 Task C — Debounced persistence to config.json (sim_top1_th)

## Objective
- Define debounce strategy for writes to config.json and atomic write pattern.

## Deliverables
- Debounce plan (e.g., 300ms)
- Atomic write pattern for config.json updates (temp file + rename)
- Partial write: only sim_top1_th and minimal metadata to config.json
- Error handling and retry policy outline

## Data & Interfaces
- In-memory state: config.sim_top1_th
- Persistence entry: { "sim_top1_th": value, "version": 1, "lastUpdated": timestamp }

## Acceptance Criteria
- [ ] Debounce window defined and testable
- [ ] Atomic write implemented to avoid partial corruption
- [ ] Only sim_top1_th is updated in config.json; no churn on other keys

## Risks & Mitigations
- Write failures: log and retry on next change; keep in-memory value consistent
- Concurrent writers: serialize writes via debounce guard

## Next Steps
- Wave 2: Implement actual write logic and tests
