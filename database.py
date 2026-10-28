from __future__ import annotations
import json, sqlite3
from pathlib import Path
import pandas as pd

class Database:
    def __init__(self, path):
        self.path = str(path); self.init()
    def connect(self): return sqlite3.connect(self.path)
    def init(self):
        with self.connect() as c:
            c.executescript('''CREATE TABLE IF NOT EXISTS billing_records (id INTEGER PRIMARY KEY, run_id TEXT, record_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS analyses (run_id TEXT PRIMARY KEY, metadata_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS anomalies (id INTEGER PRIMARY KEY, run_id TEXT, anomaly_json TEXT);
            CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, fingerprint TEXT UNIQUE, status TEXT DEFAULT 'open', acknowledged_by TEXT, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, fingerprint TEXT, note TEXT, author TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);''')
    def save_run(self, run_id, billing, anomalies, metadata):
        with self.connect() as c:
            c.execute("INSERT OR REPLACE INTO analyses VALUES (?,?,datetime('now'))", (run_id, json.dumps(metadata, default=str)))
            c.executemany("INSERT INTO billing_records(run_id,record_json) VALUES (?,?)", [(run_id, json.dumps(x, default=str)) for x in billing.to_dict('records')])
            c.executemany("INSERT INTO anomalies(run_id,anomaly_json) VALUES (?,?)", [(run_id, json.dumps(x, default=str)) for x in anomalies.to_dict('records')])
    def upsert_alert(self, fingerprint):
        with self.connect() as c: c.execute("INSERT OR IGNORE INTO alerts(fingerprint) VALUES (?)", (fingerprint,))
    def alerts(self):
        with self.connect() as c: return pd.read_sql_query("SELECT * FROM alerts ORDER BY updated_at DESC", c)
    def update_alert(self, alert_id, status, reviewer):
        with self.connect() as c: c.execute("UPDATE alerts SET status=?, acknowledged_by=?, updated_at=datetime('now') WHERE id=?", (status, reviewer, alert_id))
    def add_note(self, fingerprint, note, author):
        with self.connect() as c: c.execute("INSERT INTO notes(fingerprint,note,author) VALUES (?,?,?)", (fingerprint, note, author))
