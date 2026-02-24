"use client";

import Link from "next/link";
import { DEAL_STAGES, STAGE_COLOR_MAP } from "@/lib/constants";
import type { PortfolioPipelineSummary } from "@/lib/types";

interface PropertyLeaseProgressProps {
  pipelineData: PortfolioPipelineSummary[];
}

export default function PropertyLeaseProgress({ pipelineData }: PropertyLeaseProgressProps) {
  // Sort by most active deals first
  const sorted = [...pipelineData].sort((a, b) => b.total_active_deals - a.total_active_deals);

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="font-semibold text-gray-900">Lease Progress by Property</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="px-4 py-2.5 text-left font-medium text-gray-500 sticky left-0 bg-white">
                Property
              </th>
              {DEAL_STAGES.map((stage) => (
                <th
                  key={stage.key}
                  className="px-2 py-2.5 text-center font-medium text-gray-500 whitespace-nowrap"
                  title={stage.label}
                >
                  <span className="text-xs">{stage.label}</span>
                </th>
              ))}
              <th className="px-3 py-2.5 text-center font-medium text-gray-500">Active</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((prop) => {
              const isStagnant = prop.total_active_deals === 0;
              return (
                <tr
                  key={prop.property_id}
                  className={`border-b border-gray-50 hover:bg-gray-50 ${isStagnant ? "opacity-60" : ""}`}
                >
                  <td className="px-4 py-2.5 sticky left-0 bg-white">
                    <Link
                      href={`/properties/${prop.property_id}`}
                      className="font-medium text-gray-900 hover:text-blue-600"
                    >
                      {prop.property_name}
                    </Link>
                  </td>
                  {DEAL_STAGES.map((stage) => {
                    const count = prop.stage_counts[stage.key] || 0;
                    return (
                      <td key={stage.key} className="px-2 py-2.5 text-center">
                        {count > 0 ? (
                          <span
                            className={`inline-flex items-center justify-center min-w-[1.5rem] h-6 px-1.5 rounded-full text-xs font-medium ${STAGE_COLOR_MAP[stage.key]}`}
                          >
                            {count}
                          </span>
                        ) : (
                          <span className="text-gray-300">-</span>
                        )}
                      </td>
                    );
                  })}
                  <td className="px-3 py-2.5 text-center">
                    <span className={`font-semibold ${isStagnant ? "text-gray-400" : "text-gray-900"}`}>
                      {prop.total_active_deals}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {sorted.length === 0 && (
        <div className="px-6 py-8 text-center text-gray-500">
          No properties with reports yet. Upload activity reports to see lease progress.
        </div>
      )}
    </div>
  );
}
