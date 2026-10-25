from pathlib import Path

import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "account_security_model.joblib"

_model = None
_model_error = None


def load_model():
    global _model, _model_error

    if _model is not None:
        return _model

    if _model_error is not None:
        raise RuntimeError(_model_error)

    if not MODEL_PATH.exists():
        _model_error = f"File model tidak ditemukan: {MODEL_PATH.name}"
        raise RuntimeError(_model_error)

    try:
        _model = joblib.load(MODEL_PATH)
        return _model
    except Exception as exc:
        _model_error = f"Model gagal dimuat: {exc}"
        raise RuntimeError(_model_error) from exc


def predict_risk(
    failed_logins,
    unknown_device,
    unusual_time,
    sensitive_access,
):
    model = load_model()

    features = pd.DataFrame([{
        "failed_logins": failed_logins,
        "unknown_device": int(unknown_device),
        "unusual_time": int(unusual_time),
        "sensitive_access": int(sensitive_access),
    }])

    prediction = model.predict(features)[0]

    label = str(prediction).upper()
    label_map = {
        "LOW": "RENDAH",
        "MEDIUM": "SEDANG",
        "HIGH": "TINGGI",
        "RENDAH": "RENDAH",
        "SEDANG": "SEDANG",
        "TINGGI": "TINGGI",
    }

    if label not in label_map:
        raise ValueError(f"Label risiko model tidak dikenal: {label}")

    result = {
        "level": label_map[label],
        "prediction": str(prediction),
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        classes = list(model.classes_)
        result["probabilities"] = {
            str(cls): round(float(prob), 4)
            for cls, prob in zip(classes, probabilities)
        }

    return result