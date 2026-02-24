"""Portfolio-level AI insight generation.

Generates unprompted insights across ALL properties and deals.
Called automatically after report extraction completes.
"""

import json
import logging
from datetime import date, datetime, timezone

from openai import OpenAI
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.deal import Deal
from app.models.report import ActivityReport
from app.models.property import Property
from app.models.insight import AIInsight
from app.stages import STAGES, ACTIVE_STAGE_NUMBERS

logger = logging.getLogger(__name__)


class PortfolioInsightService:
    def __init__(self, db: Session):
        self.db = db
        api_key = settings.OPENAI_API_KEY
        if api_key and not api_key.startswith("sk-your-"):
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    def generate_all_portfolio_insights(self) -> list[AIInsight]:
        """Main entry point: generates all unprompted portfolio insights.

        Raises ValueError if OpenAI is not configured.
        """
        if not self.client:
            raise ValueError(
                "OpenAI API key is not configured. "
                "Set OPENAI_API_KEY in backend/.env to enable AI insights."
            )

        insights = []
        generators = [
            ("stale_deals", self._analyze_stale_deals),
            ("stage_bottleneck", self._analyze_stage_bottlenecks),
            ("leasing_momentum", self._analyze_leasing_momentum),
            ("dead_deal_patterns", self._analyze_dead_deal_patterns),
            ("pipeline_velocity", self._analyze_pipeline_velocity),
            ("geographic_trend", self._analyze_geographic_trends),
        ]

        for insight_type, generator in generators:
            try:
                result = generator()
                if result:
                    insights.append(result)
            except Exception as e:
                logger.error(f"Portfolio insight generation failed for {insight_type}: {e}")

        if insights:
            for i in insights:
                self.db.add(i)
            self.db.commit()
            for i in insights:
                self.db.refresh(i)

        return insights

    def _get_latest_deals_by_property(self) -> dict[str, list[Deal]]:
        """Get deals from the latest report for each property."""
        properties = self.db.query(Property).all()
        result = {}
        for prop in properties:
            latest_report = (
                self.db.query(ActivityReport)
                .filter(ActivityReport.property_id == prop.id, ActivityReport.extraction_status == "completed")
                .order_by(ActivityReport.report_date.desc())
                .first()
            )
            if latest_report:
                deals = self.db.query(Deal).filter(Deal.report_id == latest_report.id).all()
                result[prop.name] = deals
        return result

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        return response.choices[0].message.content

    def _create_insight(self, insight_type: str, title: str, content: str,
                        data_context: dict, severity: str = "info",
                        tags: list | None = None) -> AIInsight:
        return AIInsight(
            property_id=None,
            insight_type=insight_type,
            scope="portfolio",
            severity=severity,
            is_auto_generated=True,
            tags=tags,
            title=title,
            content=content,
            data_context=data_context,
            model_used=settings.OPENAI_MODEL,
            date_range_start=date.today(),
            date_range_end=date.today(),
        )

    def _analyze_stale_deals(self) -> AIInsight | None:
        """Find deals stuck in the same stage across multiple properties."""
        deals_by_prop = self._get_latest_deals_by_property()
        all_active = []
        for prop_name, deals in deals_by_prop.items():
            for d in deals:
                if d.stage_numeric and d.stage_numeric in ACTIVE_STAGE_NUMBERS:
                    all_active.append({
                        "property": prop_name,
                        "tenant": d.tenant_name,
                        "stage": d.stage,
                        "size": d.size_raw,
                        "comments": (d.comments or "")[:200],
                    })

        if len(all_active) < 3:
            return None

        context = {"active_deals_count": len(all_active), "sample_deals": all_active[:40]}
        content = self._call_openai(
            "You are a real estate portfolio analyst. Identify deals that appear stale or stuck based on their stage, comments, and context.",
            f"""Review these active deals across the portfolio and identify any that appear stale or stuck.
Look for deals where comments suggest long periods without progress, or deals in early stages with old inquiry dates.

Active deals across portfolio ({len(all_active)} total):
{json.dumps(all_active[:40], indent=2)}

Provide:
1. Which deals appear stale and why
2. Which properties have the most stale deals
3. Recommended actions for each stale deal

Use markdown formatting. Be specific with property and tenant names."""
        )

        return self._create_insight(
            "stale_deals",
            "Stale Deal Alert - Portfolio Overview",
            content, context, severity="warning", tags=["stale_deals"]
        )

    def _analyze_stage_bottlenecks(self) -> AIInsight | None:
        """Find stages where deals pile up disproportionately."""
        deals_by_prop = self._get_latest_deals_by_property()

        stage_totals = {}
        for prop_name, deals in deals_by_prop.items():
            for d in deals:
                stage = d.stage or "Unknown"
                if stage not in stage_totals:
                    stage_totals[stage] = {"count": 0, "properties": set()}
                stage_totals[stage]["count"] += 1
                stage_totals[stage]["properties"].add(prop_name)

        if not stage_totals:
            return None

        # Serialize for context
        stage_summary = {
            k: {"count": v["count"], "properties": list(v["properties"])}
            for k, v in stage_totals.items()
        }

        context = {"stage_summary": stage_summary}
        content = self._call_openai(
            "You are a real estate portfolio analyst. Identify pipeline bottlenecks where deals accumulate.",
            f"""Analyze the deal stage distribution across the entire portfolio.

The expected lease lifecycle is: Inquiry → Review Info → Touring → Proposal/RFP → LOI Negotiation → Lease Review → Complete
Off-ramps: On Hold, Dead/Removed

Current stage distribution across all properties:
{json.dumps(stage_summary, indent=2)}

Provide:
1. Which stages have disproportionately many deals (bottlenecks)?
2. Are deals flowing through the pipeline or getting stuck?
3. Comparison of active pipeline (stages 1-6) vs off-ramps (8-9)
4. Specific recommendations to clear bottlenecks

Use markdown formatting."""
        )

        return self._create_insight(
            "stage_bottleneck",
            "Pipeline Bottleneck Analysis - Portfolio",
            content, context, severity="warning", tags=["bottleneck", "pipeline"]
        )

    def _analyze_leasing_momentum(self) -> AIInsight | None:
        """Assess overall portfolio leasing activity trends."""
        properties = self.db.query(Property).all()
        prop_summaries = []

        for prop in properties:
            reports = (
                self.db.query(ActivityReport)
                .filter(ActivityReport.property_id == prop.id, ActivityReport.extraction_status == "completed")
                .order_by(ActivityReport.report_date.desc())
                .limit(3)
                .all()
            )
            if not reports:
                continue

            latest_deals = self.db.query(Deal).filter(Deal.report_id == reports[0].id).count()
            active_deals = (
                self.db.query(Deal)
                .filter(Deal.report_id == reports[0].id, Deal.stage_numeric.in_(ACTIVE_STAGE_NUMBERS))
                .count()
            )

            prop_summaries.append({
                "property": prop.name,
                "city": prop.city,
                "state": prop.state,
                "total_deals": latest_deals,
                "active_deals": active_deals,
                "report_count": len(reports),
                "latest_report_date": str(reports[0].report_date) if reports[0].report_date else None,
            })

        if not prop_summaries:
            return None

        context = {"property_summaries": prop_summaries}
        content = self._call_openai(
            "You are a real estate portfolio analyst. Assess overall leasing momentum across a portfolio.",
            f"""Assess the leasing momentum across this real estate portfolio.

Property summaries:
{json.dumps(prop_summaries, indent=2)}

Provide:
1. Which properties have the strongest leasing momentum (most active deals)?
2. Which properties appear stagnant?
3. Overall portfolio health assessment
4. Recommendations for underperforming properties

Use markdown formatting. Be specific with property names."""
        )

        severity = "positive" if sum(p["active_deals"] for p in prop_summaries) > 20 else "info"

        return self._create_insight(
            "leasing_momentum",
            "Leasing Momentum Report - Portfolio",
            content, context, severity=severity, tags=["momentum", "activity"]
        )

    def _analyze_dead_deal_patterns(self) -> AIInsight | None:
        """Identify common themes in dead/removed deals across all properties."""
        dead_deals = (
            self.db.query(Deal, Property.name)
            .join(Property, Deal.property_id == Property.id)
            .filter(Deal.stage_numeric == 9)
            .limit(100)
            .all()
        )

        if len(dead_deals) < 5:
            return None

        dead_summary = [
            {
                "property": prop_name,
                "tenant": d.tenant_name,
                "size": d.size_raw,
                "type": d.transaction_type,
                "comments": (d.comments or "")[:300],
            }
            for d, prop_name in dead_deals
        ]

        context = {"dead_deal_count": len(dead_deals), "sample_deals": dead_summary[:50]}
        content = self._call_openai(
            "You are a real estate portfolio analyst. Analyze patterns in failed deals across a portfolio.",
            f"""Analyze dead/removed deals across the entire portfolio to identify common failure patterns.

Total dead deals: {len(dead_deals)}
Sample dead deals:
{json.dumps(dead_summary[:50], indent=2)}

Provide:
1. Common reasons deals fail (categorize into themes)
2. Which properties have the highest deal mortality?
3. Are certain deal sizes or types more likely to fail?
4. Actionable recommendations to reduce deal failure rates

Use markdown formatting. Be specific."""
        )

        return self._create_insight(
            "dead_deal_patterns",
            "Dead Deal Pattern Analysis - Portfolio",
            content, context, severity="warning", tags=["dead_deals", "patterns"]
        )

    def _analyze_pipeline_velocity(self) -> AIInsight | None:
        """Measure deal progression speed across the portfolio."""
        deals_by_prop = self._get_latest_deals_by_property()

        stage_data = {}
        for prop_name, deals in deals_by_prop.items():
            for d in deals:
                if d.stage_numeric and d.stage_numeric in ACTIVE_STAGE_NUMBERS:
                    stage = d.stage
                    if stage not in stage_data:
                        stage_data[stage] = []
                    stage_data[stage].append({
                        "property": prop_name,
                        "tenant": d.tenant_name,
                        "size": d.size_raw,
                    })

        if not stage_data:
            return None

        # Summarize for prompt
        stage_summary = {k: {"count": len(v), "sample": v[:5]} for k, v in stage_data.items()}

        context = {"stage_velocity_data": stage_summary}
        content = self._call_openai(
            "You are a real estate portfolio analyst. Analyze deal pipeline velocity.",
            f"""Analyze the current deal pipeline velocity across the portfolio.

Deals by stage (with samples):
{json.dumps(stage_summary, indent=2)}

The expected lease lifecycle progression is:
1-Inquiry → 2-Review Info → 3-Touring → 4-Proposal/RFP → 5-LOI Negotiation → 6-Lease Review → 7-Complete

Provide:
1. How healthy is the pipeline flow from early to late stages?
2. Are there enough deals in mid-to-late stages (Proposal, LOI, Lease Review)?
3. Which properties have the most advanced deals (closest to completion)?
4. Velocity assessment: is the portfolio converting fast enough?

Use markdown formatting."""
        )

        return self._create_insight(
            "pipeline_velocity",
            "Pipeline Velocity Analysis - Portfolio",
            content, context, severity="info", tags=["velocity", "pipeline"]
        )

    def _analyze_geographic_trends(self) -> AIInsight | None:
        """Analyze trends by city/state across all properties."""
        properties = self.db.query(Property).all()
        geo_data = {}

        for prop in properties:
            key = f"{prop.city or 'Unknown'}, {prop.state or 'Unknown'}"
            if key not in geo_data:
                geo_data[key] = {"properties": [], "total_deals": 0, "active_deals": 0, "dead_deals": 0}

            latest_report = (
                self.db.query(ActivityReport)
                .filter(ActivityReport.property_id == prop.id, ActivityReport.extraction_status == "completed")
                .order_by(ActivityReport.report_date.desc())
                .first()
            )
            if not latest_report:
                continue

            total = self.db.query(Deal).filter(Deal.report_id == latest_report.id).count()
            active = self.db.query(Deal).filter(
                Deal.report_id == latest_report.id,
                Deal.stage_numeric.in_(ACTIVE_STAGE_NUMBERS)
            ).count()
            dead = self.db.query(Deal).filter(
                Deal.report_id == latest_report.id,
                Deal.stage_numeric == 9
            ).count()

            geo_data[key]["properties"].append(prop.name)
            geo_data[key]["total_deals"] += total
            geo_data[key]["active_deals"] += active
            geo_data[key]["dead_deals"] += dead

        if len(geo_data) < 2:
            return None

        context = {"geographic_data": geo_data}
        content = self._call_openai(
            "You are a real estate portfolio analyst. Analyze geographic trends in leasing activity.",
            f"""Analyze leasing activity trends by geographic market across this portfolio.

Geographic breakdown:
{json.dumps(geo_data, indent=2)}

Provide:
1. Which markets are the most active?
2. Which markets have the highest deal mortality (dead deals as % of total)?
3. Are there geographic patterns in pipeline health?
4. Market-specific recommendations

Use markdown formatting."""
        )

        return self._create_insight(
            "geographic_trend",
            "Geographic Market Analysis - Portfolio",
            content, context, severity="info", tags=["geographic", "market"]
        )
