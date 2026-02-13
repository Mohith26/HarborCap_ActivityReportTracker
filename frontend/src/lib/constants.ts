export const DEAL_STAGES = [
  { key: "1-Legal", label: "Legal", numeric: 1, color: "bg-blue-900 text-white" },
  { key: "2-LOI", label: "LOI", numeric: 2, color: "bg-blue-600 text-white" },
  { key: "3-Touring", label: "Touring", numeric: 3, color: "bg-teal-500 text-white" },
  { key: "4-Inquiry", label: "Inquiry", numeric: 4, color: "bg-amber-500 text-white" },
  { key: "5-Complete", label: "Complete", numeric: 5, color: "bg-green-600 text-white" },
  { key: "6-Idle", label: "Idle", numeric: 6, color: "bg-gray-400 text-white" },
  { key: "7-Dead", label: "Dead", numeric: 7, color: "bg-red-500 text-white" },
] as const;

export const STAGE_COLOR_MAP: Record<string, string> = {
  "1-Legal": "bg-blue-900 text-white",
  "2-LOI": "bg-blue-600 text-white",
  "3-Touring": "bg-teal-500 text-white",
  "4-Inquiry": "bg-amber-500 text-white",
  "5-Complete": "bg-green-600 text-white",
  "6-Idle": "bg-gray-400 text-white",
  "7-Dead": "bg-red-500 text-white",
};

export const PROPERTY_TYPES = [
  "Industrial",
  "Commercial",
  "Mixed-Use",
  "Office",
  "Retail",
  "Warehouse",
] as const;
