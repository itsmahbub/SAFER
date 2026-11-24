"""Require complete ratings under the current codebook."""


def require_current_metrics(data):
    required = (
        "Safeguard Bypass", "Targeted Attack Discovery", "Input Plausibility",
        "Failure Reproducibility", "Failure Diagnostics", "Attack Transferability",
    )
    for paper_key, paper in data.items():
        assessments = paper.get("assessments", {})
        for metric in required:
            entry = assessments.get(metric)
            allowed = {"High", "Medium", "Low"}
            if metric == "Input Plausibility":
                allowed.add("N/A")
            if not entry or entry.get("manual", {}).get("value") not in allowed:
                raise ValueError(
                    f"{paper_key}: missing completed {metric} assessment. "
                    "Reassess under the revised codebook before generating tables."
                )
