from dataclasses import dataclass

@dataclass
class Band:
    name: str
    fmin: float
    fmax: float

# Default bands
DEFAULT_BANDS = [
    Band("delta", 1.0, 4.0),
    Band("theta", 4.0, 7.0),
    Band("alpha", 8.0, 13.0),
    Band("beta", 13.0, 30.0),
    Band("gamma", 30.0, 45.0),
]
