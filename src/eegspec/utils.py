import os, json, re
import warnings

import numpy as np
from typing import List, Tuple, Dict, Any

EPS = 1e-20

def save_json(obj: Any, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_channels(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip() for ln in f if ln.strip() and ln.strip()[0] not in "#;%"]

def parse_channels_arg(chs: str) -> List[str]:
    return [c.strip() for c in chs.split(",") if c.strip()]

def builtin_montage_path() -> str:
    import importlib.resources as ir
    return str(ir.files("eegspec").joinpath("data/montages/caps63.locs"))

def parse_locs_file(path: str) -> List[str]:
    """Robust .locs parser: accept EEGLAB-like multi-column or one-label-per-line."""
    ch = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line[0] in "#;%":
                continue
            toks = re.split(r"[\s,]+", line)
            label = None
            for tok in toks:
                if re.search(r"[A-Za-z]", tok):
                    label = tok
                    break
            if label is None and len(toks) >= 2:
                label = toks[1]
            if label:
                ch.append(label)
    if not ch:
        raise ValueError(f"No channel names parsed from {path}")
    return ch

def resolve_channels(channels_file: str = None,  n_channels: int = None) -> List[str]:
    """Resolve channel names from CSV string, plaintext file, or .locs file; fallback to built-in montage.
    If n_channels is provided and names mismatch, generate fallback names Ch1..ChN to keep pipeline running."""
    if channels_file:
        if os.path.splitext(channels_file)[1].lower() in (".locs", ".eloc", ".sfp"):
            ch = parse_locs_file(channels_file)
        elif os.path.splitext(channels_file)[1].lower() in ".csv":
            ch = parse_channels_arg(channels_file)
        else:
            ch = load_channels(channels_file)
    else:
        warnings.warn("Missing montage input, using built-in caps63 montage.")
        try:
            ch = parse_locs_file(builtin_montage_path())
        except Exception as e:
            raise f"Error parse built-in montage channel file: {e}"
    if n_channels is not None and len(ch) != n_channels:
        warnings.warn(f"Input data channels amount {len(ch)} doesn't match montage file channels amount: {n_channels}")
        return [f"Ch{i+1}" for i in range(n_channels)]
    return ch

def list_subject_jsons(input_path: str) -> List[str]:
    if os.path.isdir(input_path):
        return sorted([os.path.join(input_path, x) for x in os.listdir(input_path) if x.lower().endswith(".json")])
    else:
        return [input_path]

def subject_id_from_path(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]

def load_subject_tasks_json(path: str) -> Dict[str, np.ndarray]:
    """Load a subject JSON in 'task-centric' format:
    { "task_A": [[ch1_series ...], [ch2_series ...], ...], ... }
    Returns dict: task_name -> data (n_times, n_channels)
    """
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if not isinstance(obj, dict):
        raise ValueError("Top-level JSON must be an object mapping task_name -> channel_lists")
    out = {}
    for task, v in obj.items():
        arr = np.array(v, dtype=float)
        if arr.ndim == 1:
            arr = arr[None, :]
        if arr.ndim != 2:
            raise ValueError(f"Task '{task}' is not a 2D matrix (n_channels x n_times)")
        out[str(task)] = arr.T  # to (n_times, n_channels)
    return out

if __name__ == "__main__":
    print(parse_locs_file("./data/montages/caps63.locs"))
