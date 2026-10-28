from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.getenv("CLOUD_COST_DB", BASE_DIR / "cloud_cost.db"))
REQUIRED_COLUMNS = ["date", "service", "project", "region", "cost", "currency"]
DEFAULT_THRESHOLDS = {"warning_pct": 20.0, "critical_pct": 50.0, "min_history_days": 7, "mad_z": 3.5}
ALLOWED_CURRENCIES = {"USD", "EUR", "GBP", "INR", "AUD", "CAD", "JPY"}

src_init = ""
