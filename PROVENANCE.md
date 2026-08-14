# Provenance and claim boundary

This repository is a deliberately narrow public snapshot of the **historical 20-task exploratory L17 analysis** associated with TAROS 2026 submission 93.

## Historical analysis unit

The archived exploratory run was split into 20 consecutive prompt-defined task executions comprising 1,311 policy requests/chunks in total. The historical analysis detected 99 gripper-command events and produced 137 deduplicated L17 burst candidates.

For event detection, the mean value of the final action dimension (A7, gripper command) within each returned action chunk was used. A close window began when mean A7 was at least 0.6 and ended at the first subsequent chunk with mean A7 at most 0.1.

For L17 activity, each request contained per-neuron maximum-positive activation summaries. The layer trace used in the exploratory analysis was the 99th percentile (P99) over the 16,384 L17 FFN neuron summaries. Candidate bursts combined event-window maxima with qualifying L17 peaks/top-P99 candidates and were deduplicated by chunk.

## N9926 statement

In the archived derived outputs, N9926 is the top-activated neuron in the highest-ranked burst candidate for all 20 task executions and in all 137 deduplicated burst candidates.

The interpretation is intentionally limited: N9926 is also generally high-activation, so this observation is not presented as discovery of a uniquely semantic or causal “grasp neuron.” The poster instead discusses the temporal organization of L17 activity around manipulation windows.

## Outcome statement

Task-level benchmark outcomes are included only to support the exploratory observation that large L17 bursts can occur in both successful and unsuccessful executions. The public snapshot does not provide per-event physical contact, lift, or acquisition ground truth, and therefore does not support such event-level claims.

## Execution-video binding

The 40 published MP4 files are two views (`main.mp4` and `viewport.mp4`) of the same 20 historical executions represented by the public task tables and phase-overview figures. The binding was checked at the execution level, not inferred from filenames alone:

- all 20 benchmark task names and prompts match;
- all 20 recorded episode lengths map to the published policy-chunk counts using 15 action steps per chunk;
- all 20 success labels match;
- for every task, the first seven recorded action dimensions exactly match the concatenated request actions, and the recorded A7 gripper trace exactly matches the request A7 trace after the benchmark's binary threshold conversion.

One outcome-metadata discrepancy is retained rather than silently reconciled: Task15 has `score_total = 1.0` in the public joined summary, while the recording-side episode result stores `score = 0.5`. Both sources mark the execution successful, and the action-trace identity checks above establish that the video is from the same execution. The videos therefore remain valid execution records, but they should not be used to resolve or reinterpret that scalar score.

The 20 published phase-overview PNG files are the archived A7/L17 figures for those same task indices. They are descriptive same-execution views and do not add an independent validation population.

## Layer-selection limitation

L17 was selected during preliminary exploratory screening because it exhibited conspicuous sparse, high-amplitude responses near gripper-command windows. However, the historical public archive retained the L17-focused readouts used for the accepted poster, not a complete reproducible archive of the earlier L0-L16 screening process. Accordingly, this repository **does not claim that L17 is unique or statistically superior to every other layer**.

Subsequent project work post-dates the accepted exploratory poster and is intentionally outside this public snapshot.

## Raw-data boundary

The original request archives are retained separately and are not published here. They include robot state, prompts, model outputs, request metadata, and machine-specific paths. The public videos are visual records of the executions, not request-level model traces. This repository contains derived analysis artifacts and execution recordings intended to make the poster-level observations inspectable without releasing the broader project archive.

## Scope exclusions

This repository intentionally excludes all work produced after the accepted exploratory poster. That exclusion is a scope boundary, not a claim about whether subsequent analyses exist.
