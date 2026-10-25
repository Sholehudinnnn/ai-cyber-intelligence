import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "04_app_pipeline"))
from risk_engine import analyze_indicators

def test_no_indicators_is_low():
    result = analyze_indicators(0, False, False, False)
    assert result["level"] == "RENDAH"
    assert result["is_demo"] is True

def test_multiple_indicators_raise_risk():
    result = analyze_indicators(10, True, True, True)
    assert result["level"] == "TINGGI"
    assert result["score"] == 100
