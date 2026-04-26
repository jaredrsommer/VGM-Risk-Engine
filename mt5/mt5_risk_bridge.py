import onnxruntime as ort
import numpy as np

class MT5RiskFilter:
    def __init__(self):
        self.model = ort.InferenceSession("vgm_risk.onnx")

    def predict(self, features):
        x = np.array(features, dtype=np.float32).reshape(1, -1)

        risk = self.model.run(None, {"features": x})[0][0]

        if risk > 0.7:
            return "BLOCK"
        elif risk > 0.5:
            return "REDUCE"
        return "ALLOW"