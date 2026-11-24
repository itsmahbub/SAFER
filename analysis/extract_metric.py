#!/usr/bin/env python3
"""
extract_metric.py

Produces a filtered assessments JSON containing only a specific metric,
retaining only the 'manual' and 'arbitrator' evaluator entries (chatgpt and
gemini are dropped).

Usage:
    python3 analysis/extract_metric.py "<Metric Name>"

Example:
    python3 analysis/extract_metric.py "Safeguard Bypass"

Output:
    results/assessments_<metric_slug>.json

The output uses the original paper titles as keys. Each paper contains its
'key', 'name', and 'assessments' fields with the requested metric's 'manual'
and 'arbitrator' entries.
"""

import argparse
import json
import sys
import os
import re




KEEP_EVALUATORS = {"manual", "arbitrator"}


def slugify(name: str) -> str:
    """Convert a metric name to a safe filename component."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


def extract_metric(metric_name: str, value: str | None = None) -> None:
    # Load source data
    with open("results/assessments.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect all available metric names for validation / error messaging
    available_metrics: set[str] = set()
    for paper_data in data.values():
        available_metrics.update(paper_data.get("assessments", {}).keys())

    if metric_name not in available_metrics:
        print(f"ERROR: Metric '{metric_name}' not found in assessments.")
        print("Available metrics:")
        for m in sorted(available_metrics):
            print(f"  - {m}")
        sys.exit(1)

    # Build filtered output
    output: dict = {}
    papers_missing_metric = []

    for paper_key, paper_data in data.items():
        assessments = paper_data.get("assessments", {})

        if metric_name not in assessments:
            papers_missing_metric.append(paper_key)
            continue

        metric_entry = assessments[metric_name]

        # Keep only manual and arbitrator evaluators
        filtered_evaluators = {
            k: v for k, v in metric_entry.items() if k in KEEP_EVALUATORS
        }
        if value is not None and not any(
            str(assessment.get("value", "")).strip().lower() == value
            for assessment in filtered_evaluators.values()
        ):
            continue

        output[paper_key] = {
            field: paper_data[field] for field in ("key", "name") if field in paper_data
        }
        output[paper_key]["assessments"] = {metric_name: filtered_evaluators}

    # Write output
    slug = slugify(metric_name)
    suffix = f"_{value}" if value is not None else ""
    output_path = os.path.join("results", f"assessments_{slug}{suffix}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Report
    print(f"Metric   : {metric_name}")
    print(f"Papers   : {len(output)} included")
    if papers_missing_metric:
        print(f"Skipped  : {len(papers_missing_metric)} paper(s) had no entry for this metric:")
        for p in papers_missing_metric:
            print(f"  - {p}")
    print(f"Output   : {os.path.abspath(output_path)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract manual and arbitrator assessments.")
    parser.add_argument("metric_name", help="Metric name, such as Safeguard Bypass")
    parser.add_argument(
        "--value",
        choices=("high", "medium", "low"),
        type=str.lower,
        help="Include papers where either evaluator gave this rating",
    )
    args = parser.parse_args()
    extract_metric(args.metric_name, args.value)
