## Thresholds Verification Plan (SIM_TOP1_TH, DIFF_TOP12_TH)

Goal
- Validate that the new Thresholds UI and persistence reliably drive gate decisions and that concurrent LL-M calls deliver correct final results for all A-text rows.

Assumptions
- The gating logic is: gate_pass = (len(top3_data) >= 1) and top1_val is finite and top1_val >= sim_top1_th and (top1_val - top2_val) >= diff_top12_th.
- On gate_pass, final result for the row is the Top1 candidate with an AI score derived from top1_val.
- On gate_fail, the row is moved to pending LL-M execution and later combined into final results.

Test Dataset (small, deterministic)
- A_texts: 6 examples
- B_items: 6 items with some duplicates; ensure at least one gate_pass true and one gate_pass false scenario.

Test Matrix (thresholds):
- Case 1 (Default): sim_top1_th=0.92, diff_top12_th=0.035
- Case 2 (Higher threshold): sim_top1_th=0.95, diff_top12_th=0.05
- Case 3 (Lower threshold): sim_top1_th=0.90, diff_top12_th=0.03

Validation Steps
- Step 1: Start app and open Thresholds panel. Set to Case 1, Save configuration. Run a test batch with 6 A-text rows. Confirm:
  - Gate PASS occurrences are logged with top1/top2/diff values and candidate counts.
  - Some rows show Stage1 direct match (已匹配) without LL-M; other rows show LL-M-pending when they go to batch LL-M, then later final results show 已匹配/未达标.
- Step 2: Switch to Case 2, Save, re-run the test. Expect gate_pass fewer cases (more rows go to LL-M).
- Step 3: Switch to Case 3, Save, re-run. Expect gate_pass more frequently than Case 1.
- Step 4: Check final results: total rows equals A-text total; all rows have a final status not LL-M-pending; progress reaches 100% when all final rows are written to Excel.
- Step 5: Validate config persistence by restarting the app and re-loading thresholds; ensure sliders reflect previous saved values.

Acceptance Criteria (for each run)
- All rows have final status either 已匹配 or 未达标 in the output Excel.
- 匹配进度达到 100% only after final rows are written.
- Thresholds changes persist via config.json and UI controls reflect the persisted values on startup.

Run-time Notes
- If you observe any discrepancy in final statuses, inspect Gate decision logs and the final_results population points in run_match to confirm the final mapping from pending LL-M results to final results.

Authors: Prometheus - Planning Agent
