import axios from "axios";
import type {
  AuthResponse,
  Property,
  Deal,
  PipelineSummary,
  ActivityReport,
  Availability,
  PropertyMetric,
  AIInsight,
  PropertySummary,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
});

// Attach JWT token to requests
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle 401 responses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  register: (email: string, password: string, full_name: string) =>
    api.post<AuthResponse>("/api/auth/register", { email, password, full_name }),
  login: (email: string, password: string) =>
    api.post<AuthResponse>("/api/auth/login", { email, password }),
  me: () => api.get<AuthResponse["user"]>("/api/auth/me"),
};

// Properties
export const propertiesAPI = {
  list: () => api.get<Property[]>("/api/properties/"),
  create: (data: Partial<Property>) => api.post<Property>("/api/properties/", data),
  get: (id: string) => api.get<Property>(`/api/properties/${id}`),
  update: (id: string, data: Partial<Property>) => api.put<Property>(`/api/properties/${id}`, data),
  delete: (id: string) => api.delete(`/api/properties/${id}`),
  summary: (id: string) => api.get<PropertySummary>(`/api/properties/${id}/summary`),
};

// Reports
export const reportsAPI = {
  upload: (propertyId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<ActivityReport>(`/api/properties/${propertyId}/reports/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: (propertyId: string) => api.get<ActivityReport[]>(`/api/properties/${propertyId}/reports`),
  get: (reportId: string) => api.get<ActivityReport>(`/api/reports/${reportId}`),
  reprocess: (reportId: string) => api.post<ActivityReport>(`/api/reports/${reportId}/reprocess`),
  delete: (reportId: string) => api.delete(`/api/reports/${reportId}`),
};

// Deals
export const dealsAPI = {
  list: (propertyId: string, params?: { stage?: string; snapshot?: string }) =>
    api.get<Deal[]>(`/api/properties/${propertyId}/deals`, { params }),
  pipeline: (propertyId: string) =>
    api.get<PipelineSummary[]>(`/api/properties/${propertyId}/deals/pipeline`),
  history: (propertyId: string, tenantName: string) =>
    api.get<Deal[]>(`/api/properties/${propertyId}/deals/history/${encodeURIComponent(tenantName)}`),
  get: (dealId: string) => api.get<Deal>(`/api/deals/${dealId}`),
  update: (dealId: string, data: Partial<Deal>) => api.put<Deal>(`/api/deals/${dealId}`, data),
};

// Availabilities
export const availabilitiesAPI = {
  list: (propertyId: string) => api.get<Availability[]>(`/api/properties/${propertyId}/availabilities`),
  history: (propertyId: string) => api.get<Availability[]>(`/api/properties/${propertyId}/availabilities/history`),
};

// Metrics
export const metricsAPI = {
  list: (propertyId: string) => api.get<PropertyMetric[]>(`/api/properties/${propertyId}/metrics`),
};

// Insights
export const insightsAPI = {
  generate: (propertyId: string, insightTypes?: string[]) =>
    api.post<AIInsight[]>(`/api/properties/${propertyId}/insights/generate`, {
      insight_types: insightTypes || null,
    }),
  listForProperty: (propertyId: string) =>
    api.get<AIInsight[]>(`/api/properties/${propertyId}/insights`),
  listAll: () => api.get<AIInsight[]>("/api/insights"),
};

export default api;
