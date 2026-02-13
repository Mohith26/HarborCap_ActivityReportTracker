"""Maps varied column names from different brokerages/reports to canonical field names."""

from difflib import SequenceMatcher

# Known column name variations mapped to canonical field names
COLUMN_ALIASES: dict[str, list[str]] = {
    "stage": [
        "STAGE", "Stage", "Deal Stage", "STATUS",
    ],
    "deal_type": [
        "DEAL TYPE", "Deal Type", "Type", "DEAL\nTYPE",
    ],
    "initial_inquiry": [
        "INITIAL INQUIRY", "Initial Inquiry", "Inquiry Date", "Date",
        "INITIAL\nINQUIRY", "Initial\nInquiry",
    ],
    "tenant_name": [
        "TENANT / INDUSTRY", "TENANT / INDUSTRY / BUYER",
        "Tenant / Industry", "Tenant / Industry / Buyer",
        "TENANT /\nINDUSTRY", "Proposed Tenant Name:",
        "Tenant Name:", "Prospect (Broker)", "Prospect\n(Broker)",
        "TENANT / INDUSTRY\n/ BUYER", "TENANT /INDUSTRY",
    ],
    "broker_contact": [
        "TENANT / BROKER CONTACT", "Tenant / Broker Contact",
        "TENANT / BROKER\nCONTACT", "CoBroker", "Broker",
        "TENANT /\nBROKER CONTACT", "Broker Contact",
    ],
    "size": [
        "SIZE", "Size", "SF", "Need", "SF Needed", "Sq Ft",
        "Square Footage", "SF Range",
    ],
    "commencement": [
        "COMMENCEMENT", "Commencement", "Timing", "Move-In",
        "Target Date",
    ],
    "transaction_type": [
        "PURCHASE OR LEASE", "Purchase or Lease",
        "PURCHASE OR\nLEASE", "Transaction Type",
        "PURCHASE\nOR LEASE",
    ],
    "comments": [
        "COMMENTS", "Comments", "COMMENTS ----- Other Information",
        "Feedback / Comments", "Notes", "COMMENT",
    ],
    "last_updated": [
        "Last Updated", "LAST UPDATED", "Updated",
    ],
    "last_updated_by": [
        "Last Updated By", "LAST UPDATED BY", "Updated By",
    ],
    "lead_contact": [
        "Lead Contact", "LEAD CONTACT", "Lead",
    ],
    "building": [
        "Building", "Building #", "Bldg", "BUILDING",
    ],
    "agreed_price": [
        "Agreed to Price", "Price", "AGREED TO PRICE",
    ],
}

# Availability sheet column aliases
AVAILABILITY_ALIASES: dict[str, list[str]] = {
    "building": [
        "Building", "BUILDING", "Bldg", "Building #", "Unit",
    ],
    "total_size_sf": [
        "Total Size (SF)", "Total Size", "Total SF", "Size (SF)", "SF",
        "Total Size\n(SF)",
    ],
    "status": [
        "Status", "STATUS", "Lease Status",
    ],
    "office_sf": [
        "Office (SF)", "Office", "Office SF", "Office\n(SF)",
    ],
    "lease_rate_psf": [
        "Lease Rate PSF", "Lease Rate", "Rate PSF", "Rate/SF",
        "Lease Rate\nPSF",
    ],
    "opex": [
        "OPEX", "Opex", "Op Ex", "Operating Expenses",
    ],
    "sale_price_psf": [
        "Sale Price PSF", "Sale Price", "Price PSF",
        "Sale Price\nPSF",
    ],
    "power_amps": [
        "Power (Amps)", "Power", "Amps", "Electrical",
        "Power\n(Amps)",
    ],
    "loading_doors": [
        "Loading Doors", "Loading", "Dock Doors", "Doors",
    ],
    "eave_height": [
        "Eave Height", "Clear Height", "Height", "Eave Ht",
    ],
    "crane_ready": [
        "Crane Ready", "Crane", "Crane Cap",
    ],
    "land_acreage": [
        "Land (Acreage)", "Land", "Acreage", "Land Acreage",
        "Land\n(Acreage)",
    ],
    "additional_info": [
        "Additional Info", "Additional Information", "Notes", "Info",
    ],
}


def _clean(s: str) -> str:
    """Normalize whitespace and case for comparison."""
    return " ".join(s.split()).strip()


def _fuzzy_match(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def map_columns(header_row: list[str | None], aliases: dict[str, list[str]] | None = None) -> dict[str, int]:
    """Map actual column names to canonical field names.

    Returns a dict of {canonical_name: column_index}.
    """
    if aliases is None:
        aliases = COLUMN_ALIASES

    mapping: dict[str, int] = {}
    cleaned_headers = [_clean(str(h)) if h else "" for h in header_row]

    for canonical, alias_list in aliases.items():
        best_score = 0.0
        best_idx = -1
        for idx, header in enumerate(cleaned_headers):
            if not header:
                continue
            for alias in alias_list:
                cleaned_alias = _clean(alias)
                # Exact match (case-insensitive)
                if header.lower() == cleaned_alias.lower():
                    best_score = 1.0
                    best_idx = idx
                    break
                # Fuzzy match
                score = _fuzzy_match(header, cleaned_alias)
                if score > best_score and score > 0.80:
                    best_score = score
                    best_idx = idx
            if best_score == 1.0:
                break

        if best_idx >= 0:
            mapping[canonical] = best_idx

    return mapping
