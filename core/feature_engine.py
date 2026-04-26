import numpy as np

def features(x, i, w=25):
    if i < w:
        return None

    s = x[i-w:i]
    r = np.diff(s)

    return {
        "vol": np.std(r),
        "tail": abs(np.percentile(r, 5)),
        "mom": s[-1] - s[0],
        "grad": r[-1],
        "ent": np.std(r) / (np.mean(np.abs(r)) + 1e-8)
    }