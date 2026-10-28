from __future__ import annotations
import numpy as np
import pandas as pd


def add_baselines(df: pd.DataFrame, group_cols=("service", "project", "region"), window=7) -> pd.DataFrame:
    out = df.sort_values([*group_cols, "date"]).copy()
    g = out.groupby(list(group_cols), group_keys=False)["cost"]
    out["previous_cost"] = g.shift(1)
    out["rolling_mean"] = g.transform(lambda s: s.shift(1).rolling(window, min_periods=3).mean())
    out["rolling_median"] = g.transform(lambda s: s.shift(1).rolling(window, min_periods=3).median())
    out["rolling_mad"] = g.transform(lambda s: s.shift(1).rolling(window, min_periods=3).apply(lambda x: np.median(np.abs(x - np.median(x))), raw=True))
    out["baseline_cost"] = out["rolling_median"].fillna(out["rolling_mean"]).fillna(out["previous_cost"])
    out["history_points"] = g.transform(lambda s: s.shift(1).expanding().count())
    return out


def detect_anomalies(df: pd.DataFrame, warning_pct=20.0, critical_pct=50.0, mad_z=3.5, min_history=3) -> pd.DataFrame:
    out = add_baselines(df)
    baseline = out["baseline_cost"]
    out["absolute_difference"] = out["cost"] - baseline
    out["percentage_difference"] = np.where(baseline.abs() > 1e-9, out["absolute_difference"] / baseline.abs() * 100, np.nan)
    robust_scale = (1.4826 * out["rolling_mad"]).replace(0, np.nan)
    out["robust_z"] = (out["cost"] - baseline) / robust_scale
    out["method"] = np.where(out["robust_z"].abs() >= mad_z, "median/MAD", np.where(out["previous_cost"].notna(), "previous-period", "insufficient-history"))
    pct = out["percentage_difference"].abs().fillna(0)
    is_anomaly = (out["history_points"] >= min_history) & ((pct >= warning_pct) | (out["robust_z"].abs() >= mad_z))
    out["is_anomaly"] = is_anomaly
    out["direction"] = np.where(out["absolute_difference"] >= 0, "spike", "drop")
    out["severity"] = np.select([pct >= critical_pct, pct >= warning_pct, is_anomaly], ["critical", "warning", "informational"], default="normal")
    out["anomaly_score"] = np.maximum(pct.fillna(0) / max(critical_pct, 1), out["robust_z"].abs().fillna(0) / mad_z).round(3)
    return out
