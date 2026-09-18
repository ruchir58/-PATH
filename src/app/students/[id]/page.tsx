"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AlertCircle, CheckCircle, TrendingUp, BrainCircuit, Activity, Edit3 } from "lucide-react";
import axios from "axios";
import clsx from "clsx";

export default function StudentProfilePage() {
  const params = useParams();
  const studentId = params.id;
  const [student, setStudent] = useState<any>(null);
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  // What-if state
  const [simAttendance, setSimAttendance] = useState<number | string>("");
  const [simScore, setSimScore] = useState<number | string>("");
  const [simResult, setSimResult] = useState<any>(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    const fetchStudent = async () => {
      try {
        const latestRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/latest`);
        const dsId = latestRes.data.id;
        setDatasetId(dsId);
        const res = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${dsId}/students/${studentId}`);
        setStudent(res.data);
        setSimAttendance(res.data.attendance || 0);
        setSimScore(res.data.average_score || 0);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchStudent();
  }, [studentId]);

  const handleSimulate = async () => {
    setSimLoading(true);
    try {
      const overrides = {
        attendance: simAttendance,
        average_score: simScore
      };
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${datasetId}/students/${studentId}/what-if`, overrides);
      setSimResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSimLoading(false);
    }
  };

  const handleMarkReviewed = async () => {
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${datasetId}/students/${studentId}/review`);
      setStudent({ ...student, review_status: "reviewed" });
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="p-8 text-[#4A3B32]">Loading profile...</div>;
  if (!student) return <div className="p-8 text-red-600">Student not found</div>;

  const isHighRisk = student.risk_level === "high";

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-[#4A3B32]">{student.name || "Unknown Student"}</h2>
          <p className="text-[#4A3B32]/70">ID: {student.student_record_id} | Class: {student.class_name}</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleMarkReviewed}
            disabled={student.review_status === 'reviewed'}
            className="flex items-center gap-2 bg-white border border-[#D3B89B] text-[#4A3B32] px-4 py-2 rounded-xl text-sm font-medium hover:bg-[#F5F5DC] disabled:opacity-50"
          >
            <CheckCircle size={16} className={student.review_status === 'reviewed' ? "text-green-600" : ""} />
            {student.review_status === 'reviewed' ? "Reviewed" : "Mark as Reviewed"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column: Risk and Reason */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30 text-center relative overflow-hidden">
            <div className={clsx(
              "absolute top-0 left-0 w-full h-2",
              isHighRisk ? "bg-[#C05B43]" : student.risk_level === 'medium' ? "bg-[#D3B89B]" : "bg-[#7A9A74]"
            )} />
            <h3 className="text-lg font-semibold text-[#4A3B32] mb-2">Predicted Risk Level</h3>
            <p className={clsx(
              "text-3xl font-bold uppercase tracking-wider mb-2",
              isHighRisk ? "text-[#C05B43]" : student.risk_level === 'medium' ? "text-[#8B7355]" : "text-[#5A7755]"
            )}>
              {student.risk_level}
            </p>
            <p className="text-sm text-[#4A3B32]/70">Probability: {(student.risk_probability * 100).toFixed(1)}%</p>
          </div>

          <div className="bg-[#C05B43]/10 p-6 rounded-2xl border border-[#C05B43]/30">
            <h3 className="text-md font-semibold text-[#9A422D] flex items-center gap-2 mb-2">
              <AlertCircle size={18} /> Why Flagged?
            </h3>
            <p className="text-sm text-[#9A422D]/90">
              {student.why_flagged || "No specific flags identified."}
            </p>
          </div>
          
          <div className="text-xs text-[#4A3B32]/60 italic text-center px-4">
            "This prediction is a recommendation for faculty review, not a final academic decision."
          </div>
        </div>

        {/* Middle Column: Academic Overview */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
            <h3 className="text-lg font-semibold text-[#4A3B32] mb-4 flex items-center gap-2">
              <Activity size={20} /> Academic Overview
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-[#F5F5DC]/50 p-4 rounded-xl">
                <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider">Attendance</p>
                <p className="text-2xl font-bold text-[#4A3B32]">{student.attendance?.toFixed(1)}%</p>
              </div>
              <div className="bg-[#F5F5DC]/50 p-4 rounded-xl">
                <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider">Average Score</p>
                <p className="text-2xl font-bold text-[#4A3B32]">{student.average_score?.toFixed(1)}%</p>
              </div>
            </div>
          </div>

          {/* What-If Analysis */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
            <h3 className="text-lg font-semibold text-[#4A3B32] mb-4 flex items-center gap-2">
              <BrainCircuit size={20} /> What-If Analysis
            </h3>
            <p className="text-sm text-[#4A3B32]/70 mb-4">Simulate improvements to see how they might reduce academic risk. This does not alter actual records.</p>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-xs font-medium text-[#4A3B32] mb-1">Target Attendance (%)</label>
                <input 
                  type="number" 
                  className="w-full bg-[#F5F5DC]/50 border border-[#D3B89B] rounded-xl py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#C05B43]/50"
                  value={simAttendance}
                  onChange={(e) => setSimAttendance(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[#4A3B32] mb-1">Target Avg Score (%)</label>
                <input 
                  type="number" 
                  className="w-full bg-[#F5F5DC]/50 border border-[#D3B89B] rounded-xl py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#C05B43]/50"
                  value={simScore}
                  onChange={(e) => setSimScore(e.target.value)}
                />
              </div>
            </div>
            
            <button 
              onClick={handleSimulate}
              disabled={simLoading}
              className="w-full bg-[#4A3B32] text-white py-2 rounded-xl text-sm font-medium hover:bg-[#362A23] transition-colors disabled:opacity-50"
            >
              {simLoading ? "Simulating..." : "Run Simulation"}
            </button>

            {simResult && (
              <div className="mt-6 p-4 bg-[#7A9A74]/20 border border-[#7A9A74]/50 rounded-xl flex items-center justify-between">
                <div>
                  <p className="text-sm text-[#5A7755] font-semibold mb-1">Simulated Outcome</p>
                  <p className="text-xs text-[#5A7755]/80">If these goals are met, risk drops to:</p>
                </div>
                <div className="text-right">
                  <p className="text-xl font-bold text-[#5A7755] uppercase">{simResult.new_risk_level}</p>
                  <p className="text-xs text-[#5A7755]/80">{(simResult.new_risk_probability * 100).toFixed(1)}%</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
