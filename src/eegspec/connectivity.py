import numpy as np
from typing import List, Dict
import mne

def spectral_connectivity_matrix(
    data: np.ndarray,
    sfreq: float,
    fmin: float,
    fmax: float,
    method: List[str],
    epoch_sec: float = 2.0,
    overlap: float = 0.5,
) -> Dict[str, np.ndarray]:
    if data.ndim == 2:
        n_times, n_ch = data.shape
        win = int(round(epoch_sec * sfreq))
        hop = max(1, int(round(win * (1.0 - overlap))))
        epochs = []
        for start in range(0, max(0, n_times - win + 1), hop):
            sl = slice(start, start + win)
            epochs.append(data[sl, :].T)
        if not epochs:
            raise ValueError("Not enough data for one epoch")
        X = np.stack(epochs, axis=0)
    elif data.ndim == 3:
        X = data
    else:
        raise ValueError("data must be (n_times, n_channels) or (n_epochs, n_channels, n_times)")

    con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(
        X, method=method, mode="multitaper", sfreq=sfreq, fmin=fmin, fmax=fmax, faverage=True, verbose=False
    )
    out = {}
    for i, m in enumerate(method):
        M = con[i, :, :, 0]
        if m in ("coh", "plv"):
            np.fill_diagonal(M, 1.0)
        out[m] = M
    return out
