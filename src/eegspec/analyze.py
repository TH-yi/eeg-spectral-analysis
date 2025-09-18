import os, json, traceback
import numpy as np
from typing import Dict, Any, List, Tuple
from .base import BaseApp
from .utils import load_subject_tasks_json, list_subject_jsons, subject_id_from_path, resolve_channels, save_json
from .psd import compute_psd_welch
from .features import bandpower, spectral_entropy, spectral_moments, spectral_edge, median_frequency
from .iaf import estimate_iaf
from .faa import faa_from_psd

def run_task_compute(subject_id: str, task_name: str, data_txc: np.ndarray, sfreq: float,
                     nperseg: int, noverlap: int, window: str,
                     ch_names: List[str], alpha_band: Tuple[float,float],
                     use_db_faa: bool, out_dir: str,
                     log_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    app = BaseApp(**log_kwargs)
    try:
        app.logger.info(f"[Task start] subject={subject_id} task={task_name} shape={data_txc.shape}")
        freqs, psd = compute_psd_welch(data_txc, sfreq=sfreq, nperseg=nperseg, noverlap=noverlap, window=window)
        std_bands = {"delta":(1.0,4.0), "theta":(4.0,7.0), "alpha":alpha_band, "beta":(13.0,30.0), "gamma":(30.0,45.0)}
        bp_abs = bandpower(psd, freqs, std_bands, relative=False)
        bp_rel = bandpower(psd, freqs, std_bands, relative=True, total_range=(1.0,45.0))
        ent = spectral_entropy(psd, freqs, fmin=1.0, fmax=45.0, log_base=np.e)
        moms = spectral_moments(psd, freqs, fmin=1.0, fmax=45.0)
        sef95 = spectral_edge(psd, freqs, percent=0.95, fmin=1.0, fmax=45.0)
        f50 = median_frequency(psd, freqs, fmin=1.0, fmax=45.0)
        faa_val = faa_from_psd(psd, freqs, ch_names, left="F3", right="F4", alpha=alpha_band, use_db=use_db_faa)

        subj_dir = os.path.join(out_dir, "subjects", subject_id)
        os.makedirs(subj_dir, exist_ok=True)
        psd_path = os.path.join(subj_dir, f"psd_{task_name}.json")
        metrics_path = os.path.join(subj_dir, f"metrics_{task_name}.json")

        save_json({"freqs": freqs.tolist(), "psd": psd.tolist(), "channels": ch_names}, psd_path)

        metrics = {
            "subject": subject_id,
            "task": task_name,
            "bands_abs": {k: v.tolist() for k, v in bp_abs.items()},
            "bands_rel": {k: v.tolist() for k, v in bp_rel.items()},
            "entropy": ent.tolist(),
            "moments": {k: v.tolist() for k, v in moms.items()},
            "SEF95": sef95.tolist(),
            "F50": f50.tolist(),
            "FAA": faa_val,
            "alpha_band": list(alpha_band)
        }
        save_json(metrics, metrics_path)
        app.logger.info(f"[Task done] subject={subject_id} task={task_name} -> psd:{psd_path} metrics:{metrics_path}")
        return {"ok": True, "subject": subject_id, "task": task_name, "psd": psd_path, "metrics": metrics_path}
    except Exception as e:
        app.logger.error(f"[Task error] subject={subject_id} task={task_name}: {e}")
        app.logger.debug(traceback.format_exc())
        return {"ok": False, "subject": subject_id, "task": task_name, "error": str(e)}

def analyze_entry(input_path: str, sfreq: float, out_dir: str,
                  nperseg: int = 1024, noverlap: int = None, window: str = "hann",
                  channels_file: str = None,
                  alpha: str = "8,13", faa_db: bool = False,
                  max_processors: int = 4,
                  log_kwargs: Dict[str, Any] = None) -> Dict[str, Any]:
    if log_kwargs is None:
        log_kwargs = dict(log_level="INFO", log_dir=None, log_prefix="", log_suffix="", log_percentage=None)
    app = BaseApp(**log_kwargs)
    os.makedirs(out_dir, exist_ok=True)

    try:
        subjects = list_subject_jsons(input_path)
        if not subjects:
            raise FileNotFoundError("No JSON files found under input path")
        app.logger.info(f"Found {len(subjects)} subject file(s)")
    except Exception as e:
        app.logger.error(f"Failed to enumerate input: {e}")
        raise

    schedule = []
    alpha_band = tuple(map(float, alpha.split(",")))
    for spath in subjects:
        sid = subject_id_from_path(spath)
        try:
            tasks = load_subject_tasks_json(spath)  # task -> (n_times, n_channels)
            sample_task = next(iter(tasks.values()))
            n_ch = sample_task.shape[1]
            ch_names = resolve_channels(channels_file, n_channels=n_ch)
            if len(ch_names) != n_ch:
                app.logger.warning(f"Channel count mismatch for {sid}: using placeholders Ch1..Ch{n_ch}")
            for tname, data in tasks.items():
                schedule.append((sid, tname, data, ch_names))
        except Exception as e:
            app.logger.error(f"Failed to parse subject {sid}: {e}")

    summary = {"subjects": {}, "alpha": list(alpha_band), "sfreq": sfreq, "nperseg": nperseg, "window": window}
    total = len(schedule)
    app.logger.info(f"Total tasks to run: {total} (max_processors={max_processors})")
    if total == 0:
        save_json(summary, os.path.join(out_dir, "summary.json"))
        return summary

    import concurrent.futures
    idx = 0
    futures = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_processors) as ex:
        while idx < total and len(futures) < max_processors:
            sid, tname, data, ch = schedule[idx]; idx += 1
            task_log_kwargs = dict(log_kwargs); task_log_kwargs["log_suffix"] = f"_{sid}_{tname}"
            fut = ex.submit(run_task_compute, sid, tname, data, sfreq, nperseg, noverlap, window, ch, alpha_band, faa_db, out_dir, task_log_kwargs)
            futures.append(fut)
        done_count = 0
        while futures:
            for fut in concurrent.futures.as_completed(futures, timeout=None):
                try:
                    res = fut.result()
                except Exception as e:
                    app.logger.error(f"Worker crashed: {e}")
                    res = {"ok": False, "error": str(e)}
                if res.get("ok"):
                    sid = res["subject"]; tname = res["task"]
                    summary.setdefault("subjects", {}).setdefault(sid, {})[tname] = {k: res[k] for k in ("psd","metrics") if k in res}
                else:
                    app.logger.error(f"Task failed: {res}")
                done_count += 1
                futures.remove(fut)
                if idx < total:
                    sid, tname, data, ch = schedule[idx]; idx += 1
                    task_log_kwargs = dict(log_kwargs); task_log_kwargs["log_suffix"] = f"_{sid}_{tname}"
                    futures.append(ex.submit(run_task_compute, sid, tname, data, sfreq, nperseg, noverlap, window, ch, alpha_band, faa_db, out_dir, task_log_kwargs))
                app.logger.info(f"Progress: {done_count}/{total}")
                break

    summ_path = os.path.join(out_dir, "summary.json")
    save_json(summary, summ_path)
    app.logger.info(f"Summary written: {summ_path}")
    return summary
