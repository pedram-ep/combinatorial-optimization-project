import json
from pathlib import Path
from typing import Any, Dict

def load_instance(filename: str | Path | None = None, data: Dict[str, Any] | None = None):
    """Load a college admission instance from a JSON file or a preloaded dict."""
    if data is not None:
        instance = data
    else:
        with open(filename, "r", encoding="utf-8") as handle:
            instance = json.load(handle)

    if "preferences" in instance and isinstance(instance["preferences"], dict):
        instance["preferences"] = {int(k): [int(v2) for v2 in v] for k, v in instance["preferences"].items()}
    if "quotas" in instance and isinstance(instance["quotas"], dict):
        instance["quotas"] = {int(k): int(v) for k, v in instance["quotas"].items()}

    if "scores" in instance and isinstance(instance["scores"], dict):
        normalized_scores = {}
        for key, value in instance["scores"].items():
            if isinstance(key, tuple):
                normalized_scores[(int(key[0]), int(key[1]))] = int(value)
            else:
                i_str, j_str = key.split(",")
                normalized_scores[(int(i_str), int(j_str))] = int(value)
        instance["scores"] = normalized_scores

    instance["n"] = int(instance["n"])
    instance["m"] = int(instance["m"])
    return instance

def _normalize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(data, (str, Path)):
        return load_instance(data)
    return load_instance(data=data)