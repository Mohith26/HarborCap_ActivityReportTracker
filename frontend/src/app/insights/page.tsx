"use client";

import { useEffect, useState } from "react";
import AuthGuard from "@/components/layout/AuthGuard";
import Sidebar from "@/components/layout/Sidebar";
import InsightCard from "@/components/insights/InsightCard";
import { insightsAPI } from "@/lib/api";
import type { AIInsight } from "@/lib/types";
import { Brain } from "lucide-react";

export default function InsightsPage() {
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    insightsAPI.listAll().then(({ data }) => {
      setInsights(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-50 p-8">
          <div className="max-w-5xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">AI Insights</h1>
            <p className="text-gray-500 mb-8">All generated insights across your portfolio</p>

            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
              </div>
            ) : insights.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <Brain size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No insights yet</h3>
                <p className="text-gray-500">
                  Go to a property and click &quot;Generate Insights&quot; to create AI-powered analysis.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {insights.map((insight) => (
                  <InsightCard key={insight.id} insight={insight} />
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
