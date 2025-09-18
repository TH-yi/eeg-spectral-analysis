import numpy as np
from eegspec.psd import compute_psd_welch
from eegspec.features import bandpower
from eegspec.faa import faa_from_psd

sfreq = 500.0
t = np.arange(0, 10, 1/sfreq)
# 10 Hz alpha on two channels with different amplitudes
F3 = 1.0*np.sin(2*np.pi*10*t) + 0.1*np.random.randn(len(t))
F4 = 1.5*np.sin(2*np.pi*10*t) + 0.1*np.random.randn(len(t))
data = np.column_stack([F3, F4])
freqs, psd = compute_psd_welch(data, sfreq, nperseg=1024, noverlap=512)
bp = bandpower(psd, freqs, {"alpha": (8,13)}, relative=False)
faa = faa_from_psd(psd, freqs, ["F3","F4"], left="F3", right="F4", alpha=(8,13))
print("Alpha powers:", {k: v.tolist() for k,v in bp.items()})
print("FAA:", faa)
