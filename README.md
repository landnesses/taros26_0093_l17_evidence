# TAROS 2026 Submission 93: L17 Exploratory Evidence

This repository contains the public evidence snapshot for the exploratory L17 activation findings reported in TAROS 2026 submission 93, **“Investigating Internal Phase Signals in VLA-Based Pick-Up Manipulation for Cross-Robot Adaptation.”**

## Scope

This public snapshot is intentionally limited to the original 20-task exploratory L17 analysis used by the poster manuscript. It supports the following reported observations:

- 20 task executions and 1,311 policy chunks;
- 99 action-defined gripper-command events;
- 137 deduplicated L17 burst candidates;
- N9926 was the top-activated neuron in the highest-ranked burst candidate for all 20 tasks and in all 137 deduplicated burst candidates;
- burst magnitude alone did not determine task success, motivating a timing/organization interpretation rather than a task-success detector.

The gripper-command event definition used in the archived analysis begins a close window when the mean gripper command in an action chunk is at least 0.6 and ends it at the first subsequent chunk whose mean gripper command is at most 0.1.

## What is not included

This repository does **not** contain work produced after the accepted exploratory poster. Those later results are outside this public snapshot and remain separately archived.

## Public evidence files

The intended public snapshot contains:

- `analysis/analyze_l17_prompt_tasks.py`: historical analysis script;
- `data/task_summary.csv`: per-task chunk/event/burst summary;
- `data/task_summary_with_outcomes.csv`: task-level benchmark outcomes joined to the exploratory summary;
- `data/all_detected_events.csv`: detected gripper-command events;
- `data/all_l17_bursts.csv`: deduplicated L17 burst candidates;
- `reports/pick_put_l17_summary.md` and `reports/outcome_l17_summary.md`: archived derived summaries;
- `figures/task01_l17_task_phase_overview.png` through `figures/task20_l17_task_phase_overview.png`: historical per-task A7/L17 phase-overview figures, including the representative Task02 figure used in the poster;
- `videos/taskXX_<BenchmarkTask>/main.mp4` and `viewport.mp4`: two views of each of the same 20 historical task executions.

See `PROVENANCE.md` for the evidence boundary and archival limitations.

## Interpretation boundary

The public evidence supports an **exploratory, correlational L17 phase-associated observation**. It does not establish that L17 is unique among layers, that the signal detects physical contact or acquisition, that it causally controls the policy, or that it predicts task success.

## Data availability note

The original request archives are not included in this public repository. They contain prompts, robot state, model outputs, request metadata, and machine-specific paths. The published videos provide visual execution context but do not replace the omitted request-level records or add new outcome annotations. This repository therefore exposes the historical derived evidence and execution recordings needed to inspect the poster-level observations without publishing the broader raw project archive.


