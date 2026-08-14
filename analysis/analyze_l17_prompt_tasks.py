#!/usr/bin/env python3
"""Analyze L17 FFN phase bursts for prompt-split pick-and-put tasks."""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import math
import os
from pathlib import Path
import re
from typing import Any
import unicodedata

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DEFAULT_LOG_DIR = Path("logs/l17_pick_put_pack")
DEFAULT_OUTPUT_DIR = Path("analysis_outputs/ffn_runtime_analysis/l17_pick_put_pack")
DEFAULT_STATIC_DICT = Path("analysis_outputs/ffn_static_dictionary_filtered/candidate_neurons.jsonl")
DEFAULT_TRACKED_NEURONS = (9926, 7602, 8670, 12632, 3720, 7062, 6012, 15900, 16084)

SUMMARY_VALUES_KEY = "model_vlm_ffn_activation_summary_max_positive_values"
SUMMARY_TOKEN_KEY = "model_vlm_ffn_activation_summary_max_positive_token_indices"
SUMMARY_LAYERS_KEY = "model_vlm_ffn_activation_summary_layers"
REQUEST_RE = re.compile(r"request_(\d+)_(\d+)")

GROUP_FIELDS = {
    "action": "robotics_action_hits",
    "spatial": "spatial_hits",
    "object": "object_hits",
    "robot_state": "robot_state_hits",
}


@dataclasses.dataclass(frozen=True)
class RequestRecord:
    request_dir: Path
    request_name: str
    request_number: int
    timestamp_ns: int
    prompt: str
    state_str: str


@dataclasses.dataclass
class TaskData:
    task_index: int
    prompt: str
    slug: str
    requests: list[RequestRecord]
    max_positive: np.ndarray
    max_positive_token: np.ndarray
    final_actions: list[np.ndarray]


@dataclasses.dataclass
class StaticInfo:
    quality_score: float | str
    groups: tuple[str, ...]
    top_tokens: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--run-dir", type=Path, default=None, help="Exact run_* directory. Default: latest under log-dir.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--static-dict", type=Path, default=DEFAULT_STATIC_DICT)
    parser.add_argument("--layer", type=int, default=17)
    parser.add_argument("--close-threshold", type=float, default=0.6)
    parser.add_argument("--open-threshold", type=float, default=0.1)
    parser.add_argument("--burst-mad-threshold", type=float, default=3.0)
    parser.add_argument("--top-bursts", type=int, default=5)
    parser.add_argument("--min-peak-distance", type=int, default=2)
    parser.add_argument(
        "--tracked-neurons",
        default=",".join(str(neuron) for neuron in DEFAULT_TRACKED_NEURONS),
        help="Comma-separated L17 neurons for task overview plots.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = args.run_dir if args.run_dir is not None else discover_run_dir(args.log_dir)
    requests = load_requests(run_dir)
    prompt_blocks = split_by_prompt(requests)
    tracked_neurons = parse_int_list(args.tracked_neurons)
    static = load_static_dictionary(args.static_dict, args.layer) if args.static_dict.exists() else {}

    args.output_dir.mkdir(parents=True, exist_ok=True)
    task_rows: list[dict[str, Any]] = []
    all_event_rows: list[dict[str, Any]] = []
    all_burst_rows: list[dict[str, Any]] = []

    print(f"Run directory: {run_dir}")
    print(f"Prompt tasks: {len(prompt_blocks)}")
    for task_index, block in enumerate(prompt_blocks, start=1):
        slug = f"task_{task_index:02d}_{slugify(block[0].prompt)}"
        task = load_task_data(
            task_index=task_index,
            prompt=block[0].prompt,
            slug=slug,
            requests=block,
            layer=args.layer,
        )
        task_dir = args.output_dir / slug
        task_dir.mkdir(parents=True, exist_ok=True)
        chunk_rows = build_chunk_rows(task, static, tracked_neurons)
        event_rows = detect_gripper_events(task, args.close_threshold, args.open_threshold)
        burst_rows = detect_l17_bursts(
            task,
            static,
            event_rows,
            top_n=args.top_bursts,
            mad_threshold=args.burst_mad_threshold,
            min_peak_distance=args.min_peak_distance,
        )
        write_csv(task_dir / "l17_task_chunk_summary.csv", chunk_rows)
        write_csv(task_dir / "l17_task_events.csv", event_rows)
        write_csv(task_dir / "l17_task_bursts.csv", burst_rows)
        write_task_plot(task_dir / "l17_task_phase_overview.png", task, event_rows, burst_rows, tracked_neurons)
        write_task_report(task_dir / "l17_task_report.md", task, chunk_rows, event_rows, burst_rows)

        row = task_summary_row(task, event_rows, burst_rows)
        task_rows.append(row)
        all_event_rows.extend(add_task_fields(task, event_rows))
        all_burst_rows.extend(add_task_fields(task, burst_rows))
        print(
            f"{task_index:02d}: chunks={len(task.requests):3d} events={len(event_rows):2d} "
            f"bursts={len(burst_rows):2d} -> {task_dir}"
        )

    write_csv(args.output_dir / "task_summary.csv", task_rows)
    write_csv(args.output_dir / "all_detected_events.csv", all_event_rows)
    write_csv(args.output_dir / "all_l17_bursts.csv", all_burst_rows)
    write_root_report(args.output_dir / "pick_put_l17_summary.md", run_dir, task_rows)
    print(f"Wrote prompt-split analysis to: {args.output_dir}")


def discover_run_dir(log_dir: Path) -> Path:
    if any(log_dir.glob("request_*")):
        return log_dir
    run_dirs = sorted(path for path in log_dir.glob("run_*") if path.is_dir())
    if not run_dirs:
        raise FileNotFoundError(f"No run_* directories found under {log_dir}")
    return run_dirs[-1]


def load_requests(run_dir: Path) -> list[RequestRecord]:
    requests = []
    for request_dir in sorted(run_dir.glob("request_*")):
        parsed = parse_request_name(request_dir.name)
        if parsed is None:
            continue
        metadata_path = request_dir / "metadata.json"
        arrays_path = request_dir / "arrays.npz"
        if not metadata_path.exists() or not arrays_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        request_number, name_timestamp = parsed
        requests.append(
            RequestRecord(
                request_dir=request_dir,
                request_name=request_dir.name,
                request_number=request_number,
                timestamp_ns=int(metadata.get("timestamp_ns") or name_timestamp),
                prompt=extract_prompt(metadata),
                state_str=str(metadata.get("tokenization", {}).get("debug", {}).get("state_str", "")),
            )
        )
    return sorted(requests, key=lambda request: request.request_number)


def parse_request_name(name: str) -> tuple[int, int] | None:
    match = REQUEST_RE.search(name)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def extract_prompt(metadata: dict[str, Any]) -> str:
    prompt = (
        metadata.get("raw_prompt")
        or metadata.get("prompt")
        or metadata.get("tokenization", {}).get("raw_prompt")
        or metadata.get("tokenization", {}).get("debug", {}).get("cleaned_text")
        or ""
    )
    if prompt:
        return str(prompt).strip()
    full_prompt = str(metadata.get("tokenization", {}).get("debug", {}).get("full_prompt", ""))
    if full_prompt.startswith("Task:"):
        return full_prompt.split(", State:", 1)[0].replace("Task:", "").strip()
    return ""


def split_by_prompt(requests: list[RequestRecord]) -> list[list[RequestRecord]]:
    blocks: list[list[RequestRecord]] = []
    for request in requests:
        if not blocks or request.prompt != blocks[-1][-1].prompt:
            blocks.append([request])
        else:
            blocks[-1].append(request)
    return blocks


def load_task_data(
    *,
    task_index: int,
    prompt: str,
    slug: str,
    requests: list[RequestRecord],
    layer: int,
) -> TaskData:
    value_rows = []
    token_rows = []
    final_actions = []
    for request in requests:
        with np.load(request.request_dir / "arrays.npz", allow_pickle=False) as archive:
            layer_pos = layer_position(archive, layer, request.request_dir / "arrays.npz")
            value_rows.append(select_layer_vector(archive[SUMMARY_VALUES_KEY], layer_pos).astype(np.float64))
            token_rows.append(select_layer_vector(archive[SUMMARY_TOKEN_KEY], layer_pos).astype(np.int64))
            final_actions.append(np.asarray(archive["final_actions"], dtype=np.float64))
    return TaskData(
        task_index=task_index,
        prompt=prompt,
        slug=slug,
        requests=requests,
        max_positive=np.stack(value_rows, axis=0),
        max_positive_token=np.stack(token_rows, axis=0),
        final_actions=final_actions,
    )


def layer_position(archive: np.lib.npyio.NpzFile, layer: int, arrays_path: Path) -> int:
    if SUMMARY_LAYERS_KEY not in archive:
        raise KeyError(f"{arrays_path} is missing {SUMMARY_LAYERS_KEY}")
    matches = np.where(np.asarray(archive[SUMMARY_LAYERS_KEY]) == layer)[0]
    if len(matches) == 0:
        raise ValueError(f"{arrays_path} has layers={archive[SUMMARY_LAYERS_KEY].tolist()}, missing {layer}")
    return int(matches[0])


def select_layer_vector(array: np.ndarray, layer_pos: int) -> np.ndarray:
    selected = np.asarray(array)[layer_pos]
    if selected.ndim == 2:
        selected = selected[0]
    if selected.ndim != 1:
        raise ValueError(f"Expected summary vector after layer selection, got {selected.shape}")
    return selected


def load_static_dictionary(path: Path, layer: int) -> dict[int, StaticInfo]:
    static = {}
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            record = json.loads(line)
            if int(record["layer"]) != layer:
                continue
            groups = tuple(group for group, field in GROUP_FIELDS.items() if int(record.get(field, 0)) >= 2)
            static[int(record["neuron"])] = StaticInfo(
                quality_score=record.get("quality_score", ""),
                groups=groups,
                top_tokens=tuple(str(token) for token in record.get("top_tokens", [])[:10]),
            )
    return static


def parse_int_list(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def build_chunk_rows(task: TaskData, static: dict[int, StaticInfo], tracked_neurons: list[int]) -> list[dict[str, Any]]:
    rows = []
    l17_mean = task.max_positive.mean(axis=1)
    l17_p95 = np.percentile(task.max_positive, 95, axis=1)
    l17_p99 = np.percentile(task.max_positive, 99, axis=1)
    l17_top = task.max_positive.max(axis=1)
    for idx, request in enumerate(task.requests):
        actions = task.final_actions[idx]
        action_means = actions.mean(axis=0)
        top_neuron = int(np.argmax(task.max_positive[idx]))
        row: dict[str, Any] = {
            "chunk": idx + 1,
            "request_number": request.request_number,
            "request_name": request.request_name,
            "timestamp_ns": request.timestamp_ns,
            "gripper_mean": float(action_means[-1]),
            "gripper_first": float(actions[0, -1]),
            "gripper_last": float(actions[-1, -1]),
            "l17_mean": float(l17_mean[idx]),
            "l17_p95": float(l17_p95[idx]),
            "l17_p99": float(l17_p99[idx]),
            "l17_top": float(l17_top[idx]),
            "top_neuron": top_neuron,
            "top_token_index": int(task.max_positive_token[idx, top_neuron]),
            **static_columns(static.get(top_neuron)),
        }
        for dim, value in enumerate(action_means):
            row[f"action_{dim}_mean"] = float(value)
        for neuron in tracked_neurons:
            row[f"n{neuron}_max_positive"] = float(task.max_positive[idx, neuron]) if neuron < task.max_positive.shape[1] else math.nan
        rows.append(row)
    return rows


def detect_gripper_events(task: TaskData, close_threshold: float, open_threshold: float) -> list[dict[str, Any]]:
    gripper = gripper_series(task)
    p99 = np.percentile(task.max_positive, 99, axis=1)
    top = task.max_positive.max(axis=1)
    rows = []
    idx = 0
    event_index = 1
    while idx < len(gripper):
        if gripper[idx] < close_threshold:
            idx += 1
            continue
        close_idx = idx
        release_idx = None
        scan = close_idx + 1
        while scan < len(gripper):
            if gripper[scan] <= open_threshold:
                release_idx = scan
                break
            scan += 1
        if release_idx is None:
            release_idx = len(gripper) - 1
        burst_idx = close_idx + int(np.argmax(p99[close_idx : release_idx + 1]))
        rows.append(
            {
                "event": event_index,
                "close_chunk": close_idx + 1,
                "burst_chunk": burst_idx + 1,
                "release_chunk": release_idx + 1,
                "close_gripper_mean": float(gripper[close_idx]),
                "burst_gripper_mean": float(gripper[burst_idx]),
                "release_gripper_mean": float(gripper[release_idx]),
                "close_l17_p99": float(p99[close_idx]),
                "burst_l17_p99": float(p99[burst_idx]),
                "release_l17_p99": float(p99[release_idx]),
                "close_l17_top": float(top[close_idx]),
                "burst_l17_top": float(top[burst_idx]),
                "release_l17_top": float(top[release_idx]),
            }
        )
        event_index += 1
        idx = release_idx + 1
    return rows


def detect_l17_bursts(
    task: TaskData,
    static: dict[int, StaticInfo],
    event_rows: list[dict[str, Any]],
    *,
    top_n: int,
    mad_threshold: float,
    min_peak_distance: int,
) -> list[dict[str, Any]]:
    p99 = np.percentile(task.max_positive, 99, axis=1)
    mean = task.max_positive.mean(axis=1)
    top = task.max_positive.max(axis=1)
    gripper = gripper_series(task)
    median = float(np.median(p99))
    mad = float(np.median(np.abs(p99 - median)))
    robust_scale = 1.4826 * mad if mad > 1e-9 else float(np.std(p99) or 1.0)
    threshold = median + mad_threshold * robust_scale

    selected: dict[int, str] = {}
    for row in event_rows:
        selected[int(row["burst_chunk"]) - 1] = "gripper_window"
    for idx in local_peak_indices(p99, min_peak_distance):
        if p99[idx] >= threshold or not selected:
            selected.setdefault(idx, "l17_peak")
    for idx in np.argsort(-p99)[:top_n]:
        selected.setdefault(int(idx), "top_p99")

    rows = []
    for rank, idx in enumerate(sorted(selected, key=lambda i: (-p99[i], i)), start=1):
        if rank > max(top_n, len(event_rows)):
            break
        top_neuron = int(np.argmax(task.max_positive[idx]))
        prev_p99 = float(p99[idx] - p99[idx - 1]) if idx > 0 else math.nan
        next_p99 = float(p99[idx + 1] - p99[idx]) if idx + 1 < len(p99) else math.nan
        rows.append(
            {
                "rank": rank,
                "chunk": idx + 1,
                "reason": selected[idx],
                "is_prominent": bool(p99[idx] >= threshold),
                "robust_z": float((p99[idx] - median) / robust_scale) if robust_scale > 0 else math.nan,
                "gripper_mean": float(gripper[idx]),
                "l17_mean": float(mean[idx]),
                "l17_p99": float(p99[idx]),
                "l17_top": float(top[idx]),
                "prev_p99_delta": prev_p99,
                "next_p99_delta": next_p99,
                "top_neuron": top_neuron,
                "top_value": float(task.max_positive[idx, top_neuron]),
                "top_token_index": int(task.max_positive_token[idx, top_neuron]),
                **static_columns(static.get(top_neuron)),
            }
        )
    return rows


def local_peak_indices(values: np.ndarray, min_distance: int) -> list[int]:
    peaks = []
    for idx, value in enumerate(values):
        left = values[idx - 1] if idx > 0 else -math.inf
        right = values[idx + 1] if idx + 1 < len(values) else -math.inf
        if value >= left and value >= right:
            peaks.append(idx)
    peaks.sort(key=lambda idx: float(values[idx]), reverse=True)
    selected: list[int] = []
    for idx in peaks:
        if all(abs(idx - other) >= min_distance for other in selected):
            selected.append(idx)
    return sorted(selected)


def gripper_series(task: TaskData) -> np.ndarray:
    return np.asarray([actions[:, -1].mean() for actions in task.final_actions], dtype=np.float64)


def write_task_plot(
    path: Path,
    task: TaskData,
    event_rows: list[dict[str, Any]],
    burst_rows: list[dict[str, Any]],
    tracked_neurons: list[int],
) -> None:
    chunks = np.arange(1, len(task.requests) + 1)
    gripper = gripper_series(task)
    p99 = np.percentile(task.max_positive, 99, axis=1)
    mean = task.max_positive.mean(axis=1)
    top = task.max_positive.max(axis=1)
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    axes[0].plot(chunks, gripper, marker="o", color="#2f6b9a", linewidth=1.8)
    axes[0].set_ylabel("A7 mean")
    axes[0].set_title(f"L17 phase bursts: Task {task.task_index:02d} - {task.prompt}")

    axes[1].plot(chunks, p99, marker="o", color="#c9633e", label="p99", linewidth=1.8)
    axes[1].plot(chunks, mean, marker="o", color="#6b8f6b", label="mean", linewidth=1.5)
    axes[1].legend(frameon=False)
    axes[1].set_ylabel("L17 summary")

    axes[2].plot(chunks, top, marker="o", color="#8c5b9f", linewidth=1.8)
    axes[2].set_ylabel("L17 top")

    colors = plt.cm.tab10(np.linspace(0, 1, min(4, len(tracked_neurons))))
    for color, neuron in zip(colors, tracked_neurons[:4], strict=False):
        if neuron < task.max_positive.shape[1]:
            axes[3].plot(chunks, task.max_positive[:, neuron], marker="o", label=f"N{neuron}", linewidth=1.6, color=color)
    axes[3].legend(ncol=4, frameon=False)
    axes[3].set_ylabel("tracked")
    axes[3].set_xlabel("chunk")

    for axis in axes:
        axis.grid(alpha=0.2)
    mark_events(axes, event_rows)
    mark_bursts(axes, burst_rows)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def mark_events(axes: np.ndarray, event_rows: list[dict[str, Any]]) -> None:
    for row in event_rows:
        for axis in axes:
            axis.axvline(int(row["close_chunk"]), color="#333333", linestyle="--", linewidth=1)
            axis.axvline(int(row["release_chunk"]), color="#333333", linestyle=":", linewidth=1)


def mark_bursts(axes: np.ndarray, burst_rows: list[dict[str, Any]]) -> None:
    for row in burst_rows[:5]:
        if str(row.get("reason")) in {"gripper_window", "l17_peak"} or bool(row.get("is_prominent")):
            for axis in axes:
                axis.axvline(int(row["chunk"]), color="#d55e00", linestyle="-.", linewidth=1)


def write_task_report(
    path: Path,
    task: TaskData,
    chunk_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
    burst_rows: list[dict[str, Any]],
) -> None:
    lines = [
        f"# L17 Task {task.task_index:02d}",
        "",
        f"- Prompt: `{task.prompt}`",
        f"- Requests: `{task.requests[0].request_name}` -> `{task.requests[-1].request_name}`",
        f"- Chunks: {len(task.requests)}",
        "",
        "## Detected Gripper Events",
        "",
        markdown_table(event_rows, max_rows=20),
        "",
        "## L17 Burst Candidates",
        "",
        markdown_table(burst_rows, max_rows=20),
        "",
        "## Chunk Overview",
        "",
        markdown_table(
            [
                {
                    "chunk": row["chunk"],
                    "gripper_mean": row["gripper_mean"],
                    "l17_p99": row["l17_p99"],
                    "l17_top": row["l17_top"],
                    "top_neuron": row["top_neuron"],
                    "groups": row["groups"],
                }
                for row in chunk_rows
            ],
            max_rows=80,
        ),
        "",
        "## Files",
        "",
        "- `l17_task_phase_overview.png`",
        "- `l17_task_chunk_summary.csv`",
        "- `l17_task_events.csv`",
        "- `l17_task_bursts.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def task_summary_row(task: TaskData, event_rows: list[dict[str, Any]], burst_rows: list[dict[str, Any]]) -> dict[str, Any]:
    p99 = np.percentile(task.max_positive, 99, axis=1)
    top = task.max_positive.max(axis=1)
    best = burst_rows[0] if burst_rows else {}
    return {
        "task_index": task.task_index,
        "slug": task.slug,
        "prompt": task.prompt,
        "chunk_count": len(task.requests),
        "start_request_number": task.requests[0].request_number,
        "end_request_number": task.requests[-1].request_number,
        "detected_gripper_events": len(event_rows),
        "best_burst_chunk": best.get("chunk", ""),
        "best_burst_reason": best.get("reason", ""),
        "best_burst_l17_p99": best.get("l17_p99", ""),
        "best_burst_robust_z": best.get("robust_z", ""),
        "best_burst_top_neuron": best.get("top_neuron", ""),
        "max_l17_p99": float(np.max(p99)),
        "max_l17_p99_chunk": int(np.argmax(p99) + 1),
        "max_l17_top": float(np.max(top)),
        "max_l17_top_chunk": int(np.argmax(top) + 1),
    }


def add_task_fields(task: TaskData, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        merged = {
            "task_index": task.task_index,
            "slug": task.slug,
            "prompt": task.prompt,
        }
        merged.update(row)
        output.append(merged)
    return output


def write_root_report(path: Path, run_dir: Path, task_rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Pick-And-Put L17 Prompt Task Summary",
        "",
        f"- Run: `{run_dir}`",
        f"- Tasks: {len(task_rows)}",
        "",
        "## Task Summary",
        "",
        markdown_table(task_rows, max_rows=40),
        "",
        "## Files",
        "",
        "- `task_summary.csv`",
        "- `all_detected_events.csv`",
        "- `all_l17_bursts.csv`",
        "- one subdirectory per prompt task",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def static_columns(info: StaticInfo | None) -> dict[str, Any]:
    if info is None:
        return {"is_static_candidate": False, "quality_score": "", "groups": "", "top_tokens": ""}
    return {
        "is_static_candidate": True,
        "quality_score": info.quality_score,
        "groups": ";".join(info.groups),
        "top_tokens": " ".join(info.top_tokens[:8]),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, Any]], *, max_rows: int) -> str:
    if not rows:
        return "_No rows._"
    rows = rows[:max_rows]
    headers = list(rows[0])
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(markdown_value(row.get(header, "")) for header in headers) + " |" for row in rows)
    return "\n".join(lines)


def markdown_value(value: Any) -> str:
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:.3f}"
    return str(value).replace("|", "/")


def slugify(text: str, max_len: int = 70) -> str:
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", normalized.lower()).strip("_")
    return (slug or "task")[:max_len].strip("_")


if __name__ == "__main__":
    main()
