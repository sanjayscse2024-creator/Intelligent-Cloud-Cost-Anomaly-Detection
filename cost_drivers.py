import pandas as pd


def rank_cost_drivers(df: pd.DataFrame, dimensions=("service", "project", "region")) -> pd.DataFrame:
    if df.empty: return pd.DataFrame(columns=[*dimensions, "cost", "share_pct"])
    out = df.groupby(list(dimensions), as_index=False)["cost"].sum().sort_values("cost", ascending=False)
    total = out["cost"].sum()
    out["share_pct"] = (out["cost"] / total * 100).round(2) if total else 0
    return out


def usage_rate_analysis(df: pd.DataFrame) -> pd.DataFrame:
    cols = {"usage_quantity", "unit_rate"}
    if not cols.issubset(df.columns): return pd.DataFrame()
    out = df.copy(); out["expected_cost"] = out["usage_quantity"] * out["unit_rate"]
    out["rate_variance"] = out["cost"] - out["expected_cost"]
    return out
