import numpy as np
from scipy.signal import savgol_filter
from .features import band_mask

def estimate_iaf(psd: np.ndarray, freqs: np.ndarray, fmin=7.0, fmax=14.0, smooth=True, window=11, poly=3):
    m = band_mask(freqs, fmin, fmax)
    f = freqs[m]
    P = psd[:, m]
    if smooth and P.shape[1] >= window:
        P = savgol_filter(P, window_length=window, polyorder=poly, axis=1)
    peaks = np.argmax(P, axis=1)
    iaf = f[peaks]
    ok = np.max(P, axis=1) > (np.median(P, axis=1) + 1e-12)
    iaf[~ok] = np.nan
    return iaf
