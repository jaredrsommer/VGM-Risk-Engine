import numpy as np

def build_dataset(prices, vgm_engine):
    X, Y = [], []

    for i in range(30, len(prices)):
        f = extract_features(prices, i)

        risk = vgm_engine.score(**f)

        X.append(list(f.values()))
        Y.append(risk)

    return np.array(X), np.array(Y)