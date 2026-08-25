import React from 'react';
import { Bot, Sparkles, RefreshCw } from 'lucide-react';

interface HeaderProps {
  agents: Record<string, any>;
  selectedAppId: string;
  onSelectAgent: (appId: string) => void;
  onResetSession: () => void;
  isStreaming: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  agents,
  selectedAppId,
  onSelectAgent,
  onResetSession,
  isStreaming
}) => {
  return (
    <header className="h-16 bg-white/95 backdrop-blur-md border-b border-slate-200/80 px-6 flex items-center justify-between shrink-0 shadow-sm shadow-slate-100 z-10">
      {/* Brand Title */}
      <div className="flex items-center space-x-3.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#0080ff] to-[#38bdf8] flex items-center justify-center shadow-md shadow-blue-500/20 text-white">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="font-bold text-lg text-slate-900 tracking-tight font-['Plus_Jakarta_Sans',sans-serif]">GECX Text Streaming</h1>
            <span className="px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-sky-50 text-[#0080ff] border border-sky-200 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-[#0080ff]" /> SSE Live
            </span>
          </div>
          <p className="text-xs text-slate-500 font-mono">Google Cloud Customer Engagement Suite • Gemini 3.7 Flash</p>
        </div>
      </div>

      {/* Controls & Selectors */}
      <div className="flex items-center space-x-3">
        {/* Agent Switcher */}
        <div className="flex items-center space-x-2 bg-slate-50 px-3.5 py-1.5 rounded-lg border border-slate-200 shadow-inner">
          <label className="text-xs text-slate-500 font-medium">에이전트:</label>
          <select
            value={selectedAppId}
            onChange={(e) => onSelectAgent(e.target.value)}
            disabled={isStreaming}
            className="bg-transparent text-xs text-slate-800 font-semibold focus:outline-none cursor-pointer"
          >
            {Object.entries(agents).map(([id, agent]) => (
              <option key={id} value={id} className="bg-white text-slate-900">
                {agent.displayName || agent.name}
              </option>
            ))}
          </select>
        </div>

        {/* Reset Session Button */}
        <button
          onClick={onResetSession}
          disabled={isStreaming}
          className="p-2 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 hover:text-slate-900 shadow-sm transition-all disabled:opacity-50"
          title="세션 초기화"
        >
          <RefreshCw className={`w-4 h-4 ${isStreaming ? 'animate-spin text-[#0080ff]' : ''}`} />
        </button>
      </div>
    </header>
  );
};
