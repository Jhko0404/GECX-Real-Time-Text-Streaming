import React from 'react';
import { Terminal, CheckCircle2, Loader2, Code2 } from 'lucide-react';

export interface ToolExecution {
  callId: string;
  toolName: string;
  args: any;
  result?: any;
  status: 'executing' | 'completed' | 'failed';
  timestamp: string;
}

interface ToolInspectorProps {
  toolExecutions: ToolExecution[];
  updatedVariables: Record<string, any>;
}

export const ToolInspector: React.FC<ToolInspectorProps> = ({
  toolExecutions,
  updatedVariables
}) => {
  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm shadow-slate-100">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-100 bg-slate-50/80 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-[#0080ff]" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-['Plus_Jakarta_Sans',sans-serif]">Tool Call Inspector</h2>
        </div>
        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-sky-50 text-[#0080ff] border border-sky-200 font-mono font-semibold">
          {toolExecutions.length} Calls
        </span>
      </div>

      {/* Content Stream */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3.5">
        {/* Updated Variables Panel */}
        {Object.keys(updatedVariables).length > 0 && (
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/70">
            <div className="flex items-center space-x-1.5 text-xs font-semibold text-emerald-700 mb-2">
              <Code2 className="w-3.5 h-3.5" />
              <span>Session Updated Variables</span>
            </div>
            <pre className="text-[11px] font-mono bg-white p-3 rounded-lg border border-slate-200 text-slate-800 overflow-x-auto shadow-inner">
              {JSON.stringify(updatedVariables, null, 2)}
            </pre>
          </div>
        )}

        {/* Tool Call Cards */}
        {toolExecutions.length === 0 ? (
          <div className="h-40 flex flex-col items-center justify-center text-slate-400 text-xs">
            <Terminal className="w-8 h-8 mb-2 opacity-30 text-[#0080ff]" />
            <p className="font-medium text-slate-500">실행된 도구(Tool Call)가 없습니다.</p>
            <p className="text-[10px] text-slate-400 mt-1">질문 시 Python 툴이나 조회 API가 자동 트리거됩니다.</p>
          </div>
        ) : (
          toolExecutions.map((tool, idx) => (
            <div
              key={tool.callId || idx}
              className="p-3.5 bg-slate-50/70 rounded-xl border border-slate-200 space-y-2.5 text-xs shadow-sm"
            >
              {/* Tool Card Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2 font-mono font-bold text-slate-900">
                  <Code2 className="w-3.5 h-3.5 text-[#0080ff]" />
                  <span>{tool.toolName}</span>
                </div>
                <div className="flex items-center space-x-1">
                  {tool.status === 'executing' && (
                    <span className="flex items-center gap-1 text-amber-700 text-[10px] bg-amber-50 px-2.5 py-0.5 rounded-full border border-amber-200 font-medium">
                      <Loader2 className="w-3 h-3 animate-spin text-amber-600" /> 실행 중
                    </span>
                  )}
                  {tool.status === 'completed' && (
                    <span className="flex items-center gap-1 text-emerald-700 text-[10px] bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200 font-medium">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" /> 완료
                    </span>
                  )}
                </div>
              </div>

              {/* Arguments JSON */}
              <div>
                <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1">
                  Arguments (입력 인자):
                </div>
                <pre className="text-[11px] font-mono bg-white p-2.5 rounded-lg border border-slate-200 text-slate-800 overflow-x-auto shadow-inner">
                  {JSON.stringify(tool.args, null, 2)}
                </pre>
              </div>

              {/* Response JSON */}
              {tool.result && (
                <div>
                  <div className="text-[10px] font-semibold text-sky-800 uppercase tracking-wider mb-1">
                    Result (반환 결과):
                  </div>
                  <pre className="text-[11px] font-mono bg-white p-2.5 rounded-lg border border-sky-200 text-slate-800 overflow-x-auto shadow-inner">
                    {JSON.stringify(tool.result, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
