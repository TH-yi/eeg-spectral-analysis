# eegspec (v0.3.1)

**Analyze command** supports a **folder** (many `subject.json`) or a **single file**.  
Each subject JSON is a *task-centric* dict:
```json
{
  "task_A": [[ch1_series...], [ch2_series...], ...],  // n_channels x n_times
  "task_B": [[...]]
}
```

Outputs:
- Per-task: `psd_<task>.json` (freqs/psd/channels) and `metrics_<task>.json` (bands_abs/rel, entropy, moments, SEF95, F50, IAF, FAA)
- Top-level: `summary.json` with index and run parameters

Install (editable):
```bash
pip install -e .
```

Example (PowerShell one-liner):
```powershell
eegspec analyze --input D:\EEG\subjects --sfreq 500 --out-dir D:\EEG\out --max-processors 15 --channels-file D:\EEG\caps63.locs --alpha 8,13 --faa-db --nperseg 1024 --noverlap 512 --window hann --log-level INFO --log-dir D:\EEG\out\.logs
```
