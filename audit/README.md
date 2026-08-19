# Additive post-hoc audit

This directory adds provenance and sensitivity checks to the frozen historical
20-task evidence snapshot. It does not alter the poster manuscript, the four
historical CSV files, the historical analysis script, figures, or videos. The
manuscript-scale analysis was formed on 2026-06-24; this audit was added after
submission and must not be read as evidence that was available in the paper.

## N9926: baseline rank versus phase modulation

The archived statement that N9926 is rank 1 in all 137 retained candidates is
numerically correct but is not an enrichment result. A scan of all 1,311 raw
requests found N9926 rank 1 in 1,310 chunks. Its rank is therefore effectively
a baseline property of this L17 readout.

The phase-associated observation concerns magnitude, not identity or rank. A
task-balanced post-hoc audit of N9926 amplitude found:

- median within-task window/outside raw-mean ratio: 1.2248;
- mean task-level difference in `log1p(N9926)`: +0.2339, with task bootstrap
  95% interval [+0.1267, +0.3456];
- two-sided exact task-level sign-flip `p = 0.000435`;
- task-balanced circular-shift `p = 0.000240`, preserving each task's trace and
  event-mask coverage while randomizing phase.

These are post-hoc, one-rollout-per-task statistics. They support temporal
modulation around action-command windows, not semantics, causality, physical
grasp detection, or task-success prediction.

N9926 co-varies with the L17 upper tail (`r = 0.9237` against P99), but deleting
it changes P99 by only 0.33% on average. N9926 is therefore a strong readout of
the broad L17 high-activation mode, not the numerical cause of the P99 trace.

The candidate-versus-other contrast is intentionally not treated as
confirmatory because candidate selection used L17 statistics.

## Episode-boundary-censored windows

The historical detector returned 99 close-associated windows. Ninety-two have
an observed endpoint satisfying mean A7 <= 0.1. Seven reach the end of the
recorded episode without satisfying that release threshold. The historical
`release_chunk` field stores the episode boundary for those rows.

The author adjudication retains the seven rows as valid closure-associated
events because the exploratory signal was anchored primarily to gripper
closing. It does not adjudicate a release, physical grasp, acquisition, or task
success. See `data/right_censored_event_adjudication.csv`.

Excluding all seven censored windows leaves 19 task rollouts with at least one
complete event. The N9926 effect remains positive: mean task-level
`log1p(N9926)` difference +0.1958, task bootstrap 95% interval
[+0.0957, +0.3006], exact sign-flip `p = 0.00157`, and median raw-mean ratio
1.2134. This sensitivity check is still post-hoc.

## Figure 1 timing anchors

Figure 1 uses two related but distinct A7 anchors for Task 02:

- the grey `grasp onset` annotation at chunk 6 uses the 0.5 executor/action
  boundary; mean A7 is 0.5121 and 14 of 15 actions exceed 0.5;
- the archived event detector starts at chunk 7 because its formal criterion is
  chunk mean A7 >= 0.6; mean A7 is 0.6924;
- chunk 7 is also the marked L17/N9926 burst, and chunk 10 satisfies the formal
  release criterion with mean A7 0.0539.

Thus the figure and CSV refer to different declared anchors, not different
underlying traces. The figure is illustrative; the historical detector and CSV
are authoritative for the 99-event count.

## Task 15 outcome semantics

Task 15 exposes an upstream RoboLab evaluator mismatch, not an author relabeling.
The termination manager marked success when both configured targets were outside
the plate and detached. The subtask scorer assigned 0.5 because only one of two
per-object place-on-table sequences was complete. The historical public join
stores binary success and `score_total=1.0`; the exact scalar join generator was
not retained. See `task15_outcome_semantics.json`.

The binary success label is consistent across sources. The scalar score is not
semantically interchangeable across the two upstream evaluators and should not
be used without a sensitivity analysis.

## Files

- `posthoc_historical_l17_audit.json`: machine-readable results and input hashes;
- `task15_outcome_semantics.json`: Task 15 evaluator reconciliation and retained
  private-source hashes;
- `../analysis/posthoc_audit_historical_l17.py`: audit implementation;
- `../data/right_censored_event_adjudication.csv`: the seven author-adjudicated
  episode-boundary-censored event rows.
