import json
from pathlib import Path

import joblib


PROJECT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_DIR / "04_app_pipeline" / "account_security_model.joblib"
OUTPUT_PATH = PROJECT_DIR / "docs" / "model.json"


def export_model():
    model = joblib.load(MODEL_PATH)
    payload = {
        "algorithm": type(model).__name__,
        "features": list(model.feature_names_in_),
        "classes": [str(label) for label in model.classes_],
        "trees": [],
    }
    for estimator in model.estimators_:
        tree = estimator.tree_
        payload["trees"].append({
            "left": tree.children_left.tolist(),
            "right": tree.children_right.tolist(),
            "feature": tree.feature.tolist(),
            "threshold": tree.threshold.tolist(),
            "values": tree.value[:, 0, :].tolist(),
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Exported {len(payload['trees'])} trees to {OUTPUT_PATH}")


if __name__ == "__main__":
    export_model()
