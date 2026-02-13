"use client";

import { useState, useMemo } from "react";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from "@tanstack/react-table";
import type { Deal } from "@/lib/types";
import DealStageBadge from "./DealStageBadge";
import { DEAL_STAGES } from "@/lib/constants";
import { formatDate, formatSF, truncate } from "@/lib/utils";

interface DealPipelineTableProps {
  deals: Deal[];
}

export default function DealPipelineTable({ deals }: DealPipelineTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [stageFilter, setStageFilter] = useState<string | null>(null);
  const [expandedComments, setExpandedComments] = useState<Set<string>>(new Set());

  const filteredDeals = useMemo(() => {
    if (!stageFilter) return deals;
    return deals.filter((d) => d.stage === stageFilter);
  }, [deals, stageFilter]);

  const columns = useMemo<ColumnDef<Deal>[]>(
    () => [
      {
        accessorKey: "stage",
        header: "Stage",
        cell: ({ row }) => <DealStageBadge stage={row.original.stage} />,
        size: 120,
      },
      {
        accessorKey: "tenant_name",
        header: "Tenant / Industry",
        cell: ({ row }) => (
          <div>
            <div className="font-medium">{row.original.tenant_name || "—"}</div>
            {row.original.tenant_industry && (
              <div className="text-xs text-gray-500">{row.original.tenant_industry}</div>
            )}
          </div>
        ),
        size: 200,
      },
      {
        accessorKey: "broker_name",
        header: "Broker",
        cell: ({ row }) => (
          <div>
            <div>{row.original.broker_name || "—"}</div>
            {row.original.broker_firm && (
              <div className="text-xs text-gray-500">{row.original.broker_firm}</div>
            )}
          </div>
        ),
        size: 160,
      },
      {
        accessorKey: "size_raw",
        header: "Size",
        cell: ({ row }) => {
          if (row.original.size_min_sf && row.original.size_max_sf && row.original.size_min_sf !== row.original.size_max_sf) {
            return `${row.original.size_min_sf.toLocaleString()} - ${row.original.size_max_sf.toLocaleString()} SF`;
          }
          if (row.original.size_min_sf) {
            return formatSF(row.original.size_min_sf);
          }
          return row.original.size_raw || "—";
        },
        size: 140,
      },
      {
        accessorKey: "deal_type",
        header: "Type",
        size: 100,
      },
      {
        accessorKey: "transaction_type",
        header: "Lease/Purchase",
        size: 120,
      },
      {
        accessorKey: "commencement",
        header: "Commencement",
        size: 120,
      },
      {
        accessorKey: "initial_inquiry",
        header: "Initial Inquiry",
        cell: ({ row }) => formatDate(row.original.initial_inquiry),
        size: 120,
      },
      {
        accessorKey: "comments",
        header: "Comments",
        cell: ({ row }) => {
          const id = row.original.id;
          const expanded = expandedComments.has(id);
          const text = row.original.comments;
          if (!text) return "—";
          if (text.length <= 100) return <span className="text-sm">{text}</span>;
          return (
            <div>
              <span className="text-sm">
                {expanded ? text : truncate(text, 100)}
              </span>
              <button
                className="text-blue-600 text-xs ml-1 hover:underline"
                onClick={() => {
                  setExpandedComments((prev) => {
                    const next = new Set(prev);
                    if (next.has(id)) next.delete(id);
                    else next.add(id);
                    return next;
                  });
                }}
              >
                {expanded ? "less" : "more"}
              </button>
            </div>
          );
        },
        size: 300,
      },
    ],
    [expandedComments]
  );

  const table = useReactTable({
    data: filteredDeals,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  return (
    <div>
      {/* Stage filter bar */}
      <div className="flex gap-2 mb-4 flex-wrap">
        <button
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            !stageFilter ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
          }`}
          onClick={() => setStageFilter(null)}
        >
          All ({deals.length})
        </button>
        {DEAL_STAGES.map((s) => {
          const count = deals.filter((d) => d.stage === s.key).length;
          if (count === 0) return null;
          return (
            <button
              key={s.key}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                stageFilter === s.key
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
              onClick={() => setStageFilter(stageFilter === s.key ? null : s.key)}
            >
              {s.label} ({count})
            </button>
          );
        })}
      </div>

      {/* Table */}
      <div className="overflow-x-auto border border-gray-200 rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    onClick={header.column.getToggleSortingHandler()}
                    style={{ width: header.getSize() }}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === "asc" ? " ↑" : ""}
                      {header.column.getIsSorted() === "desc" ? " ↓" : ""}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-gray-500">
                  No deals found
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3 text-sm">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
