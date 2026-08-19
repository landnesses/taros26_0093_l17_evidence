# Evidence scope and limitations

This document is the authoritative reading boundary for the TAROS 2026
submission 93 evidence snapshot. It applies to every CSV, report, script,
figure, video, audit result, count, and repository description.

## Snapshot identity and chronology

This repository is a frozen, manuscript-stage exploratory evidence artifact.
Its historical analysis unit is one archived run split into 20 consecutive,
prompt-defined task executions. The manuscript-scale analysis was formed on
2026-06-24. Additive audit files are explicitly identified as post-submission
provenance or sensitivity checks and must not be treated as evidence available
to the frozen manuscript analysis.

This repository is not a live project record and does not document project
status. It makes no statement about the existence, absence, status, direction,
or results of any work outside the defined snapshot. No inference should be
drawn from that silence.

## Experimental and statistical units

- The highest-level observed units are **20 task executions**, with one
  execution for each prompt-defined task in this archived run.
- The 1,311 policy chunks are repeated observations nested within those 20
  executions, not 1,311 independent trials.
- The 99 gripper-command windows are repeated, action-derived windows nested
  within executions, not 99 independent task replications.
- The 137 retained burst candidates are deduplicated, selection-conditioned
  candidates derived from event-window maxima and L17 peak/rank criteria. They
  are not 137 independent or prospectively sampled events.
- The 20 tasks are heterogeneous benchmark prompts and are not documented as a
  probability sample from a wider task population.

Accordingly, chunk-, window-, or candidate-level counts must not be used as an
independent-sample denominator. The post-hoc audit uses task-balanced summaries
where stated, but one execution per task still does not estimate repeat-run,
seed, robot, model, environment, or deployment variability.

## Exploratory selection and multiplicity

- L17 was selected during exploratory screening. The public archive does not
  contain a complete reproducible L0-L16 screening record or a prospective
  layer-selection protocol. It therefore does not establish that L17 is unique
  or statistically superior to every other layer.
- N9926 is rank 1 in 1,310 of all 1,311 archived chunks. Its occurrence in
  137/137 retained candidates is numerically true but is not candidate
  enrichment and does not identify a uniquely semantic neuron.
- Candidate selection partly uses L17 statistics. Candidate-versus-other
  contrasts are selection-conditioned descriptors and must not be presented as
  confirmatory tests of the same signal used to select candidates.
- Figure 1 Task 02 was an illustrative, post-hoc example selection. No
  contemporaneous written selection rationale was recovered. Its short,
  successful, single-complete-event trace explains its compact visual value but
  does not make it prespecified, random, or representative.

No family-wise claim is supported for an unrecorded universe of inspected
layers, neurons, tasks, figures, thresholds, or candidate definitions.

## Action-command and event semantics

- A7 is a policy gripper command, not a physical contact, force, lift,
  acquisition, retention, or object-state label.
- RoboLab applies the upstream `A7 > 0.5` boundary to each individual action
  timestep to choose the binary gripper command. Figure 1 uses this executor
  boundary only as an illustrative closure-command-onset anchor.
- The archived formal event detector is different: it starts a window when
  chunk mean A7 is at least 0.6 and ends at the first subsequent chunk with mean
  A7 at most 0.1.
- Figure 1's `grasp onset` text is operational shorthand for the onset of
  executor-interpreted closure commands. It is not the formal `close event` and
  does not establish a physical grasp.
- Of the 99 archived windows, 92 have an observed A7 release-threshold endpoint.
  Seven are right-censored at the episode boundary. Their historical
  `release_chunk` value is an observation boundary, not an observed release.

These command-derived windows may be used for action-timing alignment only.
They must not be relabeled as contact, grasp acquisition, successful pickup, or
release ground truth.

## Task outcomes and score semantics

- Outcome labels are task-level benchmark annotations. They do not provide
  event-level labels for contact, grasp, lift, acquisition, retention, or
  release.
- The historical table contains 8 successes, 10 failures, and 2 partial-score
  failures. This is a descriptive partition of 20 executions, not a calibrated
  success-prediction dataset.
- Task 15 has consistent binary success labels but incompatible scalar meanings:
  the recording-side progress scorer stores 0.5 while the historical joined
  table stores `score_total = 1.0`. Scalar-score analyses must exclude Task 15
  or report an explicit sensitivity analysis.
- Large L17 bursts occur in both successful and unsuccessful executions. The
  snapshot does not support using burst magnitude, N9926, or event count as a
  task-success detector.

An absence of a relationship in this small exploratory snapshot must not be
generalized into evidence that no relationship can exist in another sample.

## Figures, videos, and recovered artifacts

- Per-task figures and videos are views of the same 20 executions represented
  in the task tables. They do not add an independent validation population.
- Videos provide visual execution context but do not replace omitted
  request-level activation records or create event-level ground truth.
- The recovered pre-specialization Task 02 four-row figure and the specialized
  paper Figure 1 plot the same underlying 10-chunk trace. Their side-by-side
  comparison demonstrates a visualization-layer difference, not a new
  experiment or changed event table.
- The specialized two-row plotting source was not recovered. The standard
  four-row image was recovered as an original Git blob and reproduced
  byte-for-byte using the historical script, retained raw requests, and the
  matching Matplotlib environment.

## Reproducibility and data availability

The repository publishes the historical analysis script, derived CSVs,
reports, figures, execution videos, and additive audit outputs. The original
request archives are not public. They include the request-level arrays required
to recompute activation summaries from source.

Therefore:

- public artifacts support inspection of the published derived values and
  evidence lineage;
- the public repository alone does not provide an end-to-end rerun from raw
  model requests;
- hashes of retained non-public inputs establish file identity, not public data
  availability or independent reproduction;
- historical report references to per-task output folders describe the
  generating analysis layout and are not a complete inventory of this public
  repository.

The additive audit preserves the historical CSVs, reports, figures, videos, and
analysis script unchanged. Where an archived report lacks a later-added
provenance qualification, this document and `PROVENANCE.md` define the permitted
interpretation; they do not retroactively alter the archived result.

## Unsupported inferences

Nothing in this snapshot establishes:

- physical contact, grasp acquisition, lift, retention, or release detection;
- causal control of policy behavior by L17 or N9926;
- a uniquely semantic "grasp neuron";
- L17 uniqueness or superiority across all layers;
- prospective event detection or calibrated task-success prediction;
- robustness across repeated seeds, rollouts, checkpoints, models, robots,
  morphologies, simulators, environments, or task distributions;
- cross-robot transfer, adaptation, or validation;
- real-world deployment performance or safety.

The phrase "for Cross-Robot Adaptation" in the manuscript title states a
research motivation. It is not evidence that this frozen snapshot contains a
cross-robot experiment.

## Statements supported within this boundary

Subject to all limitations above, the public snapshot supports inspection of:

- the historical counts of 20 executions, 1,311 chunks, 99 command-derived
  windows, and 137 retained candidates;
- the historical L17 P99 and candidate tables for the defined run;
- the descriptive fact that N9926 is the top activated L17 neuron in nearly all
  chunks, including all retained candidates;
- a task-balanced post-hoc description of increased N9926 magnitude around
  action-command windows, without semantic or causal interpretation;
- the descriptive observation that burst magnitude alone does not separate the
  archived task outcomes;
- Figure 1's exact source-image lineage and its distinct 0.5 executor and 0.6
  formal event anchors;
- the documented right-censoring and Task 15 scalar-score qualifications.
