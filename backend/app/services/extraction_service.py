"""Orchestrates file parsing: routes uploaded files to the correct parser(s) and stores results."""

import uuid
import traceback
from datetime import date

import openpyxl
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.report import ActivityReport
from app.models.deal import Deal
from app.models.availability import PropertyAvailability
from app.models.property_metric import PropertyMetric
from app.parsers.base_parser import ParseResult
from app.parsers.excel_deal_parser import ExcelDealParser
from app.parsers.excel_availability_parser import ExcelAvailabilityParser
from app.parsers.excel_building_sheet_parser import ExcelBuildingSheetParser
from app.parsers.excel_leasing_report_parser import ExcelLeasingReportParser
from app.parsers.pdf_deal_parser import PdfDealParser


# Parser instances in priority order
PARSERS = [
    ExcelLeasingReportParser(),
    ExcelBuildingSheetParser(),
    ExcelDealParser(),
    ExcelAvailabilityParser(),
    PdfDealParser(),
]


def process_report(report_id: str):
    """Background task: process an uploaded report file.

    This function runs outside of the request lifecycle,
    so it creates its own database session.
    """
    db = SessionLocal()
    try:
        report = db.query(ActivityReport).filter(ActivityReport.id == report_id).first()
        if not report:
            return

        report.extraction_status = "processing"
        db.commit()

        file_path = report.file_path
        file_type = report.file_type

        # Get sheet names for Excel files
        sheet_names = None
        if file_type in ("xlsx", "xlsm"):
            try:
                wb = openpyxl.load_workbook(file_path, read_only=True)
                sheet_names = wb.sheetnames
                report.sheet_names = sheet_names
                db.commit()
                wb.close()
            except Exception:
                pass

        # Try each parser
        combined_result = ParseResult()
        errors = []
        parsed = False

        for parser in PARSERS:
            try:
                if parser.can_parse(file_path, file_type, sheet_names):
                    result = parser.parse(file_path)
                    # Merge results
                    combined_result.deals.extend(result.deals)
                    combined_result.availabilities.extend(result.availabilities)
                    if result.metrics:
                        combined_result.metrics.update(result.metrics)
                    combined_result.raw_data.update(result.raw_data)
                    combined_result.warnings.extend(result.warnings)
                    if result.sheet_names:
                        combined_result.sheet_names = result.sheet_names
                    parsed = True
            except Exception as e:
                errors.append(f"{parser.__class__.__name__}: {str(e)}")
                traceback.print_exc()

        if not parsed and not combined_result.deals and not combined_result.availabilities:
            report.extraction_status = "failed"
            report.extraction_errors = errors or ["No compatible parser found for this file format"]
            db.commit()
            return

        # Store raw extraction data
        report.raw_extraction = {
            "deals_count": len(combined_result.deals),
            "availabilities_count": len(combined_result.availabilities),
            "metrics": combined_result.metrics,
            "warnings": combined_result.warnings,
            "raw": combined_result.raw_data,
        }

        snapshot_date = report.report_date or date.today()

        # Store deals
        for deal_data in combined_result.deals:
            # Convert date objects to proper format for SQLAlchemy
            initial_inquiry = deal_data.get("initial_inquiry")
            last_updated = deal_data.get("last_updated")

            deal = Deal(
                property_id=report.property_id,
                report_id=report.id,
                stage=deal_data.get("stage", "4-Inquiry"),
                stage_numeric=deal_data.get("stage_numeric"),
                deal_type=deal_data.get("deal_type"),
                tenant_name=deal_data.get("tenant_name"),
                tenant_industry=deal_data.get("tenant_industry"),
                is_undisclosed=deal_data.get("is_undisclosed", False),
                broker_name=deal_data.get("broker_name"),
                broker_firm=deal_data.get("broker_firm"),
                broker_phone=deal_data.get("broker_phone"),
                broker_email=deal_data.get("broker_email"),
                initial_inquiry=initial_inquiry if isinstance(initial_inquiry, date) else None,
                size_min_sf=deal_data.get("size_min_sf"),
                size_max_sf=deal_data.get("size_max_sf"),
                size_raw=deal_data.get("size_raw"),
                commencement=deal_data.get("commencement"),
                transaction_type=deal_data.get("transaction_type"),
                comments=deal_data.get("comments"),
                last_updated=last_updated if isinstance(last_updated, date) else None,
                last_updated_by=deal_data.get("last_updated_by"),
                lead_contact=deal_data.get("lead_contact"),
                building_id=deal_data.get("building_id"),
                snapshot_date=snapshot_date,
            )
            db.add(deal)

        # Store availabilities
        for avail_data in combined_result.availabilities:
            avail = PropertyAvailability(
                property_id=report.property_id,
                report_id=report.id,
                building=avail_data.get("building"),
                total_size_sf=avail_data.get("total_size_sf"),
                status=avail_data.get("status"),
                office_sf=avail_data.get("office_sf"),
                lease_rate_psf=avail_data.get("lease_rate_psf"),
                opex=avail_data.get("opex"),
                sale_price_psf=avail_data.get("sale_price_psf"),
                power_amps=avail_data.get("power_amps"),
                loading_doors=avail_data.get("loading_doors"),
                eave_height=avail_data.get("eave_height"),
                crane_ready=avail_data.get("crane_ready"),
                land_acreage=avail_data.get("land_acreage"),
                additional_info=avail_data.get("additional_info"),
                snapshot_date=snapshot_date,
            )
            db.add(avail)

        # Store metrics
        if combined_result.metrics:
            metric = PropertyMetric(
                property_id=report.property_id,
                report_id=report.id,
                report_date=snapshot_date,
                total_property_sf=combined_result.metrics.get("total_property_sf"),
                vacant_sf=combined_result.metrics.get("vacant_sf"),
                vacancy_pct=combined_result.metrics.get("vacancy_pct"),
                occupancy_pct=combined_result.metrics.get("occupancy_pct"),
                shadow_vacancy_sf=combined_result.metrics.get("shadow_vacancy_sf"),
                inquiries_sent=combined_result.metrics.get("inquiries_sent"),
                tours_conducted=combined_result.metrics.get("tours_conducted"),
                proposals_sent=combined_result.metrics.get("proposals_sent"),
                quoted_rate_psf=combined_result.metrics.get("quoted_rate_psf"),
                additional_metrics={k: v for k, v in combined_result.metrics.items()
                                    if k not in ("total_property_sf", "vacant_sf", "vacancy_pct",
                                                  "occupancy_pct", "shadow_vacancy_sf", "inquiries_sent",
                                                  "tours_conducted", "proposals_sent", "quoted_rate_psf")},
                snapshot_date=snapshot_date,
            )
            db.add(metric)

        report.extraction_status = "completed"
        if errors:
            report.extraction_errors = errors

        db.commit()

    except Exception as e:
        traceback.print_exc()
        try:
            report = db.query(ActivityReport).filter(ActivityReport.id == report_id).first()
            if report:
                report.extraction_status = "failed"
                report.extraction_errors = [str(e)]
                db.commit()
        except Exception:
            pass
    finally:
        db.close()
