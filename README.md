# eeg-spectral-analysis

**Version**: v0.1.0  
**Summary**: EEG spectral analysis toolkit for task‑centric JSON inputs. Computes Welch PSD and common spectral metrics (band powers, entropy, spectral moments, SEF95, median frequency, IAF, FAA). Supports subject‑major, task‑level multiprocessing and DualHandler logging.

---

## 1) Input format (task‑centric JSON)

Each subject is a single JSON file whose **top‑level keys are task names**. The value is a 2‑D array with shape `n_channels × n_times` (each inner list is one channel’s time‑series). The CLI will transpose internally to `(n_times × n_channels)`.

```jsonc
{
  "task_A": [[ch1_t1, ch1_t2, ...], [ch2_t1, ch2_t2, ...], ...],  // n_channels × n_times
  "task_B": [[...]],
  "...":    [[...]]
}
```

A folder of subjects is simply a folder with many such JSON files (non‑recursive).

---

## 2) Channel names

You **should** provide channel names with **`--channels-file`**. Supported formats:

- `.locs` (EEGLAB‑style or one name per line)  
- `.txt/.csv` (one channel name per line)

***Without this parameter, the program will use build-in caps63.locs as channels***

**Requirements**:
1. The number of channel names must equal the number of columns in your JSON data (i.e., `n_channels`).  
2. The order of names must match the column order in the JSON data.

> If names don’t match the data shape, the pipeline will fall back to placeholder names (`Ch1..ChN`). FAA requires `F3`/`F4`; if not present, FAA will be `NaN`.

---

## 3) Installation

```powershell
pip install -e .
```

> Requires: Python ≥ 3.9, NumPy, SciPy, MNE, Matplotlib.

---

## 4) CLI (one‑liner examples)

### Single subject
```powershell
eegspec analyze --input D:\EEG\sub_01.json --sfreq 500 --out-dir D:\EEG\out --nperseg 1024 --noverlap 512 --window hann --channels-file D:\EEG\caps63.locs --alpha 8,13 --faa-db --max-processors 8 --log-level DEBUG --log-dir D:\EEG\out\.logs --log-prefix run_ --log-suffix _alpha --log-percentage 0.8
```

### Folder of subjects
```powershell
eegspec analyze --input D:\EEG\subjects --sfreq 500 --out-dir D:\EEG\out --nperseg 1024 --noverlap 512 --window hann --channels-file D:\EEG\caps63.locs --alpha 8,13 --faa-db --max-processors 8 --log-level INFO --log-dir D:\EEG\out\.logs
```

**Key parameters**

- `--input` : A single subject JSON or a folder of subject JSON files  
- `--sfreq` : Sampling rate (Hz)  
- `--out-dir` : Output directory  
- `--nperseg` / `--noverlap` / `--window` : Welch PSD params (defaults: 1024 / 512 / hann)  
- `--channels-file` : Channel list file (`.locs` / `.txt`)  
- `--alpha` : Alpha band for FAA and bandpowers (default `8,13`)  
- `--faa-db` : Compute FAA as dB difference (otherwise natural log difference)  
- `--max-processors` : Max concurrent tasks  
- Logging: `--log-level`, `--log-dir`, `--log-prefix`, `--log-suffix`, `--log-percentage`

---

## 5) Outputs

```
out/
├─ subjects/
│  ├─ sub_01/
│  │  ├─ psd_task_A.json        # {"freqs":[Nf], "psd":[Nch×Nf], "channels":[Nch]}
│  │  └─ metrics_task_A.json    # bands_abs/rel, entropy, moments, SEF95, F50, IAF, FAA
│  └─ sub_02/...
└─ summary.json                 # run parameters and an index of all subject×task outputs
```

**Metrics included**

- **Band powers** (absolute & relative): delta (1–4), theta (4–7), alpha (α, configurable), beta (13–30), gamma (30–45)  
- **Spectral entropy** (1–45 Hz)  
- **Spectral moments** (centroid, variance, skewness, kurtosis; 1–45 Hz)  
- **SEF95** (95% spectral edge frequency; 1–45 Hz)  
- **F50** (median frequency; 1–45 Hz)  
- **IAF** (7–14 Hz peak, with optional smoothing)  
- **FAA** (F3 vs F4; dB or ln difference over alpha band)

---

## 6) Troubleshooting

- **`"FAA": NaN`** → Channel names don’t include `F3` and/or `F4`, or name/shape mismatch. Fix your `--channels-file` so that it lists the correct names in the exact data order.  
- **No outputs** → Check logs under `--log-dir` for `[Task error]` / `Analyze failed`.  
- **Data too short** → Ensure `nperseg` and `noverlap` are valid given your time‑series length.  
- **Performance** → Increase `--max-processors` to utilize more cores; the scheduler fills by subject (subject‑major, task‑level windowing) to be memory‑friendly.

---

## 7) Reproducibility & logging

- All runs log parameters and progress via **DualHandler** (console + file).  
- Each task’s log filename includes `{subject}_{task}` for easy filtering.  
- `summary.json` records global parameters and file index.

---

## 8) Roadmap (optional)

- Optional connectivity metrics (coherence, wPLI) export in `analyze`  
- Plotting helpers (PSD curves, connectivity heatmaps)  
- FAA channel selection flags (`--faa-left`, `--faa-right`) if your montage differs from F3/F4

---

## 9) License

This project is released under the MIT License. See `LICENSE` for details.
