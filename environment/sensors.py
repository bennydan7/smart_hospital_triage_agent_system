"""
environment/sensors.py
----------------------
Simulates IoT wristband sensor streams and patient arrivals.
In Prometheus Phase 1 these are the PERCEPTS entering the system.
The simulator feeds data into the agents' message queues.
"""

import asyncio
import random
import time
from beliefs.data import PatientVitals

# ── Pre-defined patient scenarios ────────────────────────────────
# Each scenario is designed to hit a specific ESI level so you can
# demonstrate the Percept→Decide→Act loop clearly in your demo.

PATIENT_SCENARIOS = [
    PatientVitals(
        patient_id="P001",
        heart_rate=155,      # ESI-1: tachycardia
        spo2=82,             # ESI-1: dangerously low O2
        systolic_bp=65,
        respiratory_rate=38,
        temperature=38.2,
        chief_complaint="Cardiac arrest, unresponsive",
    ),
    PatientVitals(
        patient_id="P002",
        heart_rate=125,      # ESI-2: high risk
        spo2=89,
        systolic_bp=88,
        respiratory_rate=24,
        temperature=38.8,
        chief_complaint="Chest pain, shortness of breath",
    ),
    PatientVitals(
        patient_id="P003",
        heart_rate=112,      # ESI-3: urgent
        spo2=93,
        systolic_bp=110,
        respiratory_rate=20,
        temperature=38.6,
        chief_complaint="Right leg fracture after fall",
    ),
    PatientVitals(
        patient_id="P004",
        heart_rate=98,       # ESI-4: less urgent
        spo2=97,
        systolic_bp=130,
        respiratory_rate=17,
        temperature=37.8,
        chief_complaint="Sore throat and mild fever",
    ),
    PatientVitals(
        patient_id="P005",
        heart_rate=72,       # ESI-5: non-urgent
        spo2=99,
        systolic_bp=120,
        respiratory_rate=15,
        temperature=36.8,
        chief_complaint="Minor cut on finger, no active bleeding",
    ),
]


def get_scenario(patient_id: str) -> PatientVitals | None:
    """Return the pre-defined scenario for a patient, or None."""
    for p in PATIENT_SCENARIOS:
        if p.patient_id == patient_id:
            # Refresh arrival time
            p.arrival_time = time.time()
            return p
    return None


def random_deterioration(vitals: PatientVitals) -> PatientVitals:
    """
    Simulates a patient deteriorating mid-wait.
    Used by the MonitorAgent demo to show re-triage.
    Drops SpO2 and raises heart rate to push ESI level up.
    """
    import copy
    worse = copy.copy(vitals)
    worse.spo2 = max(80, vitals.spo2 - random.randint(5, 12))
    worse.heart_rate = min(170, vitals.heart_rate + random.randint(15, 30))
    return worse
