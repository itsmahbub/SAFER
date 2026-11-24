
import json
from collections import Counter
from require_current_metrics import require_current_metrics

# === CONFIG ===
input_file = "results/assessments.json"

metrics = [
    "Safeguard Bypass",
    "Targeted Attack Discovery",
    "Input Plausibility",
    "Failure Reproducibility",
    "Failure Diagnostics",
    "Attack Transferability",
]

levels = ["High", "Medium", "Low"]

# === LOAD DATA ===
with open(input_file, "r") as f:
    data = json.load(f)

require_current_metrics(data)
total_papers = len(data)

if total_papers == 0:
    raise ValueError("No papers found.")

# === COUNT LEVELS ===
counts = {metric: Counter() for metric in metrics}

for paper_name, paper_data in data.items():
    assessments = paper_data.get("assessments", {})

    for metric in metrics:
        manual_entry = assessments.get(metric, {}).get("manual", {})
        value = manual_entry.get("value", "")
        value = value.strip() if isinstance(value, str) else ""

        allowed = levels + (
            ["N/A"] if metric == "Input Plausibility" else []
        )

        if value not in allowed:
            raise ValueError(
                f"Invalid or missing manual assessment: "
                f"paper={paper_name}, metric={metric}, value={value!r}"
            )

        counts[metric][value] += 1

# Include N/A only if it occurs.
has_na = counts["Input Plausibility"]["N/A"] > 0
display_levels = levels + (["N/A"] if has_na else [])

# === FORMAT CELLS ===
def format_cells(metric, level):
    if level == "N/A" and metric != "Input Plausibility":
        return [r"\multicolumn{2}{c}{---}"]

    count = counts[metric][level]
    pct = 100 * count / total_papers

    pct_str = f"{pct:.1f}\\%"
    count_str = f"({count})"

    # Bold both cells when this is a majority group.
    if count > total_papers / 2:
        pct_str = rf"\textbf{{{pct_str}}}"
        count_str = rf"\textbf{{{count_str}}}"

    return [pct_str, count_str]



for metric in metrics:
    row = [metric]

    for level in display_levels:
        row.extend(format_cells(metric, level))

    print(" & ".join(row) + r" \\")


