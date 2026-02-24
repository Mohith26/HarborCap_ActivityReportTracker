"""Normalizes messy real-world data from activity reports into clean typed values."""

import re
from datetime import date, datetime


def parse_sf_range(raw: str | None) -> tuple[int | None, int | None]:
    """Parse square footage ranges from various formats.

    Examples:
        '30,000 - 50,000 SF' -> (30000, 50000)
        '6k SF' -> (6000, 6000)
        '21,000' -> (21000, 21000)
        '10-15K' -> (10000, 15000)
        '6k sf' -> (6000, 6000)
        'Trailer parking' -> (None, None)
        '+/- 10,000 SF' -> (10000, 10000)
        '50,000+' -> (50000, 50000)
    """
    if not raw:
        return None, None

    raw = str(raw).strip()
    if not raw or raw.lower() in ("n/a", "tbd", "-", "none", ""):
        return None, None

    # Remove common prefixes/suffixes
    raw = raw.replace("+/-", "").replace("±", "").strip()

    # Try range with K notation: "10-15K"
    match = re.match(r'(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*[kK]', raw)
    if match:
        return int(float(match.group(1)) * 1000), int(float(match.group(2)) * 1000)

    # Try range with full numbers: "30,000 - 50,000"
    match = re.match(r'(\d[\d,]*)\s*[-–to]+\s*(\d[\d,]*)', raw)
    if match:
        min_sf = int(match.group(1).replace(",", ""))
        max_sf = int(match.group(2).replace(",", ""))
        return min_sf, max_sf

    # Single K notation: "6k"
    match = re.match(r'(\d+(?:\.\d+)?)\s*[kK]', raw)
    if match:
        val = int(float(match.group(1)) * 1000)
        return val, val

    # Single number with commas: "21,000"
    match = re.match(r'(\d[\d,]+)', raw)
    if match:
        val = int(match.group(1).replace(",", ""))
        if val > 100:  # Likely SF, not a random small number
            return val, val

    return None, None


def parse_stage(raw: str | None) -> tuple[str, int | None]:
    """Parse deal stage string into (stage_key, stage_numeric).

    Handles new-format ("1-Inquiry", "5-LOI Negotiation"), old-format
    ("1-Legal", "4-Inquiry"), and bare names ("Touring", "LOI", "Legal").

    Examples:
        '1-Inquiry' -> ('1-Inquiry', 1)
        '5-LOI Negotiation' -> ('5-LOI Negotiation', 5)
        '2-LOI' (old) -> ('5-LOI Negotiation', 5)
        'LOI' -> ('5-LOI Negotiation', 5)
        'Touring' -> ('3-Touring', 3)
        None -> ('1-Inquiry', 1)
    """
    from app.stages import (
        STAGES, STAGE_BY_KEY, OLD_TO_NEW_STAGE_MAP,
        DEFAULT_STAGE_KEY, DEFAULT_STAGE_NUM,
    )

    if not raw:
        return DEFAULT_STAGE_KEY, DEFAULT_STAGE_NUM

    raw = str(raw).strip()

    # Exact match against new stage keys (case-insensitive)
    for stage in STAGES.values():
        if raw.lower() == stage.key.lower():
            return stage.key, stage.numeric

    # Match old-format keys and remap
    if raw in OLD_TO_NEW_STAGE_MAP:
        return OLD_TO_NEW_STAGE_MAP[raw]

    # Try numeric prefix: "3-Touring" -> extract 3
    match = re.match(r'(\d+)\s*[-–]?\s*(.*)', raw)
    if match:
        num = int(match.group(1))
        if num in STAGES:
            return STAGES[num].key, num

    # Fuzzy keyword matching (bare names)
    _KEYWORD_MAP = {
        "inquiry": (1, "1-Inquiry"),
        "review": (2, "2-Review Info"),
        "reviewing": (2, "2-Review Info"),
        "sent details": (2, "2-Review Info"),
        "tour": (3, "3-Touring"),
        "touring": (3, "3-Touring"),
        "proposal": (4, "4-Proposal"),
        "rfp": (4, "4-Proposal"),
        "loi": (5, "5-LOI Negotiation"),
        "letter of intent": (5, "5-LOI Negotiation"),
        "legal": (6, "6-Lease Review"),
        "lease review": (6, "6-Lease Review"),
        "lease draft": (6, "6-Lease Review"),
        "complete": (7, "7-Complete"),
        "executed": (7, "7-Complete"),
        "signed": (7, "7-Complete"),
        "idle": (8, "8-On Hold"),
        "on hold": (8, "8-On Hold"),
        "hold": (8, "8-On Hold"),
        "paused": (8, "8-On Hold"),
        "inactive": (8, "8-On Hold"),
        "dead": (9, "9-Dead"),
        "removed": (9, "9-Dead"),
        "lost": (9, "9-Dead"),
        "cancelled": (9, "9-Dead"),
    }
    raw_lower = raw.lower()
    for keyword, (num, key) in _KEYWORD_MAP.items():
        if keyword in raw_lower:
            return key, num

    return raw, None


def parse_broker_contact(raw: str | None) -> dict[str, str | None]:
    """Parse multi-line broker contact info.

    Examples:
        'Preston Yaggi\\n281-744-5326\\npyaggi@lee-associates.com'
        -> {name: 'Preston Yaggi', phone: '281-744-5326', email: 'pyaggi@lee-associates.com', firm: 'Lee & Associates'}
    """
    result: dict[str, str | None] = {"name": None, "phone": None, "email": None, "firm": None}

    if not raw:
        return result

    raw = str(raw).strip()
    lines = [line.strip() for line in raw.replace("\r\n", "\n").split("\n") if line.strip()]

    for line in lines:
        # Check for email
        if "@" in line and "." in line:
            result["email"] = line
            # Try to extract firm from email domain
            match = re.search(r'@([\w.-]+)', line)
            if match:
                domain = match.group(1).split(".")[0]
                result["firm"] = _domain_to_firm(domain)
            continue

        # Check for phone number
        if re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line):
            result["phone"] = line
            continue

        # Check for firm name (common brokerage firms)
        lower = line.lower()
        if any(firm in lower for firm in ["lee & associates", "jll", "cbre", "cushman", "colliers", "marcus", "newmark", "kidder", "nai"]):
            result["firm"] = line
            continue

        # Otherwise, treat as name (first non-phone, non-email line)
        if not result["name"]:
            result["name"] = line
        elif not result["firm"]:
            result["firm"] = line

    return result


def _domain_to_firm(domain: str) -> str | None:
    """Map email domain to broker firm name."""
    domain_map = {
        "lee-associates": "Lee & Associates",
        "jll": "JLL",
        "cbre": "CBRE",
        "cushwake": "Cushman & Wakefield",
        "colliers": "Colliers",
        "marcusmillichap": "Marcus & Millichap",
        "nmrk": "Newmark",
        "kidder": "Kidder Mathews",
        "naihsr": "NAI",
        "naipartners": "NAI Partners",
        "streamrealty": "Stream Realty",
        "dfrproperties": "DFR Properties",
    }
    for key, firm in domain_map.items():
        if key in domain.lower():
            return firm
    return None


def parse_date_flexible(raw) -> date | None:
    """Handle various date formats including Excel serial dates.

    Examples:
        45678 (Excel serial) -> date(2025, 1, 15) approximately
        '1/15/2026' -> date(2026, 1, 15)
        '2025-03-01' -> date(2025, 3, 1)
        datetime object -> .date()
    """
    if raw is None:
        return None

    # Already a date
    if isinstance(raw, date):
        return raw

    # datetime object
    if isinstance(raw, datetime):
        return raw.date()

    # Excel serial number (integer or float)
    if isinstance(raw, (int, float)):
        try:
            # Excel serial date: days since 1899-12-30
            serial = int(raw)
            if 30000 < serial < 60000:  # Reasonable range for 1982-2063
                from datetime import timedelta
                base = date(1899, 12, 30)
                return base + timedelta(days=serial)
        except (ValueError, OverflowError):
            pass
        return None

    raw = str(raw).strip()
    if not raw or raw.lower() in ("n/a", "tbd", "-", "none", ""):
        return None

    # Try common formats
    formats = [
        "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y", "%m-%d-%y",
        "%Y-%m-%d", "%m.%d.%Y", "%m.%d.%y",
        "%d/%m/%Y", "%d-%m-%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue

    return None


def parse_transaction_type(raw: str | None) -> str | None:
    """Normalize transaction type."""
    if not raw:
        return None
    raw = str(raw).strip().lower()
    if "lease" in raw and "purchase" in raw:
        return "Both"
    if "lease" in raw:
        return "Lease"
    if "purchase" in raw or "sale" in raw or "buy" in raw:
        return "Purchase"
    return raw.title() if raw else None


def is_undisclosed_tenant(name: str | None) -> bool:
    """Check if tenant name is undisclosed/anonymous."""
    if not name:
        return False
    lower = name.lower().strip()
    return any(term in lower for term in ["undisclosed", "confidential", "tbd", "unknown", "anonymous"])
