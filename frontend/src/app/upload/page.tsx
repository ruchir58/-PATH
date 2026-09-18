"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle, AlertCircle, FileText, Settings, Play } from "lucide-react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [targetCol, setTargetCol] = useState("");
  const [trainingMetrics, setTrainingMetrics] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      // 1. Upload
      const res = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/upload`, formData);
      const dsId = res.data.id;
      setDatasetId(dsId);
      
      // 2. Inspect
      const reportRes = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${dsId}/inspect`);
      const reportData = reportRes.data;
      setReport(reportData);
      
      // 3. Auto-detect target column (look for risk, support, pass, or use last column)
      let target = "";
      for (const col of reportData.columns_detected) {
        const lower = col.toLowerCase();
        if (lower.includes("risk") || lower.includes("support") || lower.includes("target") || lower.includes("pass") || lower.includes("grade")) {
          target = col;
          break;
        }
      }
      if (!target && reportData.columns_detected.length > 0) {
        target = reportData.columns_detected[reportData.columns_detected.length - 1]; // Fallback to last column
      }
      setTargetCol(target);
      
      // 4. Auto-clean and Train
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${dsId}/clean`);
      const trainRes = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${dsId}/train`, { target_col: target });
      setTrainingMetrics(trainRes.data);
      
      // 5. Predict
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'}/datasets/${dsId}/predict`);
      
    } catch (err: any) {
      console.error(err);
      alert("Process failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h2 className="text-2xl font-bold text-[#4A3B32]">Dataset Upload</h2>
        <p className="text-sm text-[#4A3B32]/70">Upload CSV or Excel data to analyze student risk.</p>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-sm border border-[#D3B89B]/30 text-center">
        <UploadCloud size={48} className="mx-auto text-[#C05B43] mb-4" />
        <h3 className="text-lg font-semibold text-[#4A3B32] mb-2">Upload your dataset</h3>
        <p className="text-sm text-[#4A3B32]/60 mb-6">Supports .csv, .xls, .xlsx</p>
        
        <div className="flex flex-col items-center space-y-4">
          <input 
            type="file" 
            accept=".csv, .xlsx, .xls" 
            onChange={handleFileChange}
            className="block w-full max-w-xs text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-[#D3B89B]/20 file:text-[#4A3B32]
              hover:file:bg-[#D3B89B]/40"
          />
          <button 
            onClick={handleUpload} 
            disabled={!file || loading}
            className="bg-[#C05B43] text-white px-6 py-2 rounded-xl font-medium hover:bg-[#A84A34] transition-colors disabled:opacity-50"
          >
            {loading ? "Processing..." : "Upload & Train Model"}
          </button>
        </div>
      </div>

      {report && (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30 space-y-6">
          <h3 className="text-lg font-semibold text-[#4A3B32] flex items-center gap-2">
            <FileText size={20} /> Data Quality Report
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#F5F5DC]/50 p-4 rounded-xl">
              <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider">Total Rows</p>
              <p className="text-xl font-bold text-[#4A3B32]">{report.total_rows}</p>
            </div>
            <div className="bg-[#F5F5DC]/50 p-4 rounded-xl">
              <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider">Missing Values</p>
              <p className="text-xl font-bold text-[#C05B43]">{Object.values(report.missing_values).reduce((a: any,b: any) => a+b, 0) as number}</p>
            </div>
            <div className="bg-[#F5F5DC]/50 p-4 rounded-xl">
              <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider">Duplicate Rows</p>
              <p className="text-xl font-bold text-[#C05B43]">{report.duplicate_rows}</p>
            </div>
            <div className="bg-[#F5F5DC]/50 p-4 rounded-xl">
              <p className="text-xs text-[#4A3B32]/60 uppercase tracking-wider">Invalid Attendance</p>
              <p className="text-xl font-bold text-[#C05B43]">{report.invalid_attendance_count}</p>
            </div>
          </div>
        </div>
      )}

      {trainingMetrics && (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-[#D3B89B]/30">
          <h3 className="text-lg font-semibold text-[#4A3B32] flex items-center gap-2 mb-4">
            <CheckCircle size={20} className="text-green-600" /> Model Selected: {trainingMetrics.best_model}
          </h3>
          <p className="text-sm text-[#4A3B32]/70 mb-4">The dataset was cleaned and features were dynamically engineered. The best model was selected based on F1-score and Accuracy.</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(trainingMetrics.metrics[trainingMetrics.best_model]).map(([k, v]: [string, any]) => {
              if (typeof v === 'number') {
                return (
                  <div key={k} className="bg-green-50 p-4 rounded-xl border border-green-100">
                    <p className="text-xs text-green-700 uppercase tracking-wider">{k.replace('_', ' ')}</p>
                    <p className="text-xl font-bold text-green-900">{(v * 100).toFixed(1)}%</p>
                  </div>
                )
              }
              return null;
            })}
          </div>
        </div>
      )}
    </div>
  );
}
