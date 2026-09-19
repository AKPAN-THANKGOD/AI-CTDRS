import React from 'react';

interface SHAPItem { feature: string; shap_value: number; input_value: number; }
interface LIMEItem { feature: string; lime_weight: number; }

interface Props {
  shapExplanation?: SHAPItem[];
  limeExplanation?: LIMEItem[];
}

export default function ExplainabilityPanel({ shapExplanation, limeExplanation }: Props) {
  const hasSHAP = shapExplanation && shapExplanation.length > 0;
  const hasLIME = limeExplanation && limeExplanation.length > 0;
  if (!hasSHAP && !hasLIME) return null;

  return (
    <div className="bg-gray-800 rounded-lg p-4 mt-4 border border-gray-700">
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        🔍 Explainability Analysis (XAI)
        <span className="text-xs bg-blue-900/50 text-blue-400 px-2 py-0.5 rounded-full">Objective 2</span>
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {hasSHAP && (
          <div className="bg-gray-900/50 rounded-lg p-3">
            <h5 className="text-blue-400 text-sm font-medium mb-2">📊 SHAP Feature Contributions</h5>
            <div className="space-y-1.5">
              {shapExplanation.slice(0, 5).map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="text-gray-300 truncate flex-1 mr-2" title={item.feature}>{item.feature}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-700 rounded-full h-1.5">
                      <div className={`h-1.5 rounded-full ${item.shap_value > 0 ? 'bg-red-500' : 'bg-green-500'}`}
                           style={{ width: `${Math.min(Math.abs(item.shap_value) * 30, 100)}%` }} />
                    </div>
                    <span className={`font-mono w-16 text-right ${item.shap_value > 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {item.shap_value > 0 ? '+' : ''}{item.shap_value.toFixed(3)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {hasLIME && (
          <div className="bg-gray-900/50 rounded-lg p-3">
            <h5 className="text-purple-400 text-sm font-medium mb-2">🔬 LIME Local Explanations</h5>
            <div className="space-y-1.5">
              {limeExplanation.slice(0, 5).map((item, idx) => (
                <div key={idx} className="flex items-center justify-between text-xs">
                  <span className="text-gray-300 truncate flex-1 mr-2" title={item.feature}>{item.feature}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 bg-gray-700 rounded-full h-1.5">
                      <div className={`h-1.5 rounded-full ${item.lime_weight > 0 ? 'bg-red-500' : 'bg-green-500'}`}
                           style={{ width: `${Math.min(Math.abs(item.lime_weight) * 30, 100)}%` }} />
                    </div>
                    <span className={`font-mono w-16 text-right ${item.lime_weight > 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {item.lime_weight > 0 ? '+' : ''}{item.lime_weight.toFixed(3)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}