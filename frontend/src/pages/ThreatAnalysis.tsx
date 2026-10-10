import { useState } from "react";
import { threatService } from "../services/api";
import toast, { Toaster } from "react-hot-toast";
import ExplainabilityPanel from "../components/ExplainabilityPanel";
import { SAMPLES } from "../data/samples";

const KEY_FEATURES = [
  "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
  "Flow Bytes/s", "Flow Packets/s", "SYN Flag Count",
];

export default function ThreatAnalysis() {
  const [srcIp, setSrcIp] = useState("192.168.1.100");
  const [dstIp, setDstIp] = useState("10.0.0.1");
  const [sampleLabel, setSampleLabel] = useState(SAMPLES[0].label);
  // Full 77-feature record. Editing a key feature changes only that value.
  const [features, setFeatures] = useState<Record<string, number>>({ ...SAMPLES[0].features });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadSample = (label: string) => {
    const s = SAMPLES.find((x) => x.label === label);
    if (!s) return;
    setSampleLabel(label);
    setFeatures({ ...s.features });
    setResult(null);
  };

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      // 🔧 FIX: Clean up feature names to match backend expectations
      // e.g., "Fwd Header Length.1" -> "Fwd Header Length"
      const cleanedFeatures: Record<string, number> = {};
      Object.entries(features).forEach(([key, value]) => {
        const cleanKey = key.replace(/\.1$/, "").trim();
        cleanedFeatures[cleanKey] = value;
      });

      const response = await threatService.analyze({ 
        features: cleanedFeatures, 
        src_ip: srcIp, 
        dst_ip: dstIp 
      });
      
      setResult(response.data);
      toast.success("Analysis complete!");
    } catch (error: any) {
      const d = error.response?.data;
      const msg = d?.detail || (d?.features && JSON.stringify(d.features)) || "Analysis failed";
      toast.error(typeof msg === "string" ? msg : "Check console for details");
    } finally {
      setLoading(false);
    }
  };

  const updateFeature = (key: string, value: string) =>
    setFeatures({ ...features, [key]: parseFloat(value) || 0 });

  const sev = result?.severity || "low";
  const box =
    !result?.is_threat ? "bg-green-950 border border-green-800" :
    sev === "critical" ? "bg-red-950 border border-red-800" :
    sev === "high" ? "bg-orange-950 border border-orange-800" :
    "bg-yellow-950 border border-yellow-800";

  return (
    <div className="space-y-6 p-6">
      <Toaster position="top-right" />
      <div>
        <h1 className="text-2xl font-bold text-white">Threat Analysis</h1>
        <p className="text-gray-400 text-sm mt-1">
          Analyze a network flow record ({Object.keys(features).length} CICIDS2017 features)
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-bold text-white">Flow record</h2>

          <div>
            <label className="block text-gray-300 text-sm mb-2">Load a real sample from the dataset</label>
            <select
              value={sampleLabel}
              onChange={(e) => loadSample(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              {SAMPLES.map((s) => (
                <option key={s.label} value={s.label}>{s.label}</option>
              ))}
            </select>
            <p className="text-gray-500 text-xs mt-1">
              The label is the dataset's ground truth, shown so you can compare it with the model's verdict.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-300 text-sm mb-2">Source IP</label>
              <input value={srcIp} onChange={(e) => setSrcIp(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-gray-300 text-sm mb-2">Destination IP</label>
              <input value={dstIp} onChange={(e) => setDstIp(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500" />
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-gray-400 text-xs">Key features (the other {Object.keys(features).length - KEY_FEATURES.length} stay as loaded)</p>
            {KEY_FEATURES.map((key) => (
              <div key={key}>
                <label className="block text-gray-300 text-xs mb-1">{key}</label>
                <input type="number" value={features[key] ?? 0}
                  onChange={(e) => updateFeature(key, e.target.value)}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500" />
              </div>
            ))}
          </div>

          <button onClick={handleAnalyze} disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white py-3 rounded-lg font-medium transition-colors">
            {loading ? "Analyzing..." : "Analyze traffic"}
          </button>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">Analysis results</h2>
          {result ? (
            <div className="space-y-4">
              <div className={`p-4 rounded-lg ${box}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-white font-bold text-lg">{result.threat_type}</span>
                  <span className="text-xs px-2 py-1 rounded-full font-medium bg-gray-800 text-gray-200">
                    {result.is_threat ? sev.toUpperCase() : "NO THREAT"}
                  </span>
                </div>
                <p className="text-gray-300 text-sm">
                  Attack probability:{" "}
                  <span className="font-bold text-white">{(result.attack_probability * 100).toFixed(2)}%</span>
                </p>
                <p className="text-gray-400 text-xs mt-1">
                  RF {(result.rf_confidence * 100).toFixed(1)}% · XGBoost {(result.xgb_confidence * 100).toFixed(1)}% · threshold {(result.threshold_used * 100).toFixed(0)}%
                </p>
              </div>

              {result.warning && (
                <div className="bg-yellow-950 border border-yellow-800 rounded-lg p-3 text-yellow-300 text-xs">{result.warning}</div>
              )}
              {result.unknown_features?.length > 0 && (
                <div className="bg-yellow-950 border border-yellow-800 rounded-lg p-3 text-yellow-300 text-xs">
                  Ignored unknown features: {result.unknown_features.join(", ")}
                </div>
              )}

              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="bg-gray-800 p-3 rounded">
                  <p className="text-gray-400 text-xs">Source IP</p>
                  <p className="text-white font-mono">{result.source_ip || srcIp}</p>
                </div>
                <div className="bg-gray-800 p-3 rounded">
                  <p className="text-gray-400 text-xs">Recorded</p>
                  <p className="text-white">{result.recorded ? "Threat, alert and incident created" : "Not stored (benign)"}</p>
                </div>
              </div>

              <ExplainabilityPanel shapExplanation={result.shap_explanation} limeExplanation={result.lime_explanation} />
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              <p>Pick a sample and press Analyze.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}