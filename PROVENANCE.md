# Provenance and claim boundary

This repository is a deliberately narrow public snapshot of the **historical 20-task exploratory L17 analysis** associated with TAROS 2026 submission 93.

## Historical analysis unit

The archived exploratory run was split into 20 consecutive prompt-defined task executions comprising 1,311 policy requests/chunks in total. The historical analysis detected 99 gripper-command events and produced 137 deduplicated L17 burst candidates.

For event detection, the mean value of the final action dimension (A7, gripper command) within each returned action chunk was used. A close window began when mean A7 was at least 0.6 and ended at the first subsequent chunk with mean A7 at most 0.1.

Of the 99 archived windows, 92 have an observed endpoint satisfying mean
A7 <= 0.1. Seven reach the episode boundary without satisfying that criterion.
For compact historical analysis, those seven were author-adjudicated as valid
**closure-associated events** and their episode boundary was stored in the
legacy `release_chunk` field. This is a right-censoring convention: it is not an
observed release and has no implication for physical grasp, acquisition, or
task success. The seven rows and their terminal A7 values are listed in
`data/right_censored_event_adjudication.csv`. A complete-event-only sensitivity
analysis is reported in `audit/README.md`.

For L17 activity, each request contained per-neuron maximum-positive activation summaries. The layer trace used in the exploratory analysis was the 99th percentile (P99) over the 16,384 L17 FFN neuron summaries. Candidate bursts combined event-window maxima with qualifying L17 peaks/top-P99 candidates and were deduplicated by chunk.

## N9926 statement

In the archived derived outputs, N9926 is the top-activated neuron in the highest-ranked burst candidate for all 20 task executions and in all 137 deduplicated burst candidates.

The interpretation is intentionally limited: a post-hoc raw-archive audit found
N9926 rank 1 in 1,310 of all 1,311 chunks. Therefore, 137/137 is not evidence of
candidate enrichment. The relevant descriptive observation is increased N9926
magnitude around action-defined close windows. The task-balanced audit found a
median within-task raw-mean ratio of 1.2248; the effect remained 1.2134 when all
seven episode-boundary-censored windows were excluded. Exact post-hoc methods,
uncertainty, null tests, and limitations are in `audit/README.md` and
`audit/posthoc_historical_l17_audit.json`.

N9926 is not presented as a uniquely semantic or causal “grasp neuron.” Its
correlation with L17 P99 also does not mean that one neuron numerically creates
the P99 trace: removing N9926 changes P99 by only 0.33% on average.

## Outcome statement

Task-level benchmark outcomes are included only to support the exploratory observation that large L17 bursts can occur in both successful and unsuccessful executions. The public snapshot does not provide per-event physical contact, lift, or acquisition ground truth, and therefore does not support such event-level claims.

## Execution-video binding

The 40 published MP4 files are two views (`main.mp4` and `viewport.mp4`) of the same 20 historical executions represented by the public task tables and phase-overview figures. The binding was checked at the execution level, not inferred from filenames alone:

- all 20 benchmark task names and prompts match;
- all 20 recorded episode lengths map to the published policy-chunk counts using 15 action steps per chunk;
- all 20 success labels match;
- for every task, the first seven recorded action dimensions exactly match the concatenated request actions, and the recorded A7 gripper trace exactly matches the request A7 trace after the benchmark's binary threshold conversion.

One upstream outcome-semantics discrepancy is retained rather than silently
reconciled. Task 15 has `score_total = 1.0` in the historical public join, while
the RoboLab recording stores `success = true` and `score = 0.5`. This is not an
author relabeling. RoboLab used two different criteria: the termination manager
marked binary success when both configured targets were outside the plate and
detached, while the subtask scorer awarded 0.5 because only one of two
per-object place-on-table sequences was complete. The exact generator of the
historical joined scalar was not retained.

There is no binary success-label conflict: both sources mark the execution
successful, and the action-trace checks bind the video to that execution. The
two scalar semantics are not interchangeable. The historical CSV remains
unchanged; scalar-score analyses must report a sensitivity analysis or exclude
Task 15. See `audit/task15_outcome_semantics.json`.

## Figure 1 timing anchors

The representative Task 02 figure uses two related A7 anchors. Its grey
`grasp onset` marker at chunk 6 is the 0.5 executor/action boundary: mean A7 is
0.5121 and 14 of 15 returned actions exceed 0.5. The archived 99-event detector
uses the stricter chunk-mean criterion and therefore starts the formal close
window at chunk 7, where mean A7 is 0.6924. Chunk 7 is also the marked L17/N9926
burst. Chunk 10 has mean A7 0.0539 and is the formal release endpoint.

The annotation and event table therefore use different timing anchors over the
same action trace. The figure is illustrative; the historical detector and CSV
are authoritative for event counts and window statistics.

The 20 published phase-overview PNG files are the archived A7/L17 figures for those same task indices. They are descriptive same-execution views and do not add an independent validation population.

## Layer-selection limitation

L17 was selected during preliminary exploratory screening because it exhibited conspicuous sparse, high-amplitude responses near gripper-command windows. However, the historical public archive retained the L17-focused readouts used for the accepted poster, not a complete reproducible archive of the earlier L0-L16 screening process. Accordingly, this repository **does not claim that L17 is unique or statistically superior to every other layer**.

Subsequent project work post-dates the accepted exploratory poster and is intentionally outside this public snapshot.

## Raw-data boundary

The original request archives are retained separately and are not published here. They include robot state, prompts, model outputs, request metadata, and machine-specific paths. The public videos are visual records of the executions, not request-level model traces. This repository contains derived analysis artifacts and execution recordings intended to make the poster-level observations inspectable without releasing the broader project archive.

## Scope exclusions

This repository intentionally excludes all work produced after the accepted exploratory poster. That exclusion is a scope boundary, not a claim about whether subsequent analyses exist.
