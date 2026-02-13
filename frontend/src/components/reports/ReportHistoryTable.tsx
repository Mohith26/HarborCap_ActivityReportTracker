"use client";

import type { ActivityReport } from "@/lib/types";
import { formatDate, formatFileSize } from "@/lib/utils";
import { FileText, RefreshCw, Trash2 } from "lucide-react";

interface ReportHistoryTableProps {
  reports: ActivityReport[];
  onReprocess?: (reportId: string) => void;
  onDelete?: (reportId: string) => void;
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-700",
    processing: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors[status] || "bg-gray-100 text-gray-700"}`}>
      {status}
    </span>
  );
}

export default function ReportHistoryTable({ reports, onReprocess, onDelete }: ReportHistoryTableProps) {
  if (reports.length === 0) {
    return <p className="text-gray-500 text-sm">No reports uploaded yet.</p>;
  }

  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">File</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Report Date</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Uploaded</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {reports.map((report) => (
            <tr key={report.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-sm">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-gray-400 shrink-0" />
                  <span className="truncate max-w-xs">{report.file_name}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-sm uppercase text-gray-500">{report.file_type}</td>
              <td className="px-4 py-3 text-sm text-gray-500">{formatFileSize(report.file_size_bytes)}</td>
              <td className="px-4 py-3 text-sm">{formatDate(report.report_date)}</td>
              <td className="px-4 py-3">
                <StatusBadge status={report.extraction_status} />
                {report.extraction_errors && report.extraction_errors.length > 0 && (
                  <p className="text-xs text-red-500 mt-1">{report.extraction_errors[0]}</p>
                )}
              </td>
              <td className="px-4 py-3 text-sm text-gray-500">{formatDate(report.created_at)}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {onReprocess && (
                    <button
                      onClick={() => onReprocess(report.id)}
                      className="text-blue-600 hover:text-blue-800"
                      title="Reprocess"
                    >
                      <RefreshCw size={16} />
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(report.id)}
                      className="text-red-500 hover:text-red-700"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
