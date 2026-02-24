"""Centralized stage definitions for the entire application.

This is the single source of truth for all deal stages.
Every other file imports from here — no hardcoded stage maps elsewhere.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class StageDefinition:
    numeric: int
    key: str        # e.g. "1-Inquiry"
    label: str      # e.g. "Inquiry"
    is_active: bool
    group: str      # "active", "closed", "off_ramp"


STAGES: dict[int, StageDefinition] = {
    1: StageDefinition(1, "1-Inquiry",         "Inquiry",         True,  "active"),
    2: StageDefinition(2, "2-Review Info",     "Review Info",     True,  "active"),
    3: StageDefinition(3, "3-Touring",         "Touring",         True,  "active"),
    4: StageDefinition(4, "4-Proposal",        "Proposal / RFP",  True,  "active"),
    5: StageDefinition(5, "5-LOI Negotiation", "LOI Negotiation", True,  "active"),
    6: StageDefinition(6, "6-Lease Review",    "Lease Review",    True,  "active"),
    7: StageDefinition(7, "7-Complete",        "Complete",        False, "closed"),
    8: StageDefinition(8, "8-On Hold",         "On Hold / Idle",  False, "off_ramp"),
    9: StageDefinition(9, "9-Dead",            "Dead / Removed",  False, "off_ramp"),
}

ACTIVE_STAGE_NUMBERS = [s.numeric for s in STAGES.values() if s.is_active]   # [1,2,3,4,5,6]
ALL_STAGE_KEYS = [s.key for s in STAGES.values()]
DEFAULT_STAGE_KEY = "1-Inquiry"
DEFAULT_STAGE_NUM = 1

# Lookup helpers
STAGE_BY_KEY: dict[str, StageDefinition] = {s.key: s for s in STAGES.values()}
STAGE_BY_NUM: dict[int, StageDefinition] = dict(STAGES)

# Old-to-new migration mapping (used by normalizer and migration script)
OLD_TO_NEW_STAGE_MAP: dict[str, tuple[str, int]] = {
    "1-Legal":    ("6-Lease Review",    6),
    "2-LOI":      ("5-LOI Negotiation", 5),
    "3-Touring":  ("3-Touring",         3),
    "4-Inquiry":  ("1-Inquiry",         1),
    "5-Complete": ("7-Complete",        7),
    "6-Idle":     ("8-On Hold",         8),
    "7-Dead":     ("9-Dead",            9),
}
