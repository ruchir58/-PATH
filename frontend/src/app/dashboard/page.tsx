"use client";

import { useEffect, useState } from "react";
import { Users, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import axios from "axios";

export default function DashboardPage() {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const latestRes = await axios.get(`http://localhost:8005/datasets/latest`);
        const datasetId = latestRes.data.id;
        const res = await axios.get(`http://localhost:8005/datasets/${datasetId}/dashboard-summary`);
        setSummary(res.data);
      } catch (err) {
        console.error("Failed to load dashboard summary", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) return <div className="p-8 text-[#4A3B32]">Loading dashboard...</div>;
  if (!summary || summary.total_students === 0) return (
    <div className="p-8 text-[#4A3B32]">
      <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
        <p>No data available. Please upload and process a dataset first.</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-[#4A3B32]">Dashboard</h2>
          <p className="text-sm text-[#4A3B32]/70">Overview of student academic risk.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Students" value={summary.total_students} icon={<Users size={24} />} color="bg-[#D3B89B]/20 text-[#4A3B32]" />
        <StatCard title="Low Risk" value={summary.risk_distribution.low} icon={<CheckCircle size={24} />} color="bg-[#7A9A74]/20 text-[#5A7755]" />
        <StatCard title="Medium Risk" value={summary.risk_distribution.medium} icon={<Clock size={24} />} color="bg-[#D3B89B]/40 text-[#8B7355]" />
        <StatCard title="High Risk" value={summary.risk_distribution.high} icon={<AlertTriangle size={24} />} color="bg-[#C05B43]/20 text-[#9A422D]" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
          <h3 className="text-lg font-semibold text-[#4A3B32] mb-4">Risk Distribution</h3>
          <div className="h-64 flex items-center justify-center bg-white rounded-xl">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: 'Low Risk', value: summary.risk_distribution.low },
                    { name: 'Medium Risk', value: summary.risk_distribution.medium },
                    { name: 'High Risk', value: summary.risk_distribution.high },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  <Cell fill="#7A9A74" />
                  <Cell fill="#D3B89B" />
                  <Cell fill="#C05B43" />
                </Pie>
                <Tooltip 
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
          <h3 className="text-lg font-semibold text-[#4A3B32] mb-4">Key Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 bg-[#F5F5DC]/50 rounded-xl">
              <span className="font-medium">Average Attendance</span>
              <span className="text-lg font-bold">{summary.average_attendance}%</span>
            </div>
            <div className="flex justify-between items-center p-4 bg-[#F5F5DC]/50 rounded-xl">
              <span className="font-medium">Average Performance</span>
              <span className="text-lg font-bold">{summary.average_performance}%</span>
            </div>
          </div>
          <div className="mt-6 text-sm text-[#4A3B32]/60 italic text-center">
            "Risk indicators help faculty identify students who may benefit from support."
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string, value: number, icon: any, color: string }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30 flex items-center space-x-4">
      <div className={`p-4 rounded-xl ${color}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-[#4A3B32]/70">{title}</p>
        <p className="text-2xl font-bold text-[#4A3B32]">{value}</p>
      </div>
    </div>
  );
}
