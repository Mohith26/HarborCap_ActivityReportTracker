"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthGuard from "@/components/layout/AuthGuard";
import Sidebar from "@/components/layout/Sidebar";
import { propertiesAPI } from "@/lib/api";
import type { Property } from "@/lib/types";
import { PROPERTY_TYPES } from "@/lib/constants";
import { formatSF, formatDate } from "@/lib/utils";
import { Plus, X } from "lucide-react";

export default function PropertiesPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    address: "",
    city: "",
    state: "",
    property_type: "",
    total_sf: "",
    num_buildings: "",
    description: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const fetchProperties = () => {
    propertiesAPI.list().then(({ data }) => {
      setProperties(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await propertiesAPI.create({
        name: formData.name,
        address: formData.address || null,
        city: formData.city || null,
        state: formData.state || null,
        property_type: formData.property_type || null,
        total_sf: formData.total_sf ? parseInt(formData.total_sf) : null,
        num_buildings: formData.num_buildings ? parseInt(formData.num_buildings) : null,
        description: formData.description || null,
      });
      setShowForm(false);
      setFormData({ name: "", address: "", city: "", state: "", property_type: "", total_sf: "", num_buildings: "", description: "" });
      fetchProperties();
    } catch {
      alert("Failed to create property");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-50 p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <h1 className="text-2xl font-bold text-gray-900">Properties</h1>
              <button
                onClick={() => setShowForm(true)}
                className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                <Plus size={18} />
                Add Property
              </button>
            </div>

            {/* Create Property Modal */}
            {showForm && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-xl w-full max-w-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Create Property</h2>
                    <button onClick={() => setShowForm(false)}>
                      <X size={20} />
                    </button>
                  </div>
                  <form onSubmit={handleCreate} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                        placeholder="e.g., Twinwood Commerce Center"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                        <input
                          type="text"
                          value={formData.address}
                          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                        <input
                          type="text"
                          value={formData.city}
                          onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                        <input
                          type="text"
                          value={formData.state}
                          onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                        <select
                          value={formData.property_type}
                          onChange={(e) => setFormData({ ...formData, property_type: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select type...</option>
                          {PROPERTY_TYPES.map((t) => (
                            <option key={t} value={t.toLowerCase()}>{t}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Total SF</label>
                        <input
                          type="number"
                          value={formData.total_sf}
                          onChange={(e) => setFormData({ ...formData, total_sf: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Buildings</label>
                        <input
                          type="number"
                          value={formData.num_buildings}
                          onChange={(e) => setFormData({ ...formData, num_buildings: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={2}
                      />
                    </div>
                    <div className="flex gap-3 justify-end">
                      <button
                        type="button"
                        onClick={() => setShowForm(false)}
                        className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={submitting}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {submitting ? "Creating..." : "Create Property"}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

            {/* Properties Table */}
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Size</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reports</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Active Deals</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Report</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {properties.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                          No properties yet. Click &quot;Add Property&quot; to get started.
                        </td>
                      </tr>
                    ) : (
                      properties.map((prop) => (
                        <tr key={prop.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <Link href={`/properties/${prop.id}`} className="font-medium text-blue-600 hover:underline">
                              {prop.name}
                            </Link>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {[prop.city, prop.state].filter(Boolean).join(", ") || "—"}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500 capitalize">{prop.property_type || "—"}</td>
                          <td className="px-6 py-4 text-sm">{formatSF(prop.total_sf)}</td>
                          <td className="px-6 py-4 text-sm">{prop.report_count || 0}</td>
                          <td className="px-6 py-4 text-sm">{prop.active_deal_count || 0}</td>
                          <td className="px-6 py-4 text-sm text-gray-500">{formatDate(prop.last_report_date)}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </main>
      </div>
    </AuthGuard>
  );
}
