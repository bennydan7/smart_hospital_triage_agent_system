"""
beliefs/data.py
---------------
Shared data structures (beliefs) for the Smart Hospital Triage System.
In Prometheus terminology these are the "Data Descriptions" from Phase 1
and the "Beliefs" column of each agent's Capability Diagram (Phase 3).
"""

from dataclasses import dataclass, field
from typing import Optional
import time


# ── ESI Triage Levels ────────────────────────────────────────────
ESI_1 = 1   # Immediate  – life threatening
ESI_2 = 2   # Emergent   – high risk
ESI_3 = 3   # Urgent     – multiple resources needed
ESI_4 = 4   # Less urgent
ESI_5 = 5   # Non-urgent

ESI_LABELS = {
    1: "IMMEDIATE (ESI-1)",
    2: "EMERGENT  (ESI-2)",
    3: "URGENT    (ESI-3)",
    4: "LESS URG  (ESI-4)",
    5: "NON-URG   (ESI-5)",
}

ESI_COLOURS = {
    1: "\033[91m",   # bright red
    2: "\033[31m",   # red
    3: "\033[33m",   # yellow
    4: "\033[32m",   # green
    5: "\033[37m",   # grey
}
RESET = "\033[0m"


# ── Patient Record (belief held by TriageAgent) ───────────────────
@dataclass
class PatientVitals:
    patient_id: str
    heart_rate: int          # bpm
    spo2: int                # % oxygen saturation
    systolic_bp: int         # mmHg
    respiratory_rate: int    # breaths/min
    temperature: float       # Celsius
    chief_complaint: str
    arrival_time: float = field(default_factory=time.time)


# ── Triage Record (result produced by TriageAgent) ────────────────
@dataclass
class TriageRecord:
    patient_id: str
    esi_level: int
    assigned_ward: Optional[str] = None
    assigned_bed: Optional[str] = None
    triage_time: float = field(default_factory=time.time)
    escalated: bool = False


# ── Bed Record (belief held by ResourceAgent) ─────────────────────
@dataclass
class BedRecord:
    bed_id: str
    ward: str
    occupied: bool = False
    patient_id: Optional[str] = None


# ── Alert Record (belief held by NotificationAgent) ───────────────
@dataclass
class AlertRecord:
    patient_id: str
    esi_level: int
    message: str
    sent_to: str
    sent_at: float = field(default_factory=time.time)


# ── ESI Rule Engine ───────────────────────────────────────────────
# This is the "esi_rule_table" belief of the TriageAgent.
# In Prometheus Phase 3, this is the data the DECIDE step reads.
def apply_esi_rules(vitals: PatientVitals) -> int:
    """
    Prometheus DECIDE step.
    Returns ESI level 1-5 based on patient vitals.
    Rules are checked in priority order (most critical first).
    """
    # ESI-1: Immediate life threat
    if vitals.spo2 < 85 or vitals.heart_rate > 150 or vitals.heart_rate < 30:
        return ESI_1
    if vitals.systolic_bp < 70 or vitals.respiratory_rate > 35:
        return ESI_1

    # ESI-2: High risk / altered mental status
    if vitals.spo2 < 92 or vitals.heart_rate > 130:
        return ESI_2
    if vitals.systolic_bp < 90 or vitals.systolic_bp > 180:
        return ESI_2
    if vitals.temperature > 39.5 or vitals.temperature < 35.0:
        return ESI_2
    if "chest pain" in vitals.chief_complaint.lower():
        return ESI_2
    if "stroke" in vitals.chief_complaint.lower():
        return ESI_2

    # ESI-3: Urgent
    if vitals.spo2 < 95 or vitals.heart_rate > 110:
        return ESI_3
    if vitals.temperature > 38.5:
        return ESI_3
    if "fracture" in vitals.chief_complaint.lower():
        return ESI_3

    # ESI-4: Less urgent
    if vitals.temperature > 37.5 or vitals.heart_rate > 95:
        return ESI_4

    # ESI-5: Non-urgent
    return ESI_5


# ── Ward assignment by ESI level ─────────────────────────────────
def get_target_ward(esi_level: int) -> str:
    mapping = {
        ESI_1: "Resus",
        ESI_2: "ICU",
        ESI_3: "Acute",
        ESI_4: "General",
        ESI_5: "Waiting",
    }
    return mapping[esi_level]
