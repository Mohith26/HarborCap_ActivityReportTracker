"use client";

import { useState } from "react";
import type { AIInsight } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { ChevronDown, ChevronUp, Brain } from "lucide-react";

interface InsightCardProps {
  insight: AIInsight;
}

const TYPE_LABELS: Record<string, string> = {
  pipeline_health: "Pipeline Health",
  dead_deal_analysis: "Dead Deal Analysis",
  deal_velocity: "Deal Velocity",
  conversion_rate: "Conversion Rate",
  market_trend: "Market Trend",
};

const TYPE_COLORS: Record<string, string> = {
  pipeline_health: "bg-blue-100 text-blue-700",
  dead_deal_analysis: "bg-red-100 text-red-700",
  deal_velocity: "bg-purple-100 text-purple-700",
  conversion_rate: "bg-green-100 text-green-700",
  market_trend: "bg-amber-100 text-amber-700",
};

export default function InsightCard({ insight }: InsightCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Brain size={18} className="text-blue-600" />
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">{insight.title}</span>
              <span
                className={`px-2 py-0.5 rounded text-xs font-medium ${
                  TYPE_COLORS[insight.insight_type] || "bg-gray-100 text-gray-700"
                }`}
              >
                {TYPE_LABELS[insight.insight_type] || insight.insight_type}
              </span>
            </div>
            <div className="text-xs text-gray-500 mt-0.5">
              Generated {formatDate(insight.created_at)}
              {insight.model_used && ` · ${insight.model_used}`}
            </div>
          </div>
        </div>
        {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
      </button>
      {expanded && (
        <div className="px-4 pb-4 pt-2 border-t border-gray-100">
          <div
            className="prose prose-sm max-w-none text-gray-700"
            dangerouslySetInnerHTML={{ __html: formatMarkdown(insight.content) }}
          />
        </div>
      )}
    </div>
  );
}

function formatMarkdown(text: string): string {
  // Simple markdown to HTML conversion
  return text
    .replace(/### (.*)/g, "<h3 class='font-semibold mt-3 mb-1'>$1</h3>")
    .replace(/## (.*)/g, "<h2 class='font-semibold text-lg mt-4 mb-2'>$1</h2>")
    .replace(/# (.*)/g, "<h1 class='font-bold text-xl mt-4 mb-2'>$1</h1>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/^- (.*)/gm, "<li class='ml-4'>$1</li>")
    .replace(/^\d+\. (.*)/gm, "<li class='ml-4 list-decimal'>$1</li>")
    .replace(/\n\n/g, "<br/><br/>")
    .replace(/\n/g, "<br/>");
}
