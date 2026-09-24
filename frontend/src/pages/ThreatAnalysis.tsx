import React, { useState } from "react";
import { threatService } from "../services/api";
import toast, { Toaster } from "react-hot-toast";
import ExplainabilityPanel from "../components/ExplainabilityPanel";

export default function ThreatAnalysis() {
  const [srcIp, setSrcIp] = useState("192.168.1.100");
  const [dstIp, setDstIp] = useState("10.0.0.1");
  const [features, setFeatures] = useState({
    "Flow Duration": 125000,
    "Total Fwd Packets": 8500,
    "Total Backward Packets": 1200,
    "Flow Bytes/s": 3400000,
    "Flow Packets/s": 78000,
    "SYN Flag Count": 15000,
  });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      // ✅ CORRECT: Combine everything into ONE flat object
      const payload = {
        ...features,
        source_ip: srcIp,
        destination_ip: dstIp,
      };

      // threatService.analyze will automatically wrap this in { features: payload }
      const response = await threatService.analyze(payload);
      
      setResult(response.data);
      toast.success("Analysis complete!");
    } catch (error: any) {
      // 🔍 This will print the exact backend error to the console
      console.error("🔴 Backend Error Details:", error.response?.data);
      
      const errorMsg = error.response?.data?.detail || error.response?.data?.features || "Analysis failed";
      toast.error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    } finally {
      setLoading(false);
    }
  };

  const updateFeature = (key: string, value: string) => {
    setFeatures({ ...features, [key]: parseFloat(value) || 0 });
  };

  return (
    <div className="space-y-6 p-6">
      <Toaster position="top-right" />
      
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Analysis</h1>
        <p className="text-gray-400 text-sm mt-1">Manually analyze network traffic with AI</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">Network Traffic Features</h2>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 text-sm mb-2">Source IP</label>
                <input
                  type="text"
                  value={srcIp}
                  onChange={(e) => setSrcIp(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-gray-300 text-sm mb-2">Destination IP</label>
                <input
                  type="text"
                  value={dstIp}
                  onChange={(e) => setDstIp(e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <div className="space-y-3">
              {Object.entries(features).map(([key, value]) => (
                <div key={key}>
                  <label className="block text-gray-300 text-xs mb-1">{key}</label>
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => updateFeature(key, e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
                  />
                </div>
              ))}
            </div>

            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white py-3 rounded-lg font-medium transition-colors"
            >
              {loading ? "Analyzing..." : "🔍 Analyze Traffic"}
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">Analysis Results</h2>
          
          {result ? (
            <div className="space-y-4">
              <div className={`p-4 rounded-lg ${
                result.severity === 'critical' ? 'bg-red-950 border border-red-800' :
                result.severity === 'high' ? 'bg-orange-950 border border-orange-800' :
                result.severity === 'medium' ? 'bg-yellow-950 border border-yellow-800' :
                'bg-green-950 border border-green-800'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-bold text-lg">{result.threat_type || "Unknown Threat"}</span>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    result.severity === 'critical' ? 'bg-red-900 text-red-300' :
                    result.severity === 'high' ? 'bg-orange-900 text-orange-300' :
                    result.severity === 'medium' ? 'bg-yellow-900 text-yellow-300' :
                    'bg-green-900 text-green-300'
                  }`}>
                    {(result.severity || "low").toUpperCase()}
                  </span>
                </div>
                <p className="text-gray-300 text-sm">
                  Confidence: <span className="font-bold text-white">{((result.confidence || 0) * 100).toFixed(2)}%</span>
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-800 p-3 rounded">
                  <p className="text-gray-400 text-xs">Source IP</p>
                  <p className="text-white font-mono">{result.source_ip || srcIp}</p>
                </div>
                <div className="bg-gray-800 p-3 rounded">
                  <p className="text-gray-400 text-xs">Status</p>
                  <p className="text-white">{result.status || "Analyzed"}</p>
                </div>
              </div>

              <ExplainabilityPanel
                shapExplanation={result.shap_explanation}
                limeExplanation={result.lime_explanation}
              />
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p className="text-4xl mb-3">🔍</p>
              <p>Submit network traffic features to analyze</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}