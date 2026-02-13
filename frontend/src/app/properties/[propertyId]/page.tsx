"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import AuthGuard from "@/components/layout/AuthGuard";
import Sidebar from "@/components/layout/Sidebar";
import DealPipelineTable from "@/components/deals/DealPipelineTable";
import FileUploadDropzone from "@/components/reports/FileUploadDropzone";
import ReportHistoryTable from "@/components/reports/ReportHistoryTable";
import InsightCard from "@/components/insights/InsightCard";
import {
  propertiesAPI,
  dealsAPI,
  reportsAPI,
  availabilitiesAPI,
  metricsAPI,
  insightsAPI,
} from "@/lib/api";
import type {
  Property,
  Deal,
  ActivityReport,
  Availability,
  PropertyMetric,
  AIInsight,
  PipelineSummary,
} from "@/lib/types";
import { formatSF, formatDate, formatCurrency } from "@/lib/utils";
import { DEAL_STAGES } from "@/lib/constants";
import { ArrowLeft, Upload, Loader2, Brain } from "lucide-react";

type Tab = "pipeline" | "availabilities" | "reports" | "insights";

export default function PropertyDetailPage() {
  const params = useParams();
  const propertyId = params.propertyId as string;

  const [property, setProperty] = useState<Property | null>(null);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [pipeline, setPipeline] = useState<PipelineSummary[]>([]);
  const [reports, setReports] = useState<ActivityReport[]>([]);
  const [availabilities, setAvailabilities] = useState<Availability[]>([]);
  const [metrics, setMetrics] = useState<PropertyMetric[]>([]);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [activeTab, setActiveTab] = useState<Tab>("pipeline");
  const [loading, setLoading] = useState(true);
  const [generatingInsights, setGeneratingInsights] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [propRes, dealsRes, pipelineRes, reportsRes, availRes, metricsRes, insightsRes] =
        await Promise.all([
          propertiesAPI.get(propertyId),
          dealsAPI.list(propertyId),
          dealsAPI.pipeline(propertyId),
          reportsAPI.list(propertyId),
          availabilitiesAPI.list(propertyId),
          metricsAPI.list(propertyId),
          insightsAPI.listForProperty(propertyId),
        ]);
      setProperty(propRes.data);
      setDeals(dealsRes.data);
      setPipeline(pipelineRes.data);
      setReports(reportsRes.data);
      setAvailabilities(availRes.data);
      setMetrics(metricsRes.data);
      setInsights(insightsRes.data);
    } catch (err) {
      console.error("Failed to load property data:", err);
    } finally {
      setLoading(false);
    }
  }, [propertyId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleReprocess = async (reportId: string) => {
    await reportsAPI.reprocess(reportId);
    setTimeout(fetchData, 2000);
  };

  const handleDeleteReport = async (reportId: string) => {
    if (!confirm("Delete this report and all its extracted data?")) return;
    await reportsAPI.delete(reportId);
    fetchData();
  };

  const handleGenerateInsights = async () => {
    setGeneratingInsights(true);
    try {
      const { data } = await insightsAPI.generate(propertyId);
      setInsights((prev) => [...data, ...prev]);
    } catch (err) {
      console.error("Failed to generate insights:", err);
      alert("Failed to generate insights. Make sure your OpenAI API key is configured.");
    } finally {
      setGeneratingInsights(false);
    }
  };

  const latestMetric = metrics[0] || null;

  if (loading) {
    return (
      <AuthGuard>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </main>
        </div>
      </AuthGuard>
    );
  }

  if (!property) {
    return (
      <AuthGuard>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 flex items-center justify-center">
            <p className="text-gray-500">Property not found</p>
          </main>
        </div>
      </AuthGuard>
    );
  }

  const tabs: { key: Tab; label: string; count?: number }[] = [
    { key: "pipeline", label: "Deal Pipeline", count: deals.length },
    { key: "availabilities", label: "Availabilities", count: availabilities.length },
    { key: "reports", label: "Reports", count: reports.length },
    { key: "insights", label: "AI Insights", count: insights.length },
  ];

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-6">
              <Link href="/properties" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4">
                <ArrowLeft size={16} />
                Back to Properties
              </Link>
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">{property.name}</h1>
                  {property.address && (
                    <p className="text-gray-500 mt-1">
                      {property.address}
                      {property.city && `, ${property.city}`}
                      {property.state && `, ${property.state}`}
                    </p>
                  )}
                  <div className="flex gap-4 mt-2 text-sm text-gray-500">
                    {property.total_sf && <span>{formatSF(property.total_sf)}</span>}
                    {property.property_type && <span className="capitalize">{property.property_type}</span>}
                    {property.num_buildings && <span>{property.num_buildings} buildings</span>}
                  </div>
                </div>
                <button
                  onClick={() => setShowUpload(!showUpload)}
                  className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  <Upload size={18} />
                  Upload Report
                </button>
              </div>
            </div>

            {/* Upload area */}
            {showUpload && (
              <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
                <h3 className="font-semibold mb-4">Upload Activity Report</h3>
                <FileUploadDropzone
                  propertyId={propertyId}
                  onUploadComplete={() => {
                    setTimeout(fetchData, 3000);
                  }}
                />
              </div>
            )}

            {/* Metrics summary (if available) */}
            {latestMetric && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                {latestMetric.total_property_sf && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 uppercase">Total SF</p>
                    <p className="text-lg font-bold">{latestMetric.total_property_sf.toLocaleString()}</p>
                  </div>
                )}
                {latestMetric.vacancy_pct != null && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 uppercase">Vacancy</p>
                    <p className="text-lg font-bold">{latestMetric.vacancy_pct}%</p>
                  </div>
                )}
                {latestMetric.inquiries_sent != null && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 uppercase">Inquiries</p>
                    <p className="text-lg font-bold">{latestMetric.inquiries_sent}</p>
                  </div>
                )}
                {latestMetric.tours_conducted != null && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 uppercase">Tours</p>
                    <p className="text-lg font-bold">{latestMetric.tours_conducted}</p>
                  </div>
                )}
                {latestMetric.proposals_sent != null && (
                  <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs text-gray-500 uppercase">Proposals</p>
                    <p className="text-lg font-bold">{latestMetric.proposals_sent}</p>
                  </div>
                )}
              </div>
            )}

            {/* Pipeline summary bar */}
            {pipeline.length > 0 && (
              <div className="flex gap-3 mb-6 flex-wrap">
                {pipeline.map((p) => (
                  <div key={p.stage} className="bg-white rounded-lg border border-gray-200 px-4 py-2">
                    <span className="text-sm font-medium">{p.stage}</span>
                    <span className="ml-2 text-lg font-bold">{p.count}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Tabs */}
            <div className="border-b border-gray-200 mb-6">
              <div className="flex gap-6">
                {tabs.map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab.key
                        ? "border-blue-600 text-blue-600"
                        : "border-transparent text-gray-500 hover:text-gray-700"
                    }`}
                  >
                    {tab.label}
                    {tab.count != null && tab.count > 0 && (
                      <span className="ml-1.5 text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full">
                        {tab.count}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab content */}
            {activeTab === "pipeline" && (
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                {deals.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No deals extracted yet. Upload an activity report to get started.</p>
                  </div>
                ) : (
                  <DealPipelineTable deals={deals} />
                )}
              </div>
            )}

            {activeTab === "availabilities" && (
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                {availabilities.length === 0 ? (
                  <p className="text-center py-8 text-gray-500">
                    No availability data found. Upload a report with an &quot;Availabilities&quot; sheet.
                  </p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Building</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size (SF)</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lease Rate PSF</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sale Price PSF</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Power</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Eave Height</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loading</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {availabilities.map((a) => (
                          <tr key={a.id} className="hover:bg-gray-50">
                            <td className="px-4 py-3 text-sm font-medium">{a.building || "—"}</td>
                            <td className="px-4 py-3 text-sm">{formatSF(a.total_size_sf)}</td>
                            <td className="px-4 py-3 text-sm">
                              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                                a.status?.toUpperCase() === "LEASED" ? "bg-green-100 text-green-700" :
                                a.status?.toUpperCase() === "AVAILABLE" ? "bg-blue-100 text-blue-700" :
                                "bg-gray-100 text-gray-700"
                              }`}>
                                {a.status || "—"}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-sm">{formatCurrency(a.lease_rate_psf)}</td>
                            <td className="px-4 py-3 text-sm">{formatCurrency(a.sale_price_psf)}</td>
                            <td className="px-4 py-3 text-sm">{a.power_amps ? `${a.power_amps}A` : "—"}</td>
                            <td className="px-4 py-3 text-sm">{a.eave_height || "—"}</td>
                            <td className="px-4 py-3 text-sm">{a.loading_doors || "—"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {activeTab === "reports" && (
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <ReportHistoryTable
                  reports={reports}
                  onReprocess={handleReprocess}
                  onDelete={handleDeleteReport}
                />
              </div>
            )}

            {activeTab === "insights" && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">AI-Generated Insights</h3>
                  <button
                    onClick={handleGenerateInsights}
                    disabled={generatingInsights || reports.length === 0}
                    className="inline-flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {generatingInsights ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Brain size={16} />
                    )}
                    {generatingInsights ? "Generating..." : "Generate Insights"}
                  </button>
                </div>
                {insights.length === 0 ? (
                  <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500">
                    <Brain size={40} className="mx-auto mb-3 text-gray-300" />
                    <p>No insights generated yet.</p>
                    <p className="text-sm mt-1">Upload reports and click &quot;Generate Insights&quot; to get AI-powered analysis.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {insights.map((insight) => (
                      <InsightCard key={insight.id} insight={insight} />
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
