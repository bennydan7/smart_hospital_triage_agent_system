"""
protocols/messages.py
---------------------
FIPA-ACL message definitions for the Smart Hospital Triage System.
In Prometheus Phase 2 these are the Interaction Protocols between agents.

FIPA-ACL Performatives used:
  INFORM  – "Here is a fact you should know"
  REQUEST – "Please perform this action"
  CONFIRM – "I have done what you asked"
  FAILURE – "I could not do what you asked"
  SUBSCRIBE – "Keep telling me when X changes"
"""

import json
from spade.message import Message

# ── XMPP addresses (SPADE uses XMPP under the hood) ──────────────
# In a real deployment these would be registered on an XMPP server.
# We use a local mock XMPP via SPADE's built-in server.

TRIAGE_JID       = "triage@localhost"
RESOURCE_JID     = "resource@localhost"
NOTIFICATION_JID = "notification@localhost"
MONITOR_JID      = "monitor@localhost"

# ── Ontology tags (used to route messages to the right behaviour) ─
ONT_REGISTER      = "patient_register"     # new patient arriving
ONT_TRIAGE_RESULT = "triage_result"        # TriageAgent → NotificationAgent
ONT_BED_REQUEST   = "bed_request"          # TriageAgent → ResourceAgent
ONT_BED_CONFIRM   = "bed_confirm"          # ResourceAgent → TriageAgent
ONT_BED_FAILURE   = "bed_failure"          # ResourceAgent → TriageAgent
ONT_SUBSCRIBE     = "monitor_subscribe"    # TriageAgent → MonitorAgent
ONT_DETERIORATION = "deterioration_alert"  # MonitorAgent → TriageAgent
ONT_RETRIAGE      = "retriage_request"     # TriageAgent internal re-trigger


# ── Message builders ─────────────────────────────────────────────

def make_register_msg(vitals) -> Message:
    """Main → TriageAgent: new patient arriving with vitals."""
    msg = Message(to=TRIAGE_JID)
    msg.set_metadata("performative", "inform")
    msg.set_metadata("ontology", ONT_REGISTER)
    msg.body = json.dumps({
        "patient_id":        vitals.patient_id,
        "heart_rate":        vitals.heart_rate,
        "spo2":              vitals.spo2,
        "systolic_bp":       vitals.systolic_bp,
        "respiratory_rate":  vitals.respiratory_rate,
        "temperature":       vitals.temperature,
        "chief_complaint":   vitals.chief_complaint,
    })
    return msg


def make_bed_request_msg(patient_id: str, esi_level: int, ward: str) -> Message:
    """TriageAgent → ResourceAgent: request bed allocation."""
    msg = Message(to=RESOURCE_JID)
    msg.set_metadata("performative", "request")
    msg.set_metadata("ontology", ONT_BED_REQUEST)
    msg.body = json.dumps({
        "patient_id": patient_id,
        "esi_level":  esi_level,
        "ward":       ward,
    })
    return msg


def make_bed_confirm_msg(patient_id: str, bed_id: str, ward: str) -> Message:
    """ResourceAgent → TriageAgent: bed successfully allocated."""
    msg = Message(to=TRIAGE_JID)
    msg.set_metadata("performative", "confirm")
    msg.set_metadata("ontology", ONT_BED_CONFIRM)
    msg.body = json.dumps({
        "patient_id": patient_id,
        "bed_id":     bed_id,
        "ward":       ward,
    })
    return msg


def make_bed_failure_msg(patient_id: str, ward: str) -> Message:
    """ResourceAgent → TriageAgent: no beds available."""
    msg = Message(to=TRIAGE_JID)
    msg.set_metadata("performative", "failure")
    msg.set_metadata("ontology", ONT_BED_FAILURE)
    msg.body = json.dumps({
        "patient_id": patient_id,
        "ward":       ward,
        "reason":     "NO_BED_AVAILABLE",
    })
    return msg


def make_triage_result_msg(record) -> Message:
    """TriageAgent → NotificationAgent: inform of triage outcome."""
    msg = Message(to=NOTIFICATION_JID)
    msg.set_metadata("performative", "inform")
    msg.set_metadata("ontology", ONT_TRIAGE_RESULT)
    msg.body = json.dumps({
        "patient_id":    record.patient_id,
        "esi_level":     record.esi_level,
        "assigned_ward": record.assigned_ward,
        "assigned_bed":  record.assigned_bed,
        "escalated":     record.escalated,
    })
    return msg


def make_subscribe_msg(patient_id: str, vitals_dict: dict) -> Message:
    """TriageAgent → MonitorAgent: subscribe to vitals monitoring."""
    msg = Message(to=MONITOR_JID)
    msg.set_metadata("performative", "subscribe")
    msg.set_metadata("ontology", ONT_SUBSCRIBE)
    msg.body = json.dumps({
        "patient_id": patient_id,
        "vitals":     vitals_dict,
    })
    return msg


def make_deterioration_msg(patient_id: str, new_vitals: dict) -> Message:
    """MonitorAgent → TriageAgent: patient has deteriorated."""
    msg = Message(to=TRIAGE_JID)
    msg.set_metadata("performative", "inform")
    msg.set_metadata("ontology", ONT_DETERIORATION)
    msg.body = json.dumps({
        "patient_id": patient_id,
        "new_vitals": new_vitals,
    })
    return msg
