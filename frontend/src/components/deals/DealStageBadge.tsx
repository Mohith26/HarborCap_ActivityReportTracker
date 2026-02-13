"use client";

import { cn } from "@/lib/utils";
import { STAGE_COLOR_MAP } from "@/lib/constants";

interface DealStageBadgeProps {
  stage: string;
  className?: string;
}

export default function DealStageBadge({ stage, className }: DealStageBadgeProps) {
  const colorClass = STAGE_COLOR_MAP[stage] || "bg-gray-500 text-white";
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        colorClass,
        className
      )}
    >
      {stage}
    </span>
  );
}
