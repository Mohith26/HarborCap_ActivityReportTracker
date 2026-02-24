export const DEAL_STAGES = [
  { key: "1-Inquiry",         label: "Inquiry",         numeric: 1, color: "bg-sky-500 text-white",        group: "active" },
  { key: "2-Review Info",     label: "Review Info",     numeric: 2, color: "bg-blue-400 text-white",       group: "active" },
  { key: "3-Touring",         label: "Touring",         numeric: 3, color: "bg-teal-500 text-white",       group: "active" },
  { key: "4-Proposal",        label: "Proposal / RFP",  numeric: 4, color: "bg-indigo-500 text-white",     group: "active" },
  { key: "5-LOI Negotiation", label: "LOI Negotiation", numeric: 5, color: "bg-blue-600 text-white",       group: "active" },
  { key: "6-Lease Review",    label: "Lease Review",    numeric: 6, color: "bg-blue-900 text-white",       group: "active" },
  { key: "7-Complete",        label: "Complete",        numeric: 7, color: "bg-green-600 text-white",      group: "closed" },
  { key: "8-On Hold",         label: "On Hold / Idle",  numeric: 8, color: "bg-amber-400 text-gray-900",   group: "off_ramp" },
  { key: "9-Dead",            label: "Dead / Removed",  numeric: 9, color: "bg-red-500 text-white",        group: "off_ramp" },
] as const;

export const STAGE_COLOR_MAP: Record<string, string> = Object.fromEntries(
  DEAL_STAGES.map((s) => [s.key, s.color])
);

export const ACTIVE_STAGES = DEAL_STAGES.filter((s) => s.group === "active");
export const ACTIVE_STAGE_KEYS = ACTIVE_STAGES.map((s) => s.key);

export const PROPERTY_TYPES = [
  "Industrial",
  "Commercial",
  "Mixed-Use",
  "Office",
  "Retail",
  "Warehouse",
] as const;
