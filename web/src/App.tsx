import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { ChatWindow, ChatMessage } from './components/ChatWindow';
import { ToolInspector, ToolExecution } from './components/ToolInspector';
import { TelemetryStrip } from './components/TelemetryStrip';
import { AdaptiveTypewriterEngine } from './engine/typewriter';
import { sendChatMessageSSE } from './services/sse_client';

export const App: React.FC = () => {
  const [agents, setAgents] = useState<Record<string, any>>({});
  const [selectedAppId, setSelectedAppId] = useState<string>('');
  const [sessionId, setSessionId] = useState<string>('');
  const [ticket, setTicket] = useState<string>('');
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [toolExecutions, setToolExecutions] = useState<ToolExecution[]>([]);
  const [updatedVariables, setUpdatedVariables] = useState<Record<string, any>>({});

  const [ttftMs, setTtftMs] = useState<number>(0);
  const [tps, setTps] = useState<number>(0);
  const [totalLatencyMs, setTotalLatencyMs] = useState<number>(0);
  const [totalTokens, setTotalTokens] = useState<number>(0);

  const typewriterRef = useRef<AdaptiveTypewriterEngine | null>(null);

  useEffect(() => {
    initSession();
  }, []);

  const initSession = async (appId?: string) => {
    try {
      const res = await fetch('/api/v1/session/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: 'web-cockpit-user', app_id: appId })
      });
      const data = await res.json();
      setSessionId(data.session_id);
      setTicket(data.ticket);
      setSelectedAppId(data.app_id);
      setAgents(data.available_agents || {});
      setMessages([]);
      setToolExecutions([]);
      setUpdatedVariables({});
      setTtftMs(0);
      setTps(0);
      setTotalLatencyMs(0);
      setTotalTokens(0);
    } catch (e) {
      console.error('Session initialization error:', e);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text || isStreaming) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString()
    };

    const assistantMsgId = `assistant-${Date.now()}`;
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toLocaleTimeString(),
      isStreaming: true
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    typewriterRef.current = new AdaptiveTypewriterEngine(
      (renderedText) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantMsgId ? { ...m, content: renderedText } : m))
        );
      },
      () => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantMsgId ? { ...m, isStreaming: false } : m))
        );
      }
    );

    try {
      await sendChatMessageSSE(
        sessionId,
        text,
        selectedAppId,
        ticket,
        {
          onTextChunk: (delta) => {
            typewriterRef.current?.pushChunk(delta);
          },
          onToolCall: (toolCall) => {
            setToolExecutions((prev) => [
              ...prev,
              {
                callId: toolCall.call_id,
                toolName: toolCall.tool_name,
                args: toolCall.args,
                status: 'executing',
                timestamp: new Date().toLocaleTimeString()
              }
            ]);
          },
          onToolResponse: (toolResponse) => {
            setToolExecutions((prev) =>
              prev.map((t) =>
                t.callId === toolResponse.call_id
                  ? { ...t, result: toolResponse.result, status: 'completed' }
                  : t
              )
            );
          },
          onUpdatedVariables: (vars) => {
            setUpdatedVariables((prev) => ({ ...prev, ...vars }));
          },
          onTelemetry: (telemetry) => {
            setTtftMs(telemetry.ttft_ms);
            setTps(telemetry.tps);
            setTotalLatencyMs(telemetry.total_latency_ms);
            setTotalTokens(telemetry.total_tokens);
          },
          onEnd: () => {
            typewriterRef.current?.flush();
            setIsStreaming(false);
          },
          onError: (err) => {
            console.error('Stream error:', err);
            setIsStreaming(false);
          }
        }
      );
    } catch (e) {
      console.error('Chat error:', e);
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#f4f7fb] text-slate-800">
      <Header
        agents={agents}
        selectedAppId={selectedAppId}
        onSelectAgent={(id) => {
          setSelectedAppId(id);
          initSession(id);
        }}
        onResetSession={() => initSession(selectedAppId)}
        isStreaming={isStreaming}
      />

      <main className="flex-1 p-6 grid grid-cols-12 gap-6 overflow-hidden">
        {/* Left Column: Chat Area (7 Cols) */}
        <section className="col-span-7 h-full flex flex-col overflow-hidden">
          <ChatWindow
            messages={messages}
            onSendMessage={handleSendMessage}
            isStreaming={isStreaming}
          />
        </section>

        {/* Right Column: Telemetry & Tool Inspector (5 Cols) */}
        <section className="col-span-5 h-full flex flex-col space-y-4 overflow-hidden">
          <TelemetryStrip
            ttftMs={ttftMs}
            tps={tps}
            totalLatencyMs={totalLatencyMs}
            totalTokens={totalTokens}
          />

          <div className="flex-1 overflow-hidden">
            <ToolInspector
              toolExecutions={toolExecutions}
              updatedVariables={updatedVariables}
            />
          </div>
        </section>
      </main>
    </div>
  );
};
