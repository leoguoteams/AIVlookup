# Draft: Wave 1 Task D — Gate integration prep (Scheme A)

## Objective
- Prepare the integration point for using sim_top1_th in gating decisions (Scheme A).

## Deliverables
- API contract snippet describing in-memory access pattern for sim_top1_th
- Notes on how Wave 2 will wire UI changes into gating decisions
- Considerations: hot-reload vs restart, consistency guarantees

## Acceptance Criteria
- [ ] Clear interface for reading sim_top1_th from in-memory config
- [ ] Documentation of expected runtime behavior on updates

## Next Steps
- Wave 2: Wire actual gating logic to use the in-memory value
