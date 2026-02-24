"use client";

import { useEffect, useState } from "react";
import { X, ArrowUp, ArrowDown, Minus, FileText, Loader2 } from "lucide-react";
import DealStageBadge from "./DealStageBadge";
import { dealsAPI } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { Deal } from "@/lib/types";

interface TenantHistoryTimelineProps {
  propertyId: string;
  tenantName: string;
  propertyName?: string;
  onClose: () => void;
}

export default function TenantHistoryTimeline({
  propertyId,
  tenantName,
  propertyName,
  onClose,
}: TenantHistoryTimelineProps) {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dealsAPI
      .history(propertyId, tenantName)
      .then(({ data }) => setDeals(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [propertyId, tenantName]);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/30" onClick={onClose} />

      {/* Slide-over panel */}
      <div className="relative h-full w-full max-w-lg bg-white shadow-xl overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-start justify-between z-10">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{tenantName}</h2>
            {propertyName && (
              <p className="text-sm text-gray-500 mt-0.5">{propertyName}</p>
            )}
            <p className="text-xs text-gray-400 mt-1">
              {deals.length} report{deals.length !== 1 ? "s" : ""} found
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {loading ? (
            <div className="flex justify-center py-12">
              <Loader2 size={24} className="animate-spin text-blue-600" />
            </div>
          ) : deals.length === 0 ? (
            <p className="text-center text-gray-500 py-12">
              No history found for this tenant.
            </p>
          ) : (
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />

              <div className="space-y-0">
                {deals.map((deal, idx) => {
                  const prevDeal = idx > 0 ? deals[idx - 1] : null;
                  const stageChanged =
                    prevDeal && prevDeal.stage !== deal.stage;
                  const stageProgressed =
                    stageChanged &&
                    (deal.stage_numeric || 0) > (prevDeal!.stage_numeric || 0);
                  const stageRegressed =
                    stageChanged &&
                    (deal.stage_numeric || 0) < (prevDeal!.stage_numeric || 0);

                  return (
                    <div key={deal.id} className="relative pl-10">
                      {/* Timeline dot */}
                      <div
                        className={`absolute left-2.5 top-5 w-3 h-3 rounded-full border-2 border-white ${
                          stageChanged
                            ? stageProgressed
                              ? "bg-green-500"
                              : "bg-red-500"
                            : "bg-gray-400"
                        }`}
                      />

                      {/* Stage transition indicator */}
                      {stageChanged && (
                        <div className="mb-1 flex items-center gap-1.5 text-xs">
                          {stageProgressed ? (
                            <ArrowUp
                              size={12}
                              className="text-green-600"
                            />
                          ) : stageRegressed ? (
                            <ArrowDown
                              size={12}
                              className="text-red-600"
                            />
                          ) : null}
                          <span
                            className={
                              stageProgressed
                                ? "text-green-700 font-medium"
                                : "text-red-700 font-medium"
                            }
                          >
                            {prevDeal!.stage} &rarr; {deal.stage}
                          </span>
                        </div>
                      )}

                      {!stageChanged && idx > 0 && (
                        <div className="mb-1 flex items-center gap-1.5 text-xs text-gray-400">
                          <Minus size={12} />
                          <span>No stage change</span>
                        </div>
                      )}

                      {/* Card */}
                      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4 hover:border-gray-300 transition-colors">
                        <div className="flex items-center justify-between mb-2">
                          <DealStageBadge stage={deal.stage} />
                          <span className="text-xs text-gray-500">
                            {formatDate(deal.snapshot_date)}
                          </span>
                        </div>

                        {/* Report source */}
                        {deal.report_file_name && (
                          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
                            <FileText size={12} />
                            <span className="truncate">
                              {deal.report_file_name}
                            </span>
                            {deal.report_date && (
                              <span className="text-gray-400">
                                ({formatDate(deal.report_date)})
                              </span>
                            )}
                          </div>
                        )}

                        {/* Deal details grid */}
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm mt-2">
                          {deal.size_raw && (
                            <>
                              <span className="text-gray-500">Size</span>
                              <span className="text-gray-900">
                                {deal.size_raw}
                              </span>
                            </>
                          )}
                          {deal.broker_name && (
                            <>
                              <span className="text-gray-500">Broker</span>
                              <span className="text-gray-900">
                                {deal.broker_name}
                                {deal.broker_firm && (
                                  <span className="text-gray-500">
                                    {" "}
                                    ({deal.broker_firm})
                                  </span>
                                )}
                              </span>
                            </>
                          )}
                          {deal.transaction_type && (
                            <>
                              <span className="text-gray-500">Type</span>
                              <span className="text-gray-900">
                                {deal.transaction_type}
                              </span>
                            </>
                          )}
                          {deal.commencement && (
                            <>
                              <span className="text-gray-500">Commence</span>
                              <span className="text-gray-900">
                                {deal.commencement}
                              </span>
                            </>
                          )}
                        </div>

                        {/* Comments */}
                        {deal.comments && (
                          <p className="mt-2 text-sm text-gray-600 bg-gray-50 rounded p-2">
                            {deal.comments}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
