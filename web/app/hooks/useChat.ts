"use client";

import { useState, useCallback, useRef } from "react";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface TraceEvent {
  id: string;
  event: string;
  data: Record<string, unknown>;
  timestamp: number;
}

interface UseChatReturn {
  messages: ChatMessage[];
  traceEvents: TraceEvent[];
  isLoading: boolean;
  stats: { latency_ms: number; input_tokens: number; output_tokens: number; tool_calls: number } | null;
  sendMessage: (message: string) => void;
}

const TRACE_EVENTS = new Set(["thinking", "tool_call", "tool_result", "error"]);

const rawUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_URL = rawUrl.endsWith("/") ? rawUrl.slice(0, -1) : rawUrl;

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [traceEvents, setTraceEvents] = useState<TraceEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState<UseChatReturn["stats"]>(null);
  const threadId = useRef<string | null>(null);
  const eventCounter = useRef(0);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (message: string) => {
    // Cancel any in-flight request
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setTraceEvents([]);
    setStats(null);
    eventCounter.current = 0;

    setMessages((prev) => [...prev, { role: "user", content: message }]);

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, thread_id: threadId.current }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error("Stream failed");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let assistantContent = "";
      let eventType = "";
      let dataLines: string[] = [];

      const dispatchEvent = () => {
        if (!eventType || dataLines.length === 0) return;
        const dataStr = dataLines.join("\n");
        try {
          const data = JSON.parse(dataStr);

          if (TRACE_EVENTS.has(eventType)) {
            const traceEvent: TraceEvent = {
              id: `evt-${eventCounter.current++}`,
              event: eventType,
              data,
              timestamp: Date.now(),
            };
            setTraceEvents((prev) => [...prev, traceEvent]);
          }

          if (eventType === "text") {
            assistantContent = data.content;
          } else if (eventType === "done") {
            setStats({
              latency_ms: data.total_latency_ms,
              input_tokens: data.input_tokens,
              output_tokens: data.output_tokens,
              tool_calls: data.tool_calls,
            });
          } else if (eventType === "error") {
            assistantContent = data.message;
          }
        } catch {
          // skip malformed JSON
        }
        eventType = "";
        dataLines = [];
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (controller.signal.aborted) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line === "") {
            dispatchEvent();
          } else if (line.startsWith("event:")) {
            // New event starting — dispatch any pending one first
            dispatchEvent();
            eventType = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            dataLines.push(line.slice(5).trim());
          }
        }
      }

      // Dispatch any remaining event after stream ends
      dispatchEvent();

      if (assistantContent) {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: assistantContent },
        ]);
      }
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Connection error. Is the API server running?" },
      ]);
    } finally {
      if (!controller.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, []);

  return { messages, traceEvents, isLoading, stats, sendMessage };
}
