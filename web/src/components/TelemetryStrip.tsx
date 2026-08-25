import React from 'react';
import { Zap, Gauge, Timer, Layers } from 'lucide-react';

interface TelemetryProps {
  ttftMs: number;
  tps: number;
  totalLatencyMs: number;
  totalTokens: number;
}

export const TelemetryStrip: React.FC<TelemetryProps> = ({
  ttftMs,
  tps,
  totalLatencyMs,
  totalTokens
}) => {
  return (
    <div className="grid grid-cols-2 gap-3 p-4 bg-white rounded-2xl border border-slate-200/80 shadow-sm shadow-slate-100">
      {/* TTFT Card */}
      <div className="bg-amber-50/50 p-3.5 rounded-xl border border-amber-200/60">
        <div className="flex items-center justify-between text-slate-600 text-xs mb-1">
          <span className="flex items-center gap-1.5 font-semibold text-amber-900">
            <Zap className="w-3.5 h-3.5 text-amber-600 fill-amber-500/20" /> TTFT
          </span>
          <span className="text-[10px] text-amber-700/80 font-mono">목표 &lt; 450ms</span>
        </div>
        <div className="text-xl font-bold font-mono text-amber-700">
          {ttftMs > 0 ? `${ttftMs.toFixed(0)} ms` : '--'}
        </div>
      </div>

      {/* TPS Card */}
      <div className="bg-emerald-50/50 p-3.5 rounded-xl border border-emerald-200/60">
        <div className="flex items-center justify-between text-slate-600 text-xs mb-1">
          <span className="flex items-center gap-1.5 font-semibold text-emerald-900">
            <Gauge className="w-3.5 h-3.5 text-emerald-600" /> 속도 (TPS)
          </span>
          <span className="text-[10px] text-emerald-700/80 font-mono">Tokens/s</span>
        </div>
        <div className="text-xl font-bold font-mono text-emerald-700">
          {tps > 0 ? `${tps.toFixed(1)}` : '--'}
        </div>
      </div>

      {/* Total Latency */}
      <div className="bg-sky-50/50 p-3.5 rounded-xl border border-sky-200/60">
        <div className="flex items-center justify-between text-slate-600 text-xs mb-1">
          <span className="flex items-center gap-1.5 font-semibold text-sky-900">
            <Timer className="w-3.5 h-3.5 text-[#0080ff]" /> 총 소요 시간
          </span>
          <span className="text-[10px] text-sky-700/80 font-mono">E2E Latency</span>
        </div>
        <div className="text-lg font-bold font-mono text-sky-800">
          {totalLatencyMs > 0 ? `${(totalLatencyMs / 1000).toFixed(2)} s` : '--'}
        </div>
      </div>

      {/* Total Tokens */}
      <div className="bg-indigo-50/50 p-3.5 rounded-xl border border-indigo-200/60">
        <div className="flex items-center justify-between text-slate-600 text-xs mb-1">
          <span className="flex items-center gap-1.5 font-semibold text-indigo-900">
            <Layers className="w-3.5 h-3.5 text-indigo-600" /> 생성 토큰
          </span>
          <span className="text-[10px] text-indigo-700/80 font-mono">Estimated</span>
        </div>
        <div className="text-lg font-bold font-mono text-indigo-800">
          {totalTokens > 0 ? `${totalTokens} 토큰` : '--'}
        </div>
      </div>
    </div>
  );
};
