"use client";

import { useEffect, useRef, type ReactNode } from "react";
import type { TraceEvent } from "../hooks/useChat";

interface TracePanelProps {
  events: TraceEvent[];
  stats: { latency_ms: number; input_tokens: number; output_tokens: number; tool_calls: number } | null;
  isLoading: boolean;
}

/* ── SVG Icons (12×12, stroke-based) ── */

function IconThinking() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
    </svg>
  );
}

function IconPlay() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none">
      <path d="M6 4l15 8-15 8V4z" />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 12l6 6L20 6" />
    </svg>
  );
}

function IconMessage() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    </svg>
  );
}

function IconStar() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none">
      <path d="M12 2l3.09 6.26L22 9.27l-5 4.87L18.18 22 12 18.27 5.82 22 7 14.14l-5-4.87 6.91-1.01L12 2z" />
    </svg>
  );
}

function IconAlert() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}

function IconDot() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
      <circle cx="12" cy="12" r="4" />
    </svg>
  );
}

function IconGear() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-600">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
    </svg>
  );
}

const EVENT_CONFIG: Record<string, { icon: ReactNode; color: string; border: string; label: string }> = {
  thinking: { icon: <IconThinking />, color: "bg-blue-500/15 text-blue-400", border: "border-l-blue-500", label: "Thinking" },
  tool_call: { icon: <IconPlay />, color: "bg-purple-500/15 text-purple-400", border: "border-l-purple-500", label: "Tool Call" },
  tool_result: { icon: <IconCheck />, color: "bg-emerald-500/15 text-emerald-400", border: "border-l-emerald-500", label: "Result" },
  text: { icon: <IconMessage />, color: "bg-amber-500/15 text-amber-400", border: "border-l-amber-500", label: "Response" },
  done: { icon: <IconStar />, color: "bg-emerald-500/15 text-emerald-400", border: "border-l-emerald-500", label: "Done" },
  error: { icon: <IconAlert />, color: "bg-red-500/15 text-red-400", border: "border-l-red-500", label: "Error" },
};

const DEFAULT_CONFIG = { icon: <IconDot />, color: "bg-zinc-700/50 text-zinc-400", border: "border-l-zinc-600", label: "Event" };

function EventDetail({ event }: { event: TraceEvent }) {
  const data = event.data;

  if (event.event === "thinking") {
    return <p className="text-xs text-zinc-500 italic">{String(data.status)}</p>;
  }

  if (event.event === "tool_call") {
    return (
      <div className="space-y-1.5">
        <p className="text-xs font-semibold text-zinc-200">{String(data.tool)}</p>
        <pre className="overflow-x-auto rounded-lg bg-zinc-950/50 p-2.5 text-xs text-zinc-400 ring-1 ring-zinc-800/50">
          {JSON.stringify(data.input, null, 2)}
        </pre>
      </div>
    );
  }

  if (event.event === "tool_result") {
    return (
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <p className="text-xs font-semibold text-zinc-200">{String(data.tool)}</p>
          <span className="rounded-full bg-zinc-800/80 px-2 py-0.5 text-[10px] tabular-nums text-zinc-500">
            {String(data.latency_ms)}ms
          </span>
        </div>
        <pre className="overflow-x-auto rounded-lg bg-zinc-950/50 p-2.5 text-xs text-zinc-400 max-h-32 overflow-y-auto ring-1 ring-zinc-800/50">
          {typeof data.result === "string" ? data.result : JSON.stringify(data.result, null, 2)}
        </pre>
      </div>
    );
  }

  if (event.event === "error") {
    return <p className="text-xs text-red-400">{String(data.message)}</p>;
  }

  return null;
}

export default function TracePanel({ events, stats, isLoading }: TracePanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  return (
    <div className="flex h-full flex-col bg-zinc-900/30">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800/50 px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-zinc-100">Agent Reasoning</h2>
          <p className="text-xs text-zinc-500">Real-time trace of AI decision-making</p>
        </div>
        {isLoading && (
          <span className="flex items-center gap-2 rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400 ring-1 ring-amber-500/20">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-400" />
            </span>
            Live
          </span>
        )}
      </div>

      {/* Events */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        {events.length === 0 && !stats && (
          <div className="flex h-full flex-col items-center justify-center text-center animate-slide-up">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-800/50 ring-1 ring-zinc-700/50">
              <IconGear />
            </div>
            <p className="text-sm text-zinc-500">Send a message to see the agent&apos;s reasoning process</p>
            <p className="mt-1.5 text-xs text-zinc-600">Tool calls, SQL queries, and latency will appear here</p>
          </div>
        )}

        <div className="space-y-2.5">
          {events.map((evt) => {
            const config = EVENT_CONFIG[evt.event] || DEFAULT_CONFIG;
            return (
              <div
                key={evt.id}
                className={`animate-fade-in rounded-xl border-l-2 ${config.border} bg-zinc-800/30 p-3.5 ring-1 ring-zinc-800/40`}
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className={`inline-flex items-center gap-1.5 rounded-lg px-2 py-0.5 text-xs font-medium ${config.color}`}>
                    <span aria-hidden="true">{config.icon}</span>
                    {config.label}
                  </span>
                  <span className="text-[10px] tabular-nums text-zinc-600">
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <EventDetail event={evt} />
              </div>
            );
          })}
        </div>

        <div ref={bottomRef} />
      </div>

      {/* Stats Footer */}
      {stats && (
        <div className="border-t border-zinc-800/50 px-5 py-3">
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: "Latency", value: `${(stats.latency_ms / 1000).toFixed(1)}s`, color: "text-amber-400" },
              { label: "Input", value: stats.input_tokens.toLocaleString(), color: "text-blue-400" },
              { label: "Output", value: stats.output_tokens.toLocaleString(), color: "text-purple-400" },
              { label: "Tools", value: String(stats.tool_calls), color: "text-emerald-400" },
            ].map(({ label, value, color }) => (
              <div key={label} className="text-center">
                <p className="text-[10px] uppercase tracking-wider text-zinc-600">{label}</p>
                <p className={`text-sm font-semibold tabular-nums ${color}`}>{value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
