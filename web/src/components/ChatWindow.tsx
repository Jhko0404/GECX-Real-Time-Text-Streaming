import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Sparkles, X, ExternalLink, ZoomIn } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

interface ChatWindowProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isStreaming: boolean;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  isStreaming
}) => {
  const [inputText, setInputText] = useState('');
  const [activeModalImage, setActiveModalImage] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, messages[messages.length - 1]?.content]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isStreaming) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Helper to proxy GCS private bucket image URLs through Cloud Run authenticated proxy
  const normalizeGcsUrl = (url: string): string => {
    if (!url) return '';
    if (url.includes('storage.cloud.google.com') || url.includes('storage.googleapis.com')) {
      return `/api/v1/image-proxy?url=${encodeURIComponent(url)}`;
    }
    return url;
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm shadow-slate-100 relative">
      {/* Image Lightbox Modal */}
      {activeModalImage && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setActiveModalImage(null)}
        >
          <div className="relative max-w-4xl max-h-[90vh] bg-white rounded-2xl p-2 shadow-2xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setActiveModalImage(null)}
              className="absolute top-4 right-4 p-2 rounded-full bg-slate-900/60 hover:bg-slate-900 text-white transition-all shadow-md z-10"
            >
              <X className="w-5 h-5" />
            </button>
            <img
              src={activeModalImage}
              alt="확대 이미지"
              className="max-h-[85vh] w-auto object-contain rounded-xl"
            />
          </div>
        </div>
      )}

      {/* Messages List Area */}
      <div ref={scrollRef} className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8">
            <div className="w-14 h-14 rounded-2xl bg-sky-50 border border-sky-200/60 flex items-center justify-center text-[#0080ff] mb-4 shadow-sm">
              <Sparkles className="w-7 h-7" />
            </div>
            <h3 className="font-bold text-slate-900 text-base mb-1.5 font-['Plus_Jakarta_Sans',sans-serif]">GECX 실시간 텍스트 스트리밍 챗봇</h3>
            <p className="text-xs text-slate-500 max-w-sm mb-5 leading-relaxed">
              질문을 입력하시면 Gemini 3.7 Flash 엔진이 초저지연 토큰 스트리밍 및 이미지 다이어그램으로 즉시 응답합니다.
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {[
                "필터 교체 주기 알려주세요",
                "안녕하세요, 오늘 상담 가능한가요?",
                "상담사 연결해줘"
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => onSendMessage(suggestion)}
                  className="px-3.5 py-1.5 text-xs bg-slate-50 hover:bg-sky-50 border border-slate-200 hover:border-sky-200 text-slate-700 hover:text-[#0080ff] rounded-full transition-all text-left font-medium shadow-2xs"
                >
                  💬 {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3.5 ${
                msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-tr from-[#0080ff] to-[#38bdf8] text-white'
                    : 'bg-gradient-to-tr from-slate-800 to-slate-700 text-white'
                }`}
              >
                {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3.5 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-[#0080ff] text-white rounded-tr-none shadow-md shadow-blue-500/15'
                    : 'bg-slate-50 text-slate-900 rounded-tl-none border border-slate-200/80 shadow-2xs'
                }`}
              >
                {msg.role === 'user' ? (
                  <div className="whitespace-pre-wrap font-['Noto_Sans_KR',sans-serif]">
                    {msg.content}
                  </div>
                ) : (
                  <div className="prose prose-sm max-w-none text-slate-900 leading-relaxed">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        // 1. Image Renderer with GCS Proxy and Lightbox
                        img: ({ node, src, alt, ...props }) => {
                          const proxiedSrc = normalizeGcsUrl(src || '');
                          return (
                            <div className="my-3 group relative inline-block">
                              <img
                                src={proxiedSrc}
                                alt={alt || '다이어그램'}
                                onClick={() => setActiveModalImage(proxiedSrc)}
                                className="rounded-xl border border-slate-200 shadow-sm max-h-72 w-auto object-cover cursor-pointer transition-all group-hover:opacity-95 group-hover:shadow-md"
                                onError={(e) => {
                                  const target = e.currentTarget;
                                  target.onerror = null;
                                  target.style.display = 'none';
                                  const parent = target.parentElement;
                                  if (parent) {
                                    const fallbackDiv = document.createElement('div');
                                    fallbackDiv.className = 'p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-center gap-2';
                                    fallbackDiv.innerHTML = `<span>🖼️ [${alt || '이미지'}]</span> <a href="${proxiedSrc}" target="_blank" rel="noreferrer" class="underline text-blue-600 font-medium flex items-center gap-1">직접 열기</a>`;
                                    parent.appendChild(fallbackDiv);
                                  }
                                }}
                                {...props}
                              />
                              <div
                                onClick={() => setActiveModalImage(proxiedSrc)}
                                className="absolute bottom-2 right-2 p-1.5 rounded-lg bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-all cursor-pointer shadow"
                                title="클릭하여 확대"
                              >
                                <ZoomIn className="w-3.5 h-3.5" />
                              </div>
                            </div>
                          );
                        },
                        // 2. Links
                        a: ({ node, href, children, ...props }) => (
                          <a
                            href={href}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[#0080ff] hover:underline font-medium inline-flex items-center gap-0.5"
                            {...props}
                          >
                            {children} <ExternalLink className="w-3 h-3 inline" />
                          </a>
                        ),
                        // 3. Lists
                        ul: ({ children }) => <ul className="list-disc pl-5 my-2 space-y-1">{children}</ul>,
                        ol: ({ children }) => <ol className="list-decimal pl-5 my-2 space-y-1">{children}</ol>,
                        li: ({ children }) => <li className="text-slate-800 leading-snug">{children}</li>,
                        // 4. Paragraphs
                        p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                        // 5. Strong/Bold
                        strong: ({ children }) => <strong className="font-bold text-slate-950">{children}</strong>
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                    {msg.isStreaming && (
                      <span className="inline-block w-1.5 h-4 ml-1 bg-[#0080ff] animate-pulse align-middle" />
                    )}
                  </div>
                )}
                <div className={`mt-1.5 text-[10px] text-right font-mono ${
                  msg.role === 'user' ? 'text-blue-100/80' : 'text-slate-400'
                }`}>
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Input Bar */}
      <div className="p-4 bg-slate-50/80 border-t border-slate-200/80">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
            rows={1}
            disabled={isStreaming}
            className="w-full bg-white text-slate-900 text-sm placeholder-slate-400 rounded-xl px-4 py-3.5 pr-14 border border-slate-200 focus:outline-none focus:border-[#0080ff] focus:ring-2 focus:ring-sky-100 transition-all resize-none shadow-2xs"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isStreaming}
            className="absolute right-2 p-2 rounded-lg bg-[#0080ff] hover:bg-[#006ee6] disabled:opacity-40 disabled:hover:bg-[#0080ff] text-white transition-all shadow-sm"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
