import numpy as np
import matplotlib.pyplot as plt
from .utils import resolve_channels, builtin_montage_path

def plot_psd(freqs, psd, title="PSD", out_png=None):
    plt.figure()
    plt.plot(freqs, psd.T, alpha=0.3)
    plt.xlabel("Hz"); plt.ylabel("PSD")
    plt.title(title)
    if out_png:
        plt.savefig(out_png, dpi=150, bbox_inches="tight")
        plt.close()
    else:
        plt.show()
