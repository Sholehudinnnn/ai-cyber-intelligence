from datetime import datetime
from pathlib import Path
import json

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split

from predictor import load_model
from risk_engine import analyze_indicators
from agent_helper import explain_result

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
load_dotenv(PROJECT_DIR / ".env")
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))
history = []
FEATURES = ["failed_logins", "unknown_device", "unusual_time", "sensitive_access"]
LABELS = ["RENDAH", "SEDANG", "TINGGI"]


def load_notebook_code():
    path = PROJECT_DIR / "AI_Cyber_Intelligence_Training.ipynb"
    if not path.exists():
        return None
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        return [{"number": i, "source": "".join(cell.get("source", []))}
                for i, cell in enumerate(notebook.get("cells", []), start=1)
                if cell.get("cell_type") == "code" and "".join(cell.get("source", [])).strip()]
    except (OSError, ValueError, TypeError):
        return None


def build_training_info():
    info = {"available": False, "algorithm": "Random Forest", "n_samples": None,
            "accuracy": None, "feature_importance": [], "class_counts": [],
            "confusion_matrix": None,
            "warning": "Dataset sintetis dengan label buatan dari aturan; bukan detektor ancaman akun yang tervalidasi.",
            "error": None}
    try:
        model = load_model()
        info["algorithm"] = type(model).__name__
        feature_names = list(getattr(model, "feature_names_in_", FEATURES))
        if hasattr(model, "feature_importances_"):
            info["feature_importance"] = sorted(
                [{"name": str(name), "value": float(value), "percent": round(float(value)*100, 2)}
                 for name, value in zip(feature_names, model.feature_importances_)],
                key=lambda item: item["value"], reverse=True)
        metadata_path = BASE_DIR / "account_security_metadata.json"
        if not metadata_path.exists(): metadata_path = PROJECT_DIR / "account_security_metadata.json"
        if metadata_path.exists():
            try:
                meta = json.loads(metadata_path.read_text(encoding="utf-8"))
                info["n_samples"] = meta.get("n_samples")
                info["warning"] = meta.get("warning", info["warning"])
            except (OSError, ValueError): pass
        csv_path = next((p for p in [PROJECT_DIR/"data"/"account_security_dataset.csv", PROJECT_DIR/"account_security_dataset.csv"] if p.exists()), None)
        if csv_path:
            data = pd.read_csv(csv_path)
            if all(c in data.columns for c in FEATURES + ["risk_level"]):
                info["n_samples"] = len(data)
                info["class_counts"] = [{"label": lab, "count": int((data["risk_level"] == lab).sum())} for lab in LABELS]
                X, y = data[feature_names].copy(), data["risk_level"].copy()
                _, X_test, _, y_test = train_test_split(X, y, test_size=.20, random_state=42, stratify=y)
                pred = model.predict(X_test)
                info["accuracy"] = round(float(accuracy_score(y_test, pred))*100, 2)
                matrix = confusion_matrix(y_test, pred, labels=LABELS)
                info["confusion_matrix"] = {"labels": LABELS, "rows": matrix.astype(int).tolist()}
        info["available"] = bool(info["feature_importance"])
    except Exception as exc:
        info["error"] = str(exc)
    return info


def render_dashboard(result=None, error=None, status=200):
    return render_template("index.html", history=history[:8], result=result, error=error,
                           training_info=build_training_info(), notebook_code=load_notebook_code()), status


@app.get("/")
def index():
    return render_dashboard()


@app.post("/analyze")
def analyze():
    form = request.form
    try:
        failed_logins = int(form.get("failed_logins", "0"))
        unknown_device = form.get("unknown_device", "no") == "yes"
        unusual_time = form.get("unusual_time", "no") == "yes"
        sensitive_access = form.get("sensitive_access", "no") == "yes"
        if failed_logins < 0 or failed_logins > 100000: raise ValueError
    except (TypeError, ValueError):
        return render_dashboard(error="Masukkan jumlah percobaan login berupa bilangan bulat 0 atau lebih.", status=400)
    result = analyze_indicators(failed_logins, unknown_device, unusual_time, sensitive_access)
    result["time"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    result["details"] = {
        "Percobaan login gagal": str(failed_logins),
        "Perangkat belum dikenal": "Ya" if unknown_device else "Tidak",
        "Waktu akses tidak biasa": "Ya" if unusual_time else "Tidak",
        "Akses ke bagian sensitif": "Ya" if sensitive_access else "Tidak",
    }
    result["explanation"] = explain_result(result)
    probs = result.get("probabilities", {})
    result["probability_rows"] = [{"label": label, "value": round(float(probs.get(label, 0))*100, 2)} for label in LABELS]
    history.insert(0, {"time": result["time"], "level": result["level"], "title": result["title"]})
    del history[8:]
    response, status = render_dashboard(result=result)
    return response, status


@app.get("/health")
def health():
    return {"status": "ok", "mode": "demo-ml"}


if __name__ == "__main__":
    app.run(debug=True)
