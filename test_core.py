import pandas as pd
from src.validation import validate_billing
from src.baseline import detect_anomalies
from src.database import Database

def frame():
    return pd.DataFrame({"date": pd.date_range("2026-01-01", periods=8), "service":["A"]*8, "project":["P"]*8, "region":["R"]*8, "cost":[10,11,9,10,12,11,10,50], "currency":["USD"]*8})

def test_validation_detects_duplicate_and_invalid_currency():
    d = frame(); d.loc[1, "currency"] = "ZZZ"; d = pd.concat([d, d.iloc[[0]]], ignore_index=True)
    cleaned, errors, summary = validate_billing(d)
    assert summary["duplicates"] == 1
    assert "currency" in set(errors.column)
    assert len(cleaned) == 8

def test_anomaly_spike_is_detected():
    cleaned, errors, summary = validate_billing(frame())
    out = detect_anomalies(cleaned, warning_pct=20, critical_pct=50, min_history=3)
    assert out.iloc[-1].is_anomaly
    assert out.iloc[-1].direction == "spike"
    assert out.iloc[-1].baseline_cost > 0

def test_sqlite_round_trip(tmp_path):
    db = Database(tmp_path / "test.db")
    db.save_run("run", frame(), frame().iloc[[0]], {"x": 1})
    db.upsert_alert("fingerprint")
    assert len(db.alerts()) == 1
