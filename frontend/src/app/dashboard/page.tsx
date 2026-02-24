"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthGuard from "@/components/layout/AuthGuard";
import Sidebar from "@/components/layout/Sidebar";
import PortfolioFunnel from "@/components/dashboard/PortfolioFunnel";
import PropertyLeaseProgress from "@/components/dashboard/PropertyLeaseProgress";
import InsightsFeed from "@/components/dashboard/InsightsFeed";
import { propertiesAPI, dealsAPI, insightsAPI } from "@/lib/api";
import type { Property, PortfolioPipelineSummary, AIInsight } from "@/lib/types";
import { DEAL_STAGES } from "@/lib/constants";
import { Building2, FileText, TrendingUp, CheckCircle, Plus } from "lucide-react";

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [pipeline, setPipeline] = useState<PortfolioPipelineSummary[]>([]);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [insightError, setInsightError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      propertiesAPI.list(),
      dealsAPI.portfolioPipeline(),
      insightsAPI.listLatest(10),
    ])
      .then(([propRes, pipeRes, insightRes]) => {
        setProperties(propRes.data);
        setPipeline(pipeRes.data);
        setInsights(insightRes.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Aggregate portfolio-wide stage counts
  const dealsByStage: Record<string, number> = {};
  for (const prop of pipeline) {
    for (const [stage, count] of Object.entries(prop.stage_counts)) {
      dealsByStage[stage] = (dealsByStage[stage] || 0) + count;
    }
  }

  const totalProperties = properties.length;
  const totalReports = properties.reduce((sum, p) => sum + (p.report_count || 0), 0);
  const totalActiveDeals = pipeline.reduce((sum, p) => sum + p.total_active_deals, 0);
  const completedLeases = dealsByStage["7-Complete"] || 0;

  const handleGenerateInsights = async () => {
    setGenerating(true);
    setInsightError(null);
    try {
      const { data } = await insightsAPI.generatePortfolio();
      if (data.length === 0) {
        setInsightError("No new insights were generated. Try uploading more reports first.");
      } else {
        setInsights((prev) => [...data, ...prev]);
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      const detail = axiosErr?.response?.data?.detail;
      setInsightError(detail || "Failed to generate insights. Please try again.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Lease Progress Tracker</h1>
                <p className="text-gray-500 mt-1">Portfolio-wide lease pipeline overview</p>
              </div>
              <Link
                href="/properties"
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                <Plus size={18} />
                Add Property
              </Link>
            </div>

            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
              </div>
            ) : (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <Building2 size={20} className="text-blue-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Properties</p>
                        <p className="text-2xl font-bold text-gray-900">{totalProperties}</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-teal-100 rounded-lg">
                        <TrendingUp size={20} className="text-teal-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Active Deals</p>
                        <p className="text-2xl font-bold text-gray-900">{totalActiveDeals}</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <CheckCircle size={20} className="text-green-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Completed Leases</p>
                        <p className="text-2xl font-bold text-gray-900">{completedLeases}</p>
                      </div>
                    </div>
                  </div>
                  <div className="bg-white rounded-xl border border-gray-200 p-5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-amber-100 rounded-lg">
                        <FileText size={20} className="text-amber-600" />
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Reports Uploaded</p>
                        <p className="text-2xl font-bold text-gray-900">{totalReports}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Pipeline Funnel + Insights */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <PortfolioFunnel dealsByStage={dealsByStage} />
                  <InsightsFeed
                    insights={insights}
                    onGenerateClick={handleGenerateInsights}
                    generating={generating}
                    error={insightError}
                    onDismissError={() => setInsightError(null)}
                  />
                </div>

                {/* Per-Property Lease Progress */}
                <PropertyLeaseProgress pipelineData={pipeline} />
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
