# Draft: Wave 1 Task A — UI ThresholdSlider scaffolding (Scheme A)

## Objective
- Define the contract for a ThresholdSlider UI component to configure sim_top1_th (range 0.0-1.0, step 0.01).

## Deliverables
- UI contract: props { value: number, onChange: (v:number)=>void }
- UI rendering plan: min=0.0, max=1.0, step=0.01, live value display, accessible labels
- File path proposal: src/ui/schemeA/ThresholdSlider.tsx (skeleton)
- Binding plan: outline how it will connect to in-memory config.sim_top1_th (Wave 2 implementation)

## Data & Interfaces
- In-memory config: { sim_top1_th: number }
- Interaction: user changes slider -> onChange(newVal) -> update in-memory state

## Acceptance Criteria
- [ ] Contract defined with 2 props
- [ ] Slider renders with correct bounds and precision
- [ ] Accessibility considerations documented
- [ ] Binding to in-memory config described (no code changes in Wave 1)

## Risks & Mitigations
- UI mismatch with runtime gating: ensure clear interface contract and preview in UI doc
- Precision: ensure 0.01 step is enforced in UI and persists correctly

## Next Steps
- Wave 2: Implement the component and wire to actual config/state
