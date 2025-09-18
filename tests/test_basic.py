import numpy as np
from eegspec.psd import compute_psd_welch
from eegspec.features import bandpower
from eegspec.faa import faa_from_psd

def test_alpha_peak():
    sfreq = 500.0
    t = np.arange(0, 8, 1/sfreq)
    F3 = 1.0*np.sin(2*np.pi*10*t)
    F4 = 2.0*np.sin(2*np.pi*10*t)
    data = np.column_stack([F3, F4])
    freqs, psd = compute_psd_welch(data, sfreq, nperseg=1024, noverlap=512)
    bp = bandpower(psd, freqs, {"alpha": (8,13)})
    assert bp["alpha"][1] > bp["alpha"][0]  # F4 > F3

def test_faa_sign():
    sfreq = 500.0
    t = np.arange(0, 8, 1/sfreq)
    F3 = 1.0*np.sin(2*np.pi*10*t)
    F4 = 2.0*np.sin(2*np.pi*10*t)
    data = np.column_stack([F3, F4])
    freqs, psd = compute_psd_welch(data, sfreq, nperseg=1024, noverlap=512)
    faa = faa_from_psd(psd, freqs, ["F3","F4"], left="F3", right="F4", alpha=(8,13))
    assert faa > 0  # right alpha > left -> ln(PR)-ln(PL) > 0
