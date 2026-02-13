export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Property {
  id: string;
  name: string;
  address: string | null;
  city: string | null;
  state: string | null;
  property_type: string | null;
  total_sf: number | null;
  num_buildings: number | null;
  description: string | null;
  created_by: string | null;
  created_at: string;
  updated_at: string;
  report_count?: number;
  active_deal_count?: number;
  last_report_date?: string | null;
}

export type DealStage =
  | "1-Legal"
  | "2-LOI"
  | "3-Touring"
  | "4-Inquiry"
  | "5-Complete"
  | "6-Idle"
  | "7-Dead";

export interface Deal {
  id: string;
  property_id: string;
  report_id: string;
  stage: string;
  stage_numeric: number | null;
  deal_type: string | null;
  tenant_name: string | null;
  tenant_industry: string | null;
  is_undisclosed: boolean;
  broker_name: string | null;
  broker_firm: string | null;
  broker_phone: string | null;
  broker_email: string | null;
  initial_inquiry: string | null;
  size_min_sf: number | null;
  size_max_sf: number | null;
  size_raw: string | null;
  commencement: string | null;
  transaction_type: string | null;
  comments: string | null;
  last_updated: string | null;
  last_updated_by: string | null;
  lead_contact: string | null;
  building_id: string | null;
  snapshot_date: string | null;
  created_at: string;
}

export interface PipelineSummary {
  stage: string;
  stage_numeric: number;
  count: number;
  total_min_sf: number | null;
  total_max_sf: number | null;
}

export interface ActivityReport {
  id: string;
  property_id: string;
  file_name: string;
  file_type: string;
  file_size_bytes: number | null;
  report_date: string | null;
  extraction_status: "pending" | "processing" | "completed" | "failed";
  extraction_errors: string[] | null;
  created_at: string;
  sheet_names?: string[] | null;
  raw_extraction?: Record<string, unknown> | null;
  deal_count?: number;
  availability_count?: number;
}

export interface Availability {
  id: string;
  property_id: string;
  building: string | null;
  total_size_sf: number | null;
  status: string | null;
  office_sf: number | null;
  lease_rate_psf: number | null;
  opex: number | null;
  sale_price_psf: number | null;
  power_amps: number | null;
  loading_doors: string | null;
  eave_height: string | null;
  crane_ready: string | null;
  land_acreage: number | null;
  additional_info: string | null;
  snapshot_date: string | null;
  created_at: string;
}

export interface PropertyMetric {
  id: string;
  property_id: string;
  report_date: string | null;
  total_property_sf: number | null;
  vacant_sf: number | null;
  vacancy_pct: number | null;
  occupancy_pct: number | null;
  shadow_vacancy_sf: number | null;
  inquiries_sent: number | null;
  tours_conducted: number | null;
  proposals_sent: number | null;
  quoted_rate_psf: number | null;
  additional_metrics: Record<string, unknown> | null;
  snapshot_date: string | null;
  created_at: string;
}

export interface AIInsight {
  id: string;
  property_id: string | null;
  insight_type: string;
  title: string;
  content: string;
  model_used: string | null;
  date_range_start: string | null;
  date_range_end: string | null;
  created_at: string;
}

export interface PropertySummary {
  property: Property;
  total_reports: number;
  latest_report_date: string | null;
  deal_pipeline: Record<
    string,
    { count: number; stage_numeric: number }
  >;
}
