# Intelligent Cloud Cost Anomaly Detection

A runnable Streamlit application for evidence-based cloud billing anomaly detection. It ingests CSV/Excel billing exports, validates and normalizes records, builds robust historical baselines, detects spikes/drops, ranks cost drivers, persists results in SQLite, supports alert review, and exports auditable reports.

## Specification note
The referenced `CSE_18_Intelligent_Cloud_Cost_Anomaly_Detection.pdf` was not included in the provided workspace. This implementation therefore follows the supplied project brief as the primary specification and does not claim PDF-specific requirements beyond that brief.

## Quick start

### macOS/Linux
```bash
cd cloud-cost-anomaly-detection
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
streamlit run app.py
```

### Windows PowerShell
```powershell
cd cloud-cost-anomaly-detection
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest -q
streamlit run app.py
```

The app starts with a synthetic sample selected by default. Upload a CSV/XLSX file in the sidebar to analyze real billing exports. No cloud credentials or paid APIs are required.

## Input format
Required columns: `date`, `service`, `project`, `region`, `cost`, `currency`. Optional columns `usage_quantity` and `unit_rate` enable usage-versus-rate analysis. Dates must be parseable, cost must be non-negative, and currencies are checked against a conservative supported list. Duplicate records are reported and suppressed from analysis. Validation errors can be downloaded.

## Methodology
Records are normalized to daily grain and aggregated by billing dimensions. Baselines use a previous-period comparison plus rolling mean/median and median absolute deviation (MAD). The app safely handles zero baselines by reporting an unavailable percentage difference instead of dividing by zero. An anomaly is flagged when the configured percentage or robust MAD z-score threshold is met after minimum history is available. Severity is informational, warning, or critical. Incomplete periods and insufficient history are surfaced through method/history fields and should be investigated before acting.

Explanations separate observed facts from hypotheses. Recommendations are investigation-only: the system never changes infrastructure automatically. SQLite stores billing records, analyses, anomaly rows, alerts, reviewer status, notes, and settings-ready schema.

## Deliverables
- `app.py`: dashboard and end-to-end workflow.
- `src/validation.py`, `normalization.py`, `baseline.py`, `cost_drivers.py`, `explanations.py`, `database.py`, `exports.py`: modular business logic.
- `data/sample_billing.csv`: synthetic demo data with spike/drop and usage/rate examples.
- `tests/test_core.py`: automated unit/integration tests.
- `docs/architecture.mmd`: system architecture diagram source.
- `docs/project_report.md`: concise project report.

## Limitations and future scope
The app assumes supplied currencies are comparable; it does not perform foreign-exchange conversion. It does not connect to AWS/Azure/GCP APIs, infer billing period completeness from provider calendars, or automatically remediate infrastructure. Future scope includes provider adapters, currency conversion, seasonality-aware forecasting, role-based access, scheduled ingestion, and notification integrations.
