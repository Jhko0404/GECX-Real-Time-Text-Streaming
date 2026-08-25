/**
 * SSE Stream Client for GECX text streaming.
 */
export interface SSEEventHandlers {
  onStart?: (data: any) => void;
  onTextChunk?: (delta: string, sequence: number) => void;
  onToolCall?: (toolCall: { call_id: string; tool_name: string; args: any }) => void;
  onToolResponse?: (toolResponse: { call_id: string; tool_name: string; result: any }) => void;
  onUpdatedVariables?: (vars: any) => void;
  onTelemetry?: (telemetry: { ttft_ms: number; tps: number; total_tokens: number; total_latency_ms: number; model: string }) => void;
  onEnd?: () => void;
  onError?: (error: any) => void;
}

export async function sendChatMessageSSE(
  sessionId: string,
  message: string,
  appId: string,
  ticket: string,
  handlers: SSEEventHandlers,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${ticket}`,
      'Accept': 'text/event-stream'
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      app_id: appId
    }),
    signal
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`SSE stream request failed: HTTP ${response.status} - ${errText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('Response body reader is not available');

  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || '';

    for (const block of lines) {
      if (!block.trim()) continue;

      let eventType = 'message';
      let dataJson: any = null;

      const eventLines = block.split('\n');
      for (const line of eventLines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith('data: ')) {
          try {
            dataJson = JSON.parse(line.slice(6));
          } catch (e) {
            dataJson = { raw: line.slice(6) };
          }
        }
      }

      // Dispatch to handlers
      switch (eventType) {
        case 'start':
          handlers.onStart?.(dataJson);
          break;
        case 'text_chunk':
          handlers.onTextChunk?.(dataJson?.delta || '', dataJson?.sequence || 0);
          break;
        case 'tool_call':
          handlers.onToolCall?.(dataJson);
          break;
        case 'tool_response':
          handlers.onToolResponse?.(dataJson);
          break;
        case 'updated_variables':
          handlers.onUpdatedVariables?.(dataJson);
          break;
        case 'telemetry':
          handlers.onTelemetry?.(dataJson);
          break;
        case 'end':
          handlers.onEnd?.();
          break;
        case 'error':
          handlers.onError?.(dataJson);
          break;
      }
    }
  }
}
