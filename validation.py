from __future__ import annotations
import pandas as pd
from config import REQUIRED_COLUMNS, ALLOWED_CURRENCIES


def validate_billing(df: pd.DataFrame):
    """Return cleaned frame, row-level errors, and summary metadata."""
    errors = []
    original = df.copy()
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return pd.DataFrame(), pd.DataFrame([{"row": 0, "column": ", ".join(missing), "error": "Missing required column(s)"}]), {"valid": False, "duplicates": 0, "rows": len(df)}
    out = df.copy()
    out.columns = [str(c).strip().lower() for c in out.columns]
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    numeric = pd.to_numeric(out["cost"], errors="coerce")
    for i, row in out.iterrows():
        excel_row = int(i) + 2
        if pd.isna(row["date"]): errors.append({"row": excel_row, "column": "date", "error": "Invalid or missing date"})
        if pd.isna(numeric.loc[i]) or numeric.loc[i] < 0: errors.append({"row": excel_row, "column": "cost", "error": "Cost must be a non-negative number"})
        if not str(row["currency"]).upper() in ALLOWED_CURRENCIES: errors.append({"row": excel_row, "column": "currency", "error": f"Unsupported currency; expected one of {sorted(ALLOWED_CURRENCIES)}"})
        for col in ["service", "project", "region"]:
            if pd.isna(row[col]) or not str(row[col]).strip(): errors.append({"row": excel_row, "column": col, "error": "Missing dimension value"})
    out["cost"] = numeric
    out["currency"] = out["currency"].astype(str).str.upper().str.strip()
    duplicate_mask = out.duplicated(subset=REQUIRED_COLUMNS, keep="first")
    duplicate_count = int(duplicate_mask.sum())
    for i in out.index[duplicate_mask]: errors.append({"row": int(i)+2, "column": "*", "error": "Duplicate billing record"})
    cleaned = out.loc[~duplicate_mask].dropna(subset=["date", "cost"]).copy()
    cleaned["date"] = cleaned["date"].dt.normalize()
    err_df = pd.DataFrame(errors, columns=["row", "column", "error"])
    summary = {"valid": len(errors) == 0, "duplicates": duplicate_count, "rows": len(original), "accepted_rows": len(cleaned), "error_count": len(errors)}
    return cleaned, err_df, summary


def read_billing_file(uploaded_file) -> pd.DataFrame:
    name = getattr(uploaded_file, "name", "billing.csv").lower()
    return pd.read_excel(uploaded_file) if name.endswith((".xlsx", ".xls")) else pd.read_csv(uploaded_file)
