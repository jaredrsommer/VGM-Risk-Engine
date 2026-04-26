import torch

def export(model):
    dummy = torch.randn(1, 5)

    torch.onnx.export(
        model,
        dummy,
        "vgm_risk.onnx",
        input_names=["features"],
        output_names=["risk"],
        opset_version=12,
        dynamic_axes=None
    )

    print("✅ ONNX ready for MT5")