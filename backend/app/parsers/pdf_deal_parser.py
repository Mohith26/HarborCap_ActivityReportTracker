"""Parser for PDF activity reports and deal sheets."""

import re
import pdfplumber
from app.parsers.base_parser import BaseParser, ParseResult
from app.parsers.column_mapper import map_columns, COLUMN_ALIASES
from app.parsers.normalizer import (
    parse_sf_range, parse_stage, parse_broker_contact,
    parse_date_flexible, parse_transaction_type, is_undisclosed_tenant,
)


class PdfDealParser(BaseParser):
    """Parses PDF files containing deal tracking tables."""

    def can_parse(self, file_path: str, file_type: str, sheet_names: list[str] | None = None) -> bool:
        return file_type == "pdf"

    def parse(self, file_path: str) -> ParseResult:
        result = ParseResult()

        with pdfplumber.open(file_path) as pdf:
            # Determine format: check first page for prospect report vs deal sheet
            first_page_text = pdf.pages[0].extract_text() or ""
            is_prospect_report = "PROSPECT REPORT" in first_page_text.upper() or "PROB." in first_page_text.upper()

            if is_prospect_report:
                result = self._parse_prospect_report(pdf)
            else:
                result = self._parse_deal_sheet(pdf)

        return result

    def _parse_deal_sheet(self, pdf) -> ParseResult:
        """Parse standard deal sheet PDF (Discovery Hills, Twinwood style)."""
        result = ParseResult()
        all_tables = []

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    all_tables.append(table)

        if not all_tables:
            result.warnings.append("No tables found in PDF")
            return result

        # Process each table
        for table in all_tables:
            # First row should be headers
            header = [str(cell).strip() if cell else "" for cell in table[0]]
            mapping = map_columns(header, COLUMN_ALIASES)

            if "stage" not in mapping and "tenant_name" not in mapping:
                # Try second row as header (some PDFs have a title row first)
                if len(table) > 2:
                    header = [str(cell).strip() if cell else "" for cell in table[1]]
                    mapping = map_columns(header, COLUMN_ALIASES)
                    start_row = 2
                else:
                    continue
            else:
                start_row = 1

            for row_idx in range(start_row, len(table)):
                row = table[row_idx]
                if not row or all(not cell or str(cell).strip() == "" for cell in row):
                    continue

                deal = self._parse_deal_row(row, mapping)
                if deal and deal.get("tenant_name"):
                    result.deals.append(deal)

        result.raw_data["format"] = "deal_sheet"
        result.raw_data["total_deals"] = len(result.deals)
        return result

    def _parse_prospect_report(self, pdf) -> ParseResult:
        """Parse Aguila Azteca style prospect report PDF."""
        result = ParseResult()
        current_section = "Primary Deals"

        for page in pdf.pages:
            tables = page.extract_tables()
            text = page.extract_text() or ""

            # Check for section markers
            if "ON HOLD" in text.upper():
                current_section = "On Hold"
            elif "REMOVED" in text.upper() or "DEAD" in text.upper():
                current_section = "Removed / Dead"

            for table in tables:
                if not table or len(table) < 2:
                    continue

                header = [str(cell).strip() if cell else "" for cell in table[0]]
                header_text = " ".join(header).upper()

                # Detect prospect report columns
                has_prospect = any("PROSPECT" in h.upper() for h in header if h)
                has_prob = any("PROB" in h.upper() for h in header if h)

                if has_prospect or has_prob:
                    for row_idx in range(1, len(table)):
                        row = table[row_idx]
                        if not row or all(not cell or str(cell).strip() == "" for cell in row):
                            continue

                        deal = self._parse_prospect_row(row, header, current_section)
                        if deal and deal.get("tenant_name"):
                            result.deals.append(deal)
                else:
                    # Try standard deal sheet parsing
                    mapping = map_columns(header, COLUMN_ALIASES)
                    if "stage" in mapping or "tenant_name" in mapping:
                        for row_idx in range(1, len(table)):
                            row = table[row_idx]
                            if not row or all(not cell or str(cell).strip() == "" for cell in row):
                                continue
                            deal = self._parse_deal_row(row, mapping)
                            if deal and deal.get("tenant_name"):
                                deal["deal_section"] = current_section
                                result.deals.append(deal)

        result.raw_data["format"] = "prospect_report"
        result.raw_data["total_deals"] = len(result.deals)
        return result

    def _parse_deal_row(self, row: list, mapping: dict[str, int]) -> dict | None:
        """Parse a standard deal row from a PDF table."""

        def get(field: str) -> str | None:
            idx = mapping.get(field)
            if idx is None or idx >= len(row):
                return None
            val = row[idx]
            return str(val).strip() if val else None

        tenant_raw = get("tenant_name")
        if not tenant_raw:
            return None

        stage_raw = get("stage")
        stage, stage_numeric = parse_stage(stage_raw)
        size_min, size_max = parse_sf_range(get("size"))
        broker_info = parse_broker_contact(get("broker_contact"))

        initial_inquiry_raw = get("initial_inquiry")
        initial_inquiry = parse_date_flexible(initial_inquiry_raw)

        return {
            "stage": stage,
            "stage_numeric": stage_numeric,
            "deal_type": get("deal_type"),
            "tenant_name": tenant_raw,
            "tenant_industry": None,
            "is_undisclosed": is_undisclosed_tenant(tenant_raw),
            "broker_name": broker_info["name"],
            "broker_firm": broker_info["firm"],
            "broker_phone": broker_info["phone"],
            "broker_email": broker_info["email"],
            "initial_inquiry": initial_inquiry,
            "size_min_sf": size_min,
            "size_max_sf": size_max,
            "size_raw": get("size"),
            "commencement": get("commencement"),
            "transaction_type": parse_transaction_type(get("transaction_type")),
            "comments": get("comments"),
            "last_updated": None,
            "last_updated_by": None,
            "lead_contact": None,
            "building_id": None,
        }

    def _parse_prospect_row(self, row: list, header: list, section: str) -> dict | None:
        """Parse a prospect report row (Aguila Azteca style)."""
        if len(row) < 2:
            return None

        # Map columns by position
        col_map = {}
        for i, h in enumerate(header):
            if not h:
                continue
            h_upper = h.upper()
            if "PROSPECT" in h_upper or "BROKER" in h_upper:
                col_map["prospect"] = i
            elif "NEED" in h_upper:
                col_map["need"] = i
            elif "PROB" in h_upper:
                col_map["prob"] = i
            elif "STATUS" in h_upper or "REVIEW" in h_upper:
                col_map["status"] = i
            elif "COMMENT" in h_upper or "UPDATE" in h_upper:
                col_map["comments"] = i

        prospect_raw = row[col_map["prospect"]] if col_map.get("prospect") is not None and col_map["prospect"] < len(row) else None
        if not prospect_raw or not str(prospect_raw).strip():
            return None

        prospect_str = str(prospect_raw).strip()
        # Prospect field often contains "Company Name (Broker Name)"
        broker_match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', prospect_str)
        if broker_match:
            tenant_name = broker_match.group(1).strip()
            broker_name = broker_match.group(2).strip()
        else:
            tenant_name = prospect_str
            broker_name = None

        need_raw = row[col_map["need"]] if col_map.get("need") is not None and col_map["need"] < len(row) else None
        size_min, size_max = parse_sf_range(str(need_raw) if need_raw else None)

        prob_raw = row[col_map["prob"]] if col_map.get("prob") is not None and col_map["prob"] < len(row) else None
        probability = None
        if prob_raw:
            try:
                probability = float(str(prob_raw).strip())
            except ValueError:
                pass

        comments_raw = row[col_map["comments"]] if col_map.get("comments") is not None and col_map["comments"] < len(row) else None
        comments = str(comments_raw).strip() if comments_raw else None

        # Map section to stage
        stage_map = {
            "Primary Deals": ("1-Inquiry", 1),
            "Secondary Deals": ("8-On Hold", 8),
            "On Hold": ("8-On Hold", 8),
            "Removed / Dead": ("9-Dead", 9),
        }
        stage, stage_numeric = stage_map.get(section, ("1-Inquiry", 1))

        # Extract probability score
        prob_score = None
        if probability is not None and 1 <= probability <= 5:
            prob_score = int(probability)

        # Set deal priority based on section
        deal_priority = None
        if section == "Primary Deals":
            deal_priority = "Primary"
        elif section == "Secondary Deals":
            deal_priority = "Secondary"

        return {
            "stage": stage,
            "stage_numeric": stage_numeric,
            "deal_type": "New Deal",
            "tenant_name": tenant_name,
            "tenant_industry": None,
            "is_undisclosed": is_undisclosed_tenant(tenant_name),
            "broker_name": broker_name,
            "broker_firm": None,
            "broker_phone": None,
            "broker_email": None,
            "initial_inquiry": None,
            "size_min_sf": size_min,
            "size_max_sf": size_max,
            "size_raw": str(need_raw).strip() if need_raw else None,
            "commencement": None,
            "transaction_type": "Lease",
            "comments": comments,
            "last_updated": None,
            "last_updated_by": None,
            "lead_contact": None,
            "building_id": None,
            "deal_section": section,
            "probability_score": prob_score,
            "deal_priority": deal_priority,
        }
