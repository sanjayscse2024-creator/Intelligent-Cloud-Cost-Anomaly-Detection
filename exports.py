from __future__ import annotations
import json
import pandas as pd

def csv_bytes(df): return df.to_csv(index=False).encode('utf-8')
def json_bytes(df, metadata):
    return json.dumps({"metadata": metadata, "records": df.to_dict('records')}, indent=2, default=str).encode('utf-8')
