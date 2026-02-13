"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthGuard from "@/components/layout/AuthGuard";
import Sidebar from "@/components/layout/Sidebar";
import DealStageBadge from "@/components/deals/DealStageBadge";
import { propertiesAPI } from "@/lib/api";
import type { Property } from "@/lib/types";
import { formatDate, formatSF } from "@/lib/utils";
import { Building2, FileText, TrendingUp, Plus } from "lucide-react";

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    propertiesAPI.list().then(({ data }) => {
      setProperties(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const totalProperties = properties.length;
  const totalReports = properties.reduce((sum, p) => sum + (p.report_count || 0), 0);
  const totalActiveDeals = properties.reduce((sum, p) => sum + (p.active_deal_count || 0), 0);

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-500 mt-1">Portfolio overview</p>
              </div>
              <Link
                href="/properties"
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                <Plus size={18} />
                Add Property
              </Link>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Building2 size={20} className="text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Properties</p>
                    <p className="text-2xl font-bold">{totalProperties}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <FileText size={20} className="text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Reports Uploaded</p>
                    <p className="text-2xl font-bold">{totalReports}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <TrendingUp size={20} className="text-amber-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Active Deals</p>
                    <p className="text-2xl font-bold">{totalActiveDeals}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Properties Grid */}
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
              </div>
            ) : properties.length === 0 ? (
              <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
                <Building2 size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No properties yet</h3>
                <p className="text-gray-500 mb-4">Create your first property to start tracking activity reports.</p>
                <Link
                  href="/properties"
                  className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
                >
                  <Plus size={16} />
                  Add Property
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {properties.map((prop) => (
                  <Link
                    key={prop.id}
                    href={`/properties/${prop.id}`}
                    className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow"
                  >
                    <h3 className="font-semibold text-gray-900 mb-1">{prop.name}</h3>
                    {prop.address && (
                      <p className="text-sm text-gray-500 mb-3">
                        {prop.address}
                        {prop.city && `, ${prop.city}`}
                        {prop.state && `, ${prop.state}`}
                      </p>
                    )}
                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      {prop.total_sf && <span>{formatSF(prop.total_sf)}</span>}
                      {prop.property_type && <span className="capitalize">{prop.property_type}</span>}
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">
                        {prop.report_count || 0} reports
                      </span>
                      <span className="text-gray-500">
                        {prop.active_deal_count || 0} active deals
                      </span>
                    </div>
                    {prop.last_report_date && (
                      <p className="text-xs text-gray-400 mt-2">
                        Last report: {formatDate(prop.last_report_date)}
                      </p>
                    )}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
