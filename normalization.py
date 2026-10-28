from __future__ import annotations
import pandas as pd


def normalize_billing(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"]).dt.normalize()
    for col in ["service", "project", "region"]: out[col] = out[col].astype(str).str.strip()
    out["cost"] = pd.to_numeric(out["cost"], errors="coerce").fillna(0.0)
    return out


def aggregate(df: pd.DataFrame, dimensions=("date", "service", "project", "region")) -> pd.DataFrame:
    return df.groupby(list(dimensions), as_index=False, dropna=False).agg(cost=("cost", "sum"), currency=("currency", "first"))
