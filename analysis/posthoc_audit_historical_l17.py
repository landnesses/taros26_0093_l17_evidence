#!/usr/bin/env python3
"""Post-hoc audit of the frozen 20-task historical L17 snapshot.

This script does not regenerate or replace the poster-era CSV files. It reads
the separately retained request archive and emits an additive audit summary.
The raw request archive is not distributed in the public repository.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import re

import numpy as np


REQUEST_RE = re.compile(r"request_(\d+)_(\d+)")
N9926 = 9926


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--bursts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-repeats", type=int, default=20_000)
    parser.add_argument("--shift-repeats", type=int, default=50_000)
    parser.add_argument("--seed", type=int, default=20260819)
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def prompt_from(metadata: dict) -> str:
    prompt = (
        metadata.get("raw_prompt")
        or metadata.get("prompt")
        or metadata.get("tokenization", {}).get("raw_prompt")
        or metadata.get("tokenization", {}).get("debug", {}).get("cleaned_text")
        or ""
    )
    if prompt:
        return str(prompt).strip()
    full = str(metadata.get("tokenization", {}).get("debug", {}).get("full_prompt", ""))
    if full.startswith("Task:"):
        return full.split(", State:", 1)[0].replace("Task:", "").strip()
    return ""


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def exact_sign_flip_p(effects: np.ndarray) -> float:
    observed = abs(float(effects.mean()))
    n = len(effects)
    extreme = 0
    total = 1 << n
    block = 1 << 15
    bits = np.arange(n, dtype=np.uint64)
    for start in range(0, total, block):
        codes = np.arange(start, min(start + block, total), dtype=np.uint64)[:, None]
        signs = 1.0 - 2.0 * ((codes >> bits) & 1).astype(np.float64)
        means = (signs @ effects) / n
        extreme += int(np.count_nonzero(np.abs(means) >= observed - 1e-15))
    return extreme / total


def task_effects(
    values_by_task: dict[int, np.ndarray], masks_by_task: dict[int, np.ndarray]
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    log_effects = []
    ratios = []
    tasks = []
    for task in sorted(values_by_task):
        values = values_by_task[task]
        mask = masks_by_task[task]
        if not mask.any() or mask.all():
            continue
        log_values = np.log1p(values)
        log_effects.append(float(log_values[mask].mean() - log_values[~mask].mean()))
        ratios.append(float(values[mask].mean() / values[~mask].mean()))
        tasks.append(task)
    return np.asarray(log_effects), np.asarray(ratios), tasks


def summarize_effect(
    effects: np.ndarray,
    ratios: np.ndarray,
    tasks: list[int],
    rng: np.random.Generator,
    repeats: int,
) -> dict:
    samples = rng.integers(0, len(effects), size=(repeats, len(effects)))
    bootstrap = effects[samples].mean(axis=1)
    return {
        "n_task_rollouts": len(effects),
        "task_indices": tasks,
        "positive_task_log_effects": int(np.count_nonzero(effects > 0)),
        "mean_task_log1p_difference": float(effects.mean()),
        "bootstrap_ci95_task_log1p_difference": [
            float(np.quantile(bootstrap, 0.025)),
            float(np.quantile(bootstrap, 0.975)),
        ],
        "exact_two_sided_task_sign_flip_p": exact_sign_flip_p(effects),
        "median_task_raw_mean_ratio": float(np.median(ratios)),
    }


def circular_shift_p(
    values_by_task: dict[int, np.ndarray],
    masks_by_task: dict[int, np.ndarray],
    observed: float,
    rng: np.random.Generator,
    repeats: int,
) -> float:
    tables = []
    for task in sorted(values_by_task):
        values = np.log1p(values_by_task[task])
        mask = masks_by_task[task]
        if not mask.any() or mask.all():
            continue
        effects = []
        for shift in range(len(mask)):
            shifted = np.roll(mask, shift)
            effects.append(float(values[shifted].mean() - values[~shifted].mean()))
        tables.append(np.asarray(effects))
    null = np.zeros(repeats, dtype=np.float64)
    for table in tables:
        null += table[rng.integers(0, len(table), size=repeats)]
    null /= len(tables)
    return float((1 + np.count_nonzero(np.abs(null) >= abs(observed))) / (repeats + 1))


def main() -> None:
    args = parse_args()
    event_rows = read_rows(args.events)
    burst_rows = read_rows(args.bursts)

    request_dirs = sorted(
        (path for path in args.run_root.glob("request_*") if REQUEST_RE.fullmatch(path.name)),
        key=lambda path: int(REQUEST_RE.fullmatch(path.name).group(1)),
    )
    values_by_task: dict[int, list[float]] = {}
    top_by_task: dict[int, list[int]] = {}
    layer_top_by_task: dict[int, list[np.ndarray]] = {}
    p99_values = []
    p99_without_n9926 = []
    task = 0
    previous_prompt = None
    for request_dir in request_dirs:
        metadata = json.loads((request_dir / "metadata.json").read_text(encoding="utf-8"))
        prompt = prompt_from(metadata)
        if prompt != previous_prompt:
            task += 1
            previous_prompt = prompt
            values_by_task[task] = []
            top_by_task[task] = []
            layer_top_by_task[task] = []
        with np.load(request_dir / "arrays.npz", allow_pickle=False) as archive:
            full_l17 = np.asarray(
                archive["model_vlm_ffn_activation_summary_max_positive_values"]
            )[0, 0].astype(np.float64)
            layer_top = np.asarray(
                archive["model_vlm_ffn_activation_top_positive_values"]
            )[:, 0, :].max(axis=1).astype(np.float64)
        values_by_task[task].append(float(full_l17[N9926]))
        top_by_task[task].append(int(np.argmax(full_l17)))
        layer_top_by_task[task].append(layer_top)
        p99_values.append(float(np.percentile(full_l17, 99)))
        p99_without_n9926.append(float(np.percentile(np.delete(full_l17, N9926), 99)))

    values_by_task_np = {key: np.asarray(value) for key, value in values_by_task.items()}
    top_all = np.concatenate([np.asarray(top_by_task[key]) for key in sorted(top_by_task)])
    layer_top_all = np.concatenate(
        [np.asarray(layer_top_by_task[key]) for key in sorted(layer_top_by_task)], axis=0
    )

    all_masks = {key: np.zeros(len(value), dtype=bool) for key, value in values_by_task_np.items()}
    complete_masks = {key: np.zeros(len(value), dtype=bool) for key, value in values_by_task_np.items()}
    censored_rows = []
    for row in event_rows:
        task_index = int(row["task_index"])
        start = int(row["close_chunk"]) - 1
        end = int(row["release_chunk"])
        all_masks[task_index][start:end] = True
        right_censored = (
            end == len(values_by_task_np[task_index])
            and float(row["release_gripper_mean"]) > 0.1
        )
        if right_censored:
            censored_rows.append(
                {
                    "task_index": task_index,
                    "event": int(row["event"]),
                    "close_chunk": int(row["close_chunk"]),
                    "archived_end_chunk": int(row["release_chunk"]),
                    "archived_end_mean_a7": float(row["release_gripper_mean"]),
                }
            )
        else:
            complete_masks[task_index][start:end] = True

    candidate_masks = {
        key: np.zeros(len(value), dtype=bool) for key, value in values_by_task_np.items()
    }
    for row in burst_rows:
        candidate_masks[int(row["task_index"])][int(row["chunk"]) - 1] = True

    rng = np.random.default_rng(args.seed)
    all_effects, all_ratios, all_tasks = task_effects(values_by_task_np, all_masks)
    complete_effects, complete_ratios, complete_tasks = task_effects(
        values_by_task_np, complete_masks
    )
    candidate_effects, candidate_ratios, candidate_tasks = task_effects(
        values_by_task_np, candidate_masks
    )

    result = {
        "schema": "taros26_0093.historical_l17_posthoc_audit.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "post_hoc_additive_audit_not_manuscript_evidence",
        "inputs": {
            "request_archive_publicly_distributed": False,
            "request_count": len(request_dirs),
            "task_rollout_count": len(values_by_task_np),
            "events_csv_sha256": file_sha256(args.events),
            "bursts_csv_sha256": file_sha256(args.bursts),
            "first_request_directory": request_dirs[0].name,
            "last_request_directory": request_dirs[-1].name,
        },
        "n9926_rank_baseline": {
            "rank1_all_chunks": int(np.count_nonzero(top_all == N9926)),
            "all_chunks": len(top_all),
            "rank1_candidate_chunks": int(
                sum(
                    np.count_nonzero(
                        np.asarray(top_by_task[key])[candidate_masks[key]] == N9926
                    )
                    for key in sorted(top_by_task)
                )
            ),
            "candidate_chunks": int(sum(mask.sum() for mask in candidate_masks.values())),
            "interpretation": (
                "Rank-1 occurrence in retained candidates is not an enrichment result "
                "because N9926 is rank 1 in nearly every archived chunk."
            ),
        },
        "absolute_layer_scale_descriptor": {
            "median_l17_top1": float(np.median(layer_top_all[:, 17])),
            "largest_non_l17_layer_median_top1": float(
                max(np.median(layer_top_all[:, layer]) for layer in range(17))
            ),
            "median_per_chunk_l17_to_strongest_non_l17_top1_ratio": float(
                np.median(layer_top_all[:, 17] / layer_top_all[:, :17].max(axis=1))
            ),
            "warning": (
                "Raw activation scales are layer dependent; this is a descriptive "
                "amplitude discontinuity, not a calibrated cross-layer effect size."
            ),
        },
        "action_window_independent_of_activation": {
            "all_archived_windows": summarize_effect(
                all_effects, all_ratios, all_tasks, rng, args.bootstrap_repeats
            ),
            "complete_release_observed_windows_only": summarize_effect(
                complete_effects,
                complete_ratios,
                complete_tasks,
                rng,
                args.bootstrap_repeats,
            ),
            "all_windows_taskwise_circular_shift_p": circular_shift_p(
                values_by_task_np,
                all_masks,
                float(all_effects.mean()),
                rng,
                args.shift_repeats,
            ),
            "shift_null": (
                "Two-sided task-balanced circular shifts preserve each task's N9926 "
                "series, event-mask coverage, and spacing while randomizing phase."
            ),
        },
        "selection_conditioned_descriptor": {
            "warning": (
                "Candidate chunks were selected partly from L17 statistics; this "
                "contrast is descriptive and must not be used as confirmatory evidence."
            ),
            "candidate_vs_other": summarize_effect(
                candidate_effects,
                candidate_ratios,
                candidate_tasks,
                rng,
                args.bootstrap_repeats,
            ),
        },
        "right_censoring": {
            "complete_threshold_defined_events": len(event_rows) - len(censored_rows),
            "episode_boundary_censored_events": len(censored_rows),
            "rows": censored_rows,
            "interpretation": (
                "The historical release_chunk field stores the observation boundary "
                "for these rows. It is not an observed A7<=0.1 release."
            ),
        },
        "p99_n9926_sensitivity": {
            "pearson_r_n9926_vs_p99": float(
                np.corrcoef(
                    np.concatenate([values_by_task_np[key] for key in sorted(values_by_task_np)]),
                    np.asarray(p99_values),
                )[0, 1]
            ),
            "mean_relative_absolute_p99_change_after_removal": float(
                np.mean(
                    np.abs(np.asarray(p99_values) - np.asarray(p99_without_n9926))
                    / np.maximum(np.abs(np.asarray(p99_values)), 1e-12)
                )
            ),
            "interpretation": (
                "N9926 co-varies with the L17 upper tail but one neuron has little "
                "numerical influence on a 99th percentile over 16,384 neurons."
            ),
        },
        "inference_limits": [
            "post-hoc analysis of one rollout per task",
            "action-command timing, not physical contact or acquisition labels",
            "no causal intervention",
            "no task-success prediction claim",
            "candidate-conditioned contrasts are selection biased",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
