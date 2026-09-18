"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { BarChart3, TrendingUp, Users } from "lucide-react";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const latestRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/latest`);
        const datasetId = latestRes.data.id;
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${datasetId}/class-analytics`);
        setAnalytics(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return <div className="p-8 text-[#4A3B32]">Loading analytics...</div>;
  if (!analytics || !analytics.class_statistics) return <div className="p-8 text-[#4A3B32]">No analytics available.</div>;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#4A3B32]">Class Analytics</h2>
        <p className="text-sm text-[#4A3B32]/70">Compare risk and performance metrics across different classes.</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {analytics.class_statistics.map((cls: any) => (
          <div key={cls.class_name} className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-semibold text-[#4A3B32]">Class: {cls.class_name || "Unknown"}</h3>
              <span className="flex items-center gap-2 text-[#4A3B32]/70 bg-[#F5F5DC]/50 px-3 py-1 rounded-full text-sm">
                <Users size={16} /> {cls.student_count} Students
              </span>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-[#F5F5DC]/30 p-4 rounded-xl border border-[#D3B89B]/20">
                <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider mb-1">Avg Attendance</p>
                <p className="text-xl font-bold text-[#4A3B32]">{cls.average_attendance}%</p>
              </div>
              <div className="bg-[#F5F5DC]/30 p-4 rounded-xl border border-[#D3B89B]/20">
                <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider mb-1">Avg Score</p>
                <p className="text-xl font-bold text-[#4A3B32]">{cls.average_score}%</p>
              </div>
              <div className="bg-[#e57373]/10 p-4 rounded-xl border border-[#e57373]/20">
                <p className="text-xs text-[#c62828]/60 uppercase tracking-wider mb-1">High Risk</p>
                <p className="text-xl font-bold text-[#c62828]">{cls.risk_distribution.high}</p>
              </div>
              <div className="bg-[#ffb74d]/10 p-4 rounded-xl border border-[#ffb74d]/20">
                <p className="text-xs text-[#ef6c00]/60 uppercase tracking-wider mb-1">Medium Risk</p>
                <p className="text-xl font-bold text-[#ef6c00]">{cls.risk_distribution.medium}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
