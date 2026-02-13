"""AI insight generation using OpenAI API."""

import json
from datetime import date

from openai import OpenAI
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.deal import Deal
from app.models.report import ActivityReport
from app.models.property import Property
from app.models.property_metric import PropertyMetric
from app.models.insight import AIInsight


class InsightService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    def generate_property_insights(
        self, property_id: str, insight_types: list[str] | None = None
    ) -> list[AIInsight]:
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        prop = self.db.query(Property).filter(Property.id == property_id).first()
        if not prop:
            raise ValueError("Property not found")

        # Get all completed reports for this property
        reports = (
            self.db.query(ActivityReport)
            .filter(ActivityReport.property_id == property_id, ActivityReport.extraction_status == "completed")
            .order_by(ActivityReport.report_date)
            .all()
        )
        if not reports:
            raise ValueError("No completed reports found for this property")

        has_multiple_snapshots = len(reports) > 1

        # Determine which insight types to generate
        all_types = ["pipeline_health", "dead_deal_analysis"]
        if has_multiple_snapshots:
            all_types.extend(["deal_velocity", "conversion_rate", "market_trend"])

        types_to_generate = insight_types or all_types

        generated = []
        for insight_type in types_to_generate:
            if insight_type == "deal_velocity" and not has_multiple_snapshots:
                continue
            if insight_type == "conversion_rate" and not has_multiple_snapshots:
                continue
            if insight_type == "market_trend" and not has_multiple_snapshots:
                continue

            try:
                insight = self._generate_insight(prop, reports, insight_type)
                if insight:
                    self.db.add(insight)
                    generated.append(insight)
            except Exception as e:
                print(f"Error generating {insight_type} insight: {e}")

        self.db.commit()
        for i in generated:
            self.db.refresh(i)
        return generated

    def _generate_insight(
        self, prop: Property, reports: list[ActivityReport], insight_type: str
    ) -> AIInsight | None:
        latest_report = reports[-1]

        # Gather data context
        if insight_type == "pipeline_health":
            data_context = self._build_pipeline_context(prop, latest_report)
            system_prompt = "You are a commercial real estate analyst. Analyze deal pipeline data and provide actionable insights."
            user_prompt = self._pipeline_health_prompt(prop, data_context)

        elif insight_type == "dead_deal_analysis":
            data_context = self._build_dead_deal_context(prop, latest_report)
            if not data_context.get("dead_deals"):
                return None
            system_prompt = "You are a commercial real estate analyst. Analyze failed deals and identify patterns."
            user_prompt = self._dead_deal_prompt(prop, data_context)

        elif insight_type == "deal_velocity":
            data_context = self._build_velocity_context(prop, reports)
            system_prompt = "You are a commercial real estate analyst. Analyze deal progression speed and identify bottlenecks."
            user_prompt = self._deal_velocity_prompt(prop, data_context)

        elif insight_type == "conversion_rate":
            data_context = self._build_conversion_context(prop, reports)
            system_prompt = "You are a commercial real estate analyst. Analyze pipeline conversion rates."
            user_prompt = self._conversion_rate_prompt(prop, data_context)

        elif insight_type == "market_trend":
            data_context = self._build_market_context(prop, reports)
            system_prompt = "You are a commercial real estate analyst. Identify market trends from leasing activity."
            user_prompt = self._market_trend_prompt(prop, data_context)

        else:
            return None

        # Call OpenAI
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )

        content = response.choices[0].message.content
        title = self._generate_title(insight_type, prop.name)

        insight = AIInsight(
            property_id=prop.id,
            insight_type=insight_type,
            title=title,
            content=content,
            data_context=data_context,
            model_used=settings.OPENAI_MODEL,
            date_range_start=reports[0].report_date,
            date_range_end=reports[-1].report_date,
        )
        insight.set_report_ids([r.id for r in reports])
        return insight

    def _build_pipeline_context(self, prop: Property, report: ActivityReport) -> dict:
        deals = self.db.query(Deal).filter(Deal.report_id == report.id).all()
        stage_counts = {}
        for deal in deals:
            stage = deal.stage or "Unknown"
            if stage not in stage_counts:
                stage_counts[stage] = {"count": 0, "total_sf": 0}
            stage_counts[stage]["count"] += 1
            if deal.size_min_sf:
                stage_counts[stage]["total_sf"] += deal.size_min_sf

        return {
            "property_name": prop.name,
            "total_deals": len(deals),
            "stage_breakdown": stage_counts,
            "deals_summary": [
                {
                    "tenant": d.tenant_name,
                    "stage": d.stage,
                    "size": d.size_raw,
                    "type": d.transaction_type,
                    "commencement": d.commencement,
                }
                for d in deals[:30]  # Limit to 30 for token management
            ],
        }

    def _build_dead_deal_context(self, prop: Property, report: ActivityReport) -> dict:
        dead_deals = (
            self.db.query(Deal)
            .filter(Deal.report_id == report.id, Deal.stage_numeric == 7)
            .all()
        )
        return {
            "property_name": prop.name,
            "dead_deals": [
                {
                    "tenant": d.tenant_name,
                    "size": d.size_raw,
                    "comments": d.comments[:500] if d.comments else None,
                    "type": d.transaction_type,
                }
                for d in dead_deals
            ],
        }

    def _build_velocity_context(self, prop: Property, reports: list[ActivityReport]) -> dict:
        snapshots = []
        for report in reports[-5:]:  # Last 5 snapshots
            deals = self.db.query(Deal).filter(Deal.report_id == report.id).all()
            snapshots.append({
                "date": str(report.report_date),
                "deals": {
                    d.tenant_name: d.stage
                    for d in deals if d.tenant_name
                },
            })
        return {"property_name": prop.name, "snapshots": snapshots}

    def _build_conversion_context(self, prop: Property, reports: list[ActivityReport]) -> dict:
        first_report = reports[0]
        last_report = reports[-1]

        first_deals = {d.tenant_name: d.stage_numeric for d in
                       self.db.query(Deal).filter(Deal.report_id == first_report.id).all() if d.tenant_name}
        last_deals = {d.tenant_name: d.stage_numeric for d in
                      self.db.query(Deal).filter(Deal.report_id == last_report.id).all() if d.tenant_name}

        return {
            "property_name": prop.name,
            "first_snapshot_date": str(first_report.report_date),
            "last_snapshot_date": str(last_report.report_date),
            "first_deals": first_deals,
            "last_deals": last_deals,
        }

    def _build_market_context(self, prop: Property, reports: list[ActivityReport]) -> dict:
        all_deals = (
            self.db.query(Deal)
            .filter(Deal.property_id == prop.id)
            .order_by(Deal.snapshot_date)
            .all()
        )
        return {
            "property_name": prop.name,
            "total_inquiries": len(all_deals),
            "size_distribution": [d.size_raw for d in all_deals if d.size_raw],
            "transaction_types": [d.transaction_type for d in all_deals if d.transaction_type],
            "industries": [d.tenant_industry for d in all_deals if d.tenant_industry],
        }

    def _pipeline_health_prompt(self, prop: Property, context: dict) -> str:
        return f"""Analyze the deal pipeline for {prop.name}:

Total active deals: {context['total_deals']}
Stage breakdown: {json.dumps(context['stage_breakdown'], indent=2)}

Recent deals (sample):
{json.dumps(context['deals_summary'][:15], indent=2)}

Provide:
1. Pipeline health assessment (is it healthy, concerning, or strong?)
2. Stage distribution analysis (any bottlenecks or gaps?)
3. Key observations about the types and sizes of deals
4. 2-3 specific recommendations for improving pipeline performance

Keep the response concise and actionable. Use markdown formatting."""

    def _dead_deal_prompt(self, prop: Property, context: dict) -> str:
        return f"""Analyze the dead/failed deals for {prop.name}:

Total dead deals: {len(context['dead_deals'])}

Dead deal details:
{json.dumps(context['dead_deals'][:20], indent=2)}

Provide:
1. Common reasons deals are failing (categorize them)
2. Patterns in the types of tenants or deal sizes that fail
3. 2-3 actionable recommendations to reduce deal mortality

Keep the response concise. Use markdown formatting."""

    def _deal_velocity_prompt(self, prop: Property, context: dict) -> str:
        return f"""Analyze deal velocity for {prop.name} across multiple report snapshots:

{json.dumps(context['snapshots'], indent=2)}

Provide:
1. Which deals are progressing through the pipeline?
2. Which deals appear stalled (same stage across snapshots)?
3. Average progression speed observations
4. Recommendations for accelerating stalled deals

Keep the response concise. Use markdown formatting."""

    def _conversion_rate_prompt(self, prop: Property, context: dict) -> str:
        return f"""Analyze conversion rates for {prop.name}:

Period: {context['first_snapshot_date']} to {context['last_snapshot_date']}

First snapshot deal stages: {json.dumps(context['first_deals'], indent=2)}
Latest snapshot deal stages: {json.dumps(context['last_deals'], indent=2)}

Provide:
1. Stage-to-stage conversion rates (Inquiry→Touring, Touring→LOI, LOI→Legal, Legal→Complete)
2. Overall pipeline conversion rate
3. Where the biggest drop-offs occur
4. Recommendations for improving conversion

Keep the response concise. Use markdown formatting."""

    def _market_trend_prompt(self, prop: Property, context: dict) -> str:
        return f"""Analyze market trends from leasing activity for {prop.name}:

Total inquiries over time: {context['total_inquiries']}
Size distribution: {context['size_distribution'][:20]}
Transaction types: {context['transaction_types'][:20]}

Provide:
1. What types of tenants are most interested?
2. What size ranges are most in demand?
3. Lease vs purchase demand trends
4. Overall market demand assessment

Keep the response concise. Use markdown formatting."""

    def _generate_title(self, insight_type: str, property_name: str) -> str:
        titles = {
            "pipeline_health": f"Pipeline Health Analysis - {property_name}",
            "dead_deal_analysis": f"Dead Deal Analysis - {property_name}",
            "deal_velocity": f"Deal Velocity Report - {property_name}",
            "conversion_rate": f"Conversion Rate Analysis - {property_name}",
            "market_trend": f"Market Trend Analysis - {property_name}",
        }
        return titles.get(insight_type, f"{insight_type} - {property_name}")
