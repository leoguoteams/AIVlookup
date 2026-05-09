## Plan Generated: llm-dispatch-validation

Goal
- Introduce a small automated validation harness to compare the two modes: (1) baseline with LLM on every item, and (2) gate-based mode with configurable thresholds. The validation reports: LLM calls, total time, and final matching accuracy (agreement with baseline).

Dataset design (small, synthetic)
- Purpose: deterministic, reproducible testing of gate behavior and performance.
- A-class (texts): 8-12 short strings that simulate A 表 entries.
- B-class (candidates): 6-9 items with fields: code, name, spec, size, and a synthetic text label used for similarity.
- Example data snippet (structure, not actual run data):
  - A: ["30mm grey granite slab", "32mm grey granite slab", "Black basalt tile 20mm", ...]
  - B (candidates):
    - {code: 'G-30-1', name: '30mm Granite Grey Slab', spec: '', size: '*'}
    - {code: 'G-30-2', name: '30mm Granite Grey Slab', spec: '', size: '*'}  // duplicate for de-dup testing
    - {code: 'G-32-1', name: '32mm Granite Grey Slab', spec: '', size: '*'}
    - {code: 'G-25-1', name: '25mm Granite Grey Slab', spec: '', size: '*'}
    - {code: 'B-20-1', name: '20mm Basalt Tile', spec: '', size: '*'}

Validation harness design
- Two modes:
  1) Baseline: routine A→embedding→cosine→Top3→LLM for all items.
  2) Gate-based: same data flow, but Stage 1 uses thresholds to skip LLM when confident.
- Thresholds to validate (configurable):
  - sim_top1_th: 0.92 (default) – Top1 cosine similarity threshold.
  - diff_top12_th: 0.04 – Top1 vs Top2 difference threshold.
- Metrics collected per item:
  - llm_called: boolean
  - time_baseline: time taken for the baseline path per item
  - time_gate: time taken for the gated path per item
  - final_code_baseline: code selected by baseline
  - final_code_gate: code selected by gate path
  - agree: boolean whether final_code_gate == final_code_baseline
- Global metrics:
  - total_llm_calls_baseline
  - total_llm_calls_gate
  - total_time_baseline
  - total_time_gate
  - overall_agreement_rate = agree_count / total_items

Implementation plan (high level)
- Add a new script script/validate_llm_gate.py (off-loads to a temporary runner) that:
  - Generates or loads the dataset (A_texts, B_items) from a predefined in-repo dataset or via code-provided fixtures.
  - Configures thresholds from a small in-script config or environment variables (for quick experiments): SIM_TOP1_TH, DIFF_TOP12_TH.
  - Replays the A→embedding→cosine→Top3 logic twice: once in baseline mode (always call LLM), once in gate mode (Stage 1 gate then Stage 2 fall-back).
  - Collects per-item metrics and prints a summary to stdout and saves a CSV summary to .sisyphus/evidence/llm_gate_validation_summary.csv.
  - Creates a simple PNG chart (bar chart) showing total time and total LLM calls for both modes, saved as .sisyphus/evidence/llm_gate_validation_chart.png.

Dataflow and integration notes
- The validation script should reuse existing functions (get_embeddings_with_retry, llm_find_best_from_top3, cos_sim) when possible, but can also use local mock data to approximate behavior if embeddings are unavailable in the test environment.
- Ensure the script can run in isolation from the GUI (no tkinter required).
- The CSV and PNG artifacts live under .sisyphus/evidence/ for traceability.

Validation plan steps
- Step 1: Prepare dataset
  - Create a small in-repo dataset generator function that returns A_texts and B_items with deterministic content.
  - Example A_texts length: 10-12; B_items length: 6-8
- Step 2: Run Baseline (LLM-on-all)
  - For each A_text, compute embedding and Top3 from B via the existing pipeline and call LLM for all items.
  - Record metrics per item and aggregate totals.
- Step 3: Run Gate-based
  - Run identical dataset with gating thresholds; collect metrics per item.
- Step 4: Compare
  - Print delta of total LLM calls, total time, and agreement rate.
- Step 5: Visualization
  - Produce chart comparing Time (ms) and LLM calls across modes.
- Step 6: Validation verdict
  - If gating reduces LLM calls by >= 50% and time by >= 30% with accuracy loss <= 3%, declare success. Otherwise, suggest adjustments.

Deliverables
- .sisyphus/evidence/llm_gate_validation_summary.csv
- .sisyphus/evidence/llm_gate_validation_chart.png
- Console summary when script runs, with per-item details for traceability.

Patch plan (implementation guidance)
- Create script at scripts/validate_llm_gate.py with the described logic (import from main module where possible).
- Add in-repo small dataset fixture in a new module or within the script for deterministic runs.
- Extend .gitignore to avoid committing large artifacts; artifacts go under .sisyphus/evidence/ only during runs.
- Run validation in a separate CI job or local run to compare baseline vs gate mode on the synthetic dataset.

Notes
- This is a minimal, non-intrusive validation harness aimed at quick iteration. It does not require changing the production GUI, and can later be evolved into a proper integration test.
