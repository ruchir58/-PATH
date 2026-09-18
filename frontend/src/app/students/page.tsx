"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Download, Search, Filter } from "lucide-react";
import axios from "axios";
import clsx from "clsx";

export default function StudentsPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("");

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const latestRes = await axios.get(`http://localhost:8005/datasets/latest`);
      const dsId = latestRes.data.id;
      setDatasetId(dsId);
      const res = await axios.get(`http://localhost:8005/datasets/${dsId}/students`, {
        params: { search, risk_level: riskFilter }
      });
      setStudents(res.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [search, riskFilter]);

  const handleExportCSV = () => {
    if (datasetId) window.open(`http://localhost:8005/datasets/${datasetId}/export/csv?risk_level=${riskFilter}`, "_blank");
  };

  const handleExportPDF = () => {
    if (datasetId) window.open(`http://localhost:8005/datasets/${datasetId}/export/pdf?risk_level=${riskFilter}`, "_blank");
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-[#4A3B32]">Students Directory</h2>
          <p className="text-sm text-[#4A3B32]/70">View and manage student academic risks.</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={handleExportCSV} className="flex items-center gap-2 bg-white border border-[#D3B89B] text-[#4A3B32] px-4 py-2 rounded-xl text-sm font-medium hover:bg-[#F5F5DC]">
            <Download size={16} /> CSV
          </button>
          <button onClick={handleExportPDF} className="flex items-center gap-2 bg-white border border-[#D3B89B] text-[#4A3B32] px-4 py-2 rounded-xl text-sm font-medium hover:bg-[#F5F5DC]">
            <Download size={16} /> PDF
          </button>
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm border border-[#D3B89B]/30 flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 min-w-[250px]">
          <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-[#4A3B32]/50">
            <Search size={18} />
          </span>
          <input
            type="text"
            className="w-full bg-[#F5F5DC]/50 border border-[#D3B89B] rounded-xl py-2 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-[#C05B43]/50"
            placeholder="Search by name or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={18} className="text-[#4A3B32]/70" />
          <select
            className="bg-[#F5F5DC]/50 border border-[#D3B89B] rounded-xl py-2 px-4 focus:outline-none focus:ring-2 focus:ring-[#C05B43]/50"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="">All Risk Levels</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-[#D3B89B]/30 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#4A3B32] text-[#F5F5DC] text-sm">
                <th className="p-4 font-semibold">ID</th>
                <th className="p-4 font-semibold">Name</th>
                <th className="p-4 font-semibold">Class</th>
                <th className="p-4 font-semibold">Attendance</th>
                <th className="p-4 font-semibold">Avg Score</th>
                <th className="p-4 font-semibold">Risk Level</th>
                <th className="p-4 font-semibold">Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-[#4A3B32]">Loading...</td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-[#4A3B32]">No students found.</td>
                </tr>
              ) : (
                students.map((student, idx) => (
                  <tr key={student.id} className={clsx("border-b border-[#D3B89B]/20 hover:bg-[#F5F5DC]/30 transition-colors", idx % 2 === 0 ? "bg-white" : "bg-[#F5F5DC]/10")}>
                    <td className="p-4 text-sm text-[#4A3B32]">{student.student_record_id || '-'}</td>
                    <td className="p-4 text-sm font-medium text-[#4A3B32]">{student.name || '-'}</td>
                    <td className="p-4 text-sm text-[#4A3B32]">{student.class_name || '-'}</td>
                    <td className="p-4 text-sm text-[#4A3B32]">{student.attendance?.toFixed(1) || '-'}%</td>
                    <td className="p-4 text-sm text-[#4A3B32]">{student.average_score?.toFixed(1) || '-'}%</td>
                    <td className="p-4">
                      <span className={clsx(
                        "px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider",
                        student.risk_level === 'high' ? "bg-[#e57373]/20 text-[#c62828]" :
                        student.risk_level === 'medium' ? "bg-[#ffb74d]/20 text-[#ef6c00]" :
                        "bg-[#81c784]/20 text-[#2e7d32]"
                      )}>
                        {student.risk_level || 'Unknown'}
                      </span>
                    </td>
                    <td className="p-4 text-sm">
                      <Link href={`/students/${student.id}`} className="text-[#C05B43] hover:underline font-medium">
                        View Profile
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
