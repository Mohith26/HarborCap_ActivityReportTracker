"use client";

import { DEAL_STAGES, STAGE_COLOR_MAP } from "@/lib/constants";

interface PortfolioFunnelProps {
  dealsByStage: Record<string, number>;
}

export default function PortfolioFunnel({ dealsByStage }: PortfolioFunnelProps) {
  const maxCount = Math.max(...Object.values(dealsByStage), 1);

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="font-semibold text-gray-900 mb-4">Portfolio Pipeline</h3>
      <div className="space-y-2">
        {DEAL_STAGES.map((stage) => {
          const count = dealsByStage[stage.key] || 0;
          const widthPct = maxCount > 0 ? Math.max((count / maxCount) * 100, 2) : 2;

          return (
            <div key={stage.key} className="flex items-center gap-3">
              <div className="w-28 text-sm text-gray-600 text-right shrink-0">
                {stage.label}
              </div>
              <div className="flex-1 bg-gray-100 rounded-full h-7 overflow-hidden">
                <div
                  className={`h-full rounded-full flex items-center justify-end pr-2 transition-all ${STAGE_COLOR_MAP[stage.key] || "bg-gray-400"}`}
                  style={{ width: `${widthPct}%`, minWidth: count > 0 ? "2rem" : "0" }}
                >
                  {count > 0 && (
                    <span className="text-xs font-medium">{count}</span>
                  )}
                </div>
              </div>
              {count === 0 && (
                <span className="text-xs text-gray-400 w-6">0</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
