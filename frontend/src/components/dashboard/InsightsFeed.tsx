"use client";

import Link from "next/link";
import type { AIInsight } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Brain, Globe, Sparkles, Loader2, AlertTriangle, X } from "lucide-react";

interface InsightsFeedProps {
  insights: AIInsight[];
  onGenerateClick: () => void;
  generating: boolean;
  error?: string | null;
  onDismissError?: () => void;
}

const SEVERITY_BORDER: Record<string, string> = {
  info: "border-l-blue-400",
  warning: "border-l-amber-400",
  critical: "border-l-red-400",
  positive: "border-l-green-400",
};

const TYPE_LABELS: Record<string, string> = {
  pipeline_health: "Pipeline Health",
  dead_deal_analysis: "Dead Deals",
  deal_velocity: "Deal Velocity",
  conversion_rate: "Conversion Rate",
  market_trend: "Market Trend",
  stale_deals: "Stale Deals",
  pipeline_velocity: "Pipeline Velocity",
  geographic_trend: "Geographic",
  conversion_anomaly: "Conversion",
  leasing_momentum: "Momentum",
  stage_bottleneck: "Bottleneck",
  dead_deal_patterns: "Dead Patterns",
};

export default function InsightsFeed({ insights, onGenerateClick, generating, error, onDismissError }: InsightsFeedProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-indigo-600" />
          <h3 className="font-semibold text-gray-900">AI Insights</h3>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onGenerateClick}
            disabled={generating}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {generating ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles size={14} />
                Generate Insights
              </>
            )}
          </button>
          <Link href="/insights" className="text-sm text-indigo-600 hover:underline">
            View all
          </Link>
        </div>
      </div>

      {error && (
        <div className="mx-4 mt-3 flex items-start gap-2 rounded-lg bg-red-50 border border-red-200 px-4 py-3">
          <AlertTriangle size={16} className="text-red-500 mt-0.5 shrink-0" />
          <p className="text-sm text-red-700 flex-1">{error}</p>
          {onDismissError && (
            <button onClick={onDismissError} className="text-red-400 hover:text-red-600 shrink-0">
              <X size={14} />
            </button>
          )}
        </div>
      )}

      <div className="divide-y divide-gray-100">
        {insights.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            <Brain size={32} className="mx-auto mb-2 text-gray-300" />
            <p>No insights generated yet.</p>
            <p className="text-sm mt-1">Click "Generate Insights" to analyze your portfolio.</p>
          </div>
        ) : (
          insights.slice(0, 5).map((insight) => (
            <div
              key={insight.id}
              className={`px-6 py-3 border-l-4 ${SEVERITY_BORDER[insight.severity || "info"] || "border-l-gray-300"}`}
            >
              <div className="flex items-start gap-3">
                {insight.scope === "portfolio" ? (
                  <Globe size={16} className="text-indigo-500 mt-0.5 shrink-0" />
                ) : (
                  <Brain size={16} className="text-blue-500 mt-0.5 shrink-0" />
                )}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-sm text-gray-900">{insight.title}</span>
                    <span className="px-1.5 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                      {TYPE_LABELS[insight.insight_type] || insight.insight_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-0.5 line-clamp-2">
                    {insight.content.replace(/[#*_]/g, "").substring(0, 200)}...
                  </p>
                  <div className="text-xs text-gray-400 mt-1">
                    {formatDate(insight.created_at)}
                    {insight.is_auto_generated && " · Auto"}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
