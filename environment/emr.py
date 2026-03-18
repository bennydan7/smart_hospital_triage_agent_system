"""
environment/emr.py
------------------
Mock Electronic Medical Records database and bed registry.
In Prometheus Phase 1 these are the external environment entities
that agents perceive from and act upon.
"""

import sqlite3
import os

DB_PATH = "/tmp/triage_emr.db"


def init_db():
    """Create the mock EMR database with some pre-loaded beds."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Bed registry (ResourceAgent's environment)
    c.execute("""
        CREATE TABLE beds (
            bed_id TEXT PRIMARY KEY,
            ward TEXT,
            occupied INTEGER DEFAULT 0,
            patient_id TEXT
        )
    """)

    # Triage records (shared log)
    c.execute("""
        CREATE TABLE triage_log (
            patient_id TEXT,
            esi_level INTEGER,
            ward TEXT,
            bed_id TEXT,
            triage_time REAL,
            escalated INTEGER DEFAULT 0
        )
    """)

    # Alert log (NotificationAgent's environment)
    c.execute("""
        CREATE TABLE alert_log (
            patient_id TEXT,
            esi_level INTEGER,
            message TEXT,
            sent_to TEXT,
            sent_at REAL
        )
    """)

    # Seed the bed registry
    beds = [
        ("Resus-01", "Resus"), ("Resus-02", "Resus"),
        ("ICU-01",   "ICU"),   ("ICU-02",   "ICU"),   ("ICU-03", "ICU"),
        ("Acute-01", "Acute"), ("Acute-02", "Acute"), ("Acute-03", "Acute"),
        ("Gen-01",   "General"),("Gen-02",  "General"),("Gen-03", "General"),
        ("Wait-01",  "Waiting"),("Wait-02", "Waiting"),("Wait-03", "Waiting"),
    ]
    c.executemany("INSERT INTO beds VALUES (?,?,0,NULL)", beds)
    conn.commit()
    conn.close()
    print("[EMR] Database initialised with", len(beds), "beds.")


def query_available_bed(ward: str) -> str | None:
    """Find the first available bed in the given ward. Returns bed_id or None."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT bed_id FROM beds WHERE ward=? AND occupied=0 LIMIT 1", (ward,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def allocate_bed(bed_id: str, patient_id: str) -> bool:
    """Mark a bed as occupied. Returns True on success."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE beds SET occupied=1, patient_id=? WHERE bed_id=? AND occupied=0",
              (patient_id, bed_id))
    changed = c.rowcount > 0
    conn.commit()
    conn.close()
    return changed


def free_bed(bed_id: str):
    """Release a bed back to available."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE beds SET occupied=0, patient_id=NULL WHERE bed_id=?", (bed_id,))
    conn.commit()
    conn.close()


def log_triage(record):
    """Write a triage result to the EMR log."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO triage_log VALUES (?,?,?,?,?,?)",
        (record.patient_id, record.esi_level, record.assigned_ward,
         record.assigned_bed, record.triage_time, int(record.escalated))
    )
    conn.commit()
    conn.close()


def log_alert(alert):
    """Write an alert to the alert log."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO alert_log VALUES (?,?,?,?,?)",
        (alert.patient_id, alert.esi_level, alert.message,
         alert.sent_to, alert.sent_at)
    )
    conn.commit()
    conn.close()


def get_triage_summary():
    """Return all triage records for the demo dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM triage_log ORDER BY triage_time DESC")
    rows = c.fetchall()
    conn.close()
    return rows
