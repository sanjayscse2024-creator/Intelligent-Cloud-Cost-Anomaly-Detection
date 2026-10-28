from __future__ import annotations
import uuid
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from config import DATA_DIR, DB_PATH, DEFAULT_THRESHOLDS
from src.validation import read_billing_file, validate_billing
from src.normalization import normalize_billing
from src.baseline import detect_anomalies
from src.cost_drivers import rank_cost_drivers, usage_rate_analysis
from src.explanations import explain
from src.database import Database
from src.exports import csv_bytes, json_bytes

st.set_page_config(page_title="Cloud Cost Anomaly Detection", page_icon="☁", layout="wide")
st.title("Intelligent Cloud Cost Anomaly Detection")
st.caption("Evidence-first monitoring for billing data. This app recommends investigation; it never changes infrastructure automatically.")
db = Database(DB_PATH)

with st.sidebar:
    st.header("Data source")
    uploaded = st.file_uploader("Upload CSV or Excel billing data", type=["csv", "xlsx", "xls"])
    use_sample = st.checkbox("Use synthetic sample data", value=uploaded is None)
    st.header("Detection thresholds")
    warning = st.number_input("Warning deviation (%)", 1.0, 500.0, DEFAULT_THRESHOLDS["warning_pct"])
    critical = st.number_input("Critical deviation (%)", 1.0, 1000.0, DEFAULT_THRESHOLDS["critical_pct"])
    mad_z = st.number_input("Median/MAD z-score", 1.0, 20.0, DEFAULT_THRESHOLDS["mad_z"])
    min_history = st.number_input("Minimum history points", 1, 365, DEFAULT_THRESHOLDS["min_history_days"])

@st.cache_data(show_spinner=False)
def load_sample(): return pd.read_csv(DATA_DIR / "sample_billing.csv")

if uploaded is not None:
    try: raw = read_billing_file(uploaded)
    except Exception as e: st.error(f"Could not read file: {e}"); st.stop()
elif use_sample: raw = load_sample()
else: st.info("Upload a file or select the synthetic sample to begin."); st.stop()

cleaned, errors, summary = validate_billing(raw)
with st.expander("Validation summary", expanded=not summary["valid"]):
    st.write({k: v for k, v in summary.items()})
    if not errors.empty:
        st.dataframe(errors, use_container_width=True)
        st.download_button("Download validation errors", csv_bytes(errors), "validation_errors.csv", "text/csv")
if cleaned.empty: st.error("No usable records remain after validation."); st.stop()

df = normalize_billing(cleaned)
result = detect_anomalies(df, warning_pct=warning, critical_pct=critical, mad_z=mad_z, min_history=min_history)
run_id = str(uuid.uuid4())
metadata = {"run_id": run_id, "thresholds": {"warning_pct": warning, "critical_pct": critical, "mad_z": mad_z, "min_history": min_history}, "assumptions": ["Costs are comparable within the supplied currency.", "Missing/incomplete periods can weaken baselines."], "limitations": ["Synthetic data is illustrative only.", "No automatic remediation is performed."], "exclusions": []}

anoms = result[result["is_anomaly"]].copy()
for _, r in anoms.iterrows(): db.upsert_alert(f"{r['date']}|{r['service']}|{r['project']}|{r['region']}")
try: db.save_run(run_id, df, anoms, metadata)
except Exception as e: st.warning(f"Persistence warning: {e}")

k1,k2,k3,k4 = st.columns(4)
k1.metric("Total spend", f"{df.cost.sum():,.2f} {df.currency.iloc[0]}")
k2.metric("Billing records", f"{len(df):,}")
k3.metric("Anomalies", f"{len(anoms):,}")
k4.metric("Critical alerts", f"{(anoms.severity == 'critical').sum():,}")

st.subheader("Spend trend")
trend = df.groupby("date", as_index=False).cost.sum()
fig = px.line(trend, x="date", y="cost", markers=True, template="plotly_white")
fig.update_layout(yaxis_title="Cost", xaxis_title="Date")
st.plotly_chart(fig, use_container_width=True)

c1,c2 = st.columns(2)
with c1:
    st.subheader("Service breakdown")
    st.plotly_chart(px.bar(rank_cost_drivers(df, ("service",)), x="service", y="cost", template="plotly_white"), use_container_width=True)
with c2:
    st.subheader("Project breakdown")
    st.plotly_chart(px.bar(rank_cost_drivers(df, ("project",)), x="project", y="cost", template="plotly_white"), use_container_width=True)

st.subheader("Anomaly timeline")
if anoms.empty: st.success("No anomalies detected at the current thresholds.")
else:
    timeline = px.scatter(anoms, x="date", y="cost", color="severity", size="anomaly_score", hover_data=["service","project","region","baseline_cost","percentage_difference","method"], template="plotly_white")
    st.plotly_chart(timeline, use_container_width=True)
    st.dataframe(anoms[["date","service","project","region","cost","baseline_cost","absolute_difference","percentage_difference","severity","anomaly_score","method"]].sort_values("date", ascending=False), use_container_width=True)
    selected = st.selectbox("Inspect anomaly", anoms.index, format_func=lambda i: f"{anoms.loc[i, 'date'].date()} · {anoms.loc[i, 'service']} · {anoms.loc[i, 'severity']}")
    details = explain(anoms.loc[selected])
    d1,d2,d3 = st.columns(3)
    d1.markdown("**Facts**\n\n" + "\n\n".join(f"- {x}" for x in details["facts"]))
    d2.markdown("**Hypotheses (verify)**\n\n" + "\n\n".join(f"- {x}" for x in details["hypotheses"]))
    d3.markdown("**Safe investigation**\n\n" + "\n\n".join(f"- {x}" for x in details["recommendations"]))

st.subheader("Cost drivers and usage-versus-rate")
st.dataframe(rank_cost_drivers(df), use_container_width=True)
usage = usage_rate_analysis(df)
if usage.empty: st.info("Usage-versus-rate analysis is available when usage_quantity and unit_rate columns are supplied.")
else: st.dataframe(usage, use_container_width=True)

st.subheader("Alerts and review")
alerts = db.alerts()
if alerts.empty: st.info("No persisted alerts yet.")
else:
    st.dataframe(alerts, use_container_width=True)
    with st.form("review_form"):
        alert_id = st.number_input("Alert ID", min_value=1, step=1)
        reviewer = st.text_input("Reviewer", "analyst")
        status = st.selectbox("Status", ["open", "acknowledged", "resolved"])
        note = st.text_area("Reviewer note")
        if st.form_submit_button("Save review"):
            db.update_alert(int(alert_id), status, reviewer)
            if note.strip(): db.add_note(str(alert_id), note.strip(), reviewer)
            st.success("Review saved. Refresh to see the updated state.")

st.subheader("Exports")
st.download_button("Download anomaly CSV", csv_bytes(anoms), "anomalies.csv", "text/csv")
st.download_button("Download audit JSON", json_bytes(anoms, metadata), "anomaly_report.json", "application/json")
