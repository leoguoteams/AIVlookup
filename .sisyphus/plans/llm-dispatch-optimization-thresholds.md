## Plan Generated: llm-dispatch-optimization-thresholds

1) Objective
- Reduce LL M invocation by adding a two-stage gating mechanism with configurable similarity thresholds. Stage 1 decides when to skip LLM based on cosine similarity; Stage 2 triggers LLM only for uncertain cases. Thresholds are persisted in config and adjustable without code changes.

2) Thresholds (defaults in config.json)
- SIM_TOP1_TH: 0.92 — Top1 cosine similarity threshold. If Top1 >= SIM_TOP1_TH and the difference to Top2 >= DIFF_TOP12_TH, skip LLM and accept Top1.
- DIFF_TOP12_TH: 0.04 — Minimum gap between Top1 and Top2 to be considered decisive.

3) Gate logic
- Stage 1: Compute Top3 candidates by cosine similarity (Top1, Top2, Top3).
- Stage 1 condition to skip LLM: top1 >= SIM_TOP1_TH AND (top1 - top2) >= DIFF_TOP12_TH.
- If Stage 1 conditions met, select Top1 candidate with ai_score = int(top1 * 100).
- Stage 2: If Stage 1 not satisfied, call LLM with Top3 data (existing llm_find_best_from_top3 flow).

4) Data and artifacts
- Config: sim_top1_th, diff_top12_th added to config.json. Defaults used if not present.
- Plan artifacts: This document is the single source of truth for the gating strategy.

5) Verification / Acceptance Criteria
- A. LLM calls reduced by at least 50% on representative datasets.
- B. Overall processing time decreased (target: 60-70% of baseline depending on dataset).
- C. Final matching accuracy remains within ±2-3% of baseline on validated datasets.
- D. Thresholds are persisted in config.json and readable by the system on startup.

6) Implementation Notes
- Main changes in main.py:
  - Add defaults sim_top1_th = 0.92 and diff_top12_th = 0.04, load from config.json if present.
  - Extend save_config to write sim_top1_th and diff_top12_th.
  - In run_match, implement two-stage gating: Stage 1 uses Top1/Top2 thresholds; Stage 2 uses existing llm path.
  - Maintain existing caching and Top3 de-dup logic.

7) Validation Plan (quick-start)
- Prepare a small test dataset with a mix of clearly strong matches and borderline cases.
- Run the app with default thresholds; record LLM call count and total time.
- Tweak SIM_TOP1_TH and DIFF_TOP12_TH to observe changes in LLM activity and accuracy.

8) Handoff / Next Steps
- If results are satisfactory, consider a short A/B test to compare baseline vs gating mode in a staging environment.

Plan saved to: .sisyphus/plans/llm-dispatch-optimization-thresholds.md
