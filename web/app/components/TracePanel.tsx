"use client";

import { useEffect, useRef } from "react";
import type { TraceEvent } from "../hooks/useChat";

interface TracePanelProps {
  events: TraceEvent[];
  stats: { latency_ms: number; input_tokens: number; output_tokens: number; tool_calls: number } | null;
  isLoading: boolean;
}

function EventIcon({ event }: { event: string }) {
  const icons: Record<string, string> = {
    thinking: "\u2699",
    tool_call: "\u25B6",
    tool_result: "\u2714",
    text: "\u2709",
    done: "\u2605",
    error: "\u26A0",
  };
  return <span className="text-xs" aria-hidden="true">{icons[event] || "\u2022"}</span>;
}

function EventBadge({ event }: { event: string }) {
  const colors: Record<string, string> = {
    thinking: "bg-blue-500/20 text-blue-400",
    tool_call: "bg-purple-500/20 text-purple-400",
    tool_result: "bg-green-500/20 text-green-400",
    text: "bg-amber-500/20 text-amber-400",
    done: "bg-emerald-500/20 text-emerald-400",
    error: "bg-red-500/20 text-red-400",
  };
  return (
    <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium ${colors[event] || "bg-zinc-700 text-zinc-400"}`}>
      <EventIcon event={event} />
      {event}
    </span>
  );
}

function EventDetail({ event }: { event: TraceEvent }) {
  const data = event.data;

  if (event.event === "thinking") {
    return <p className="text-xs text-zinc-500 italic">{String(data.status)}</p>;
  }

  if (event.event === "tool_call") {
    return (
      <div className="space-y-1">
        <p className="text-xs font-medium text-zinc-300">{String(data.tool)}</p>
        <pre className="overflow-x-auto rounded-md bg-zinc-900 p-2 text-xs text-zinc-400">
          {JSON.stringify(data.input, null, 2)}
        </pre>
      </div>
    );
  }

  if (event.event === "tool_result") {
    return (
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <p className="text-xs font-medium text-zinc-300">{String(data.tool)}</p>
          <span className="text-xs text-zinc-600">{String(data.latency_ms)}ms</span>
        </div>
        <pre className="overflow-x-auto rounded-md bg-zinc-900 p-2 text-xs text-zinc-400 max-h-32 overflow-y-auto">
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
    <div className="flex h-full flex-col bg-zinc-900/50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold text-zinc-100">Agent Reasoning</h2>
          <p className="text-xs text-zinc-500">Real-time trace of AI decision-making</p>
        </div>
        {isLoading && (
          <span className="flex items-center gap-1.5 text-xs text-amber-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-amber-400" />
            Live
          </span>
        )}
      </div>

      {/* Events */}
      <div className="flex-1 overflow-y-auto px-5 py-4">
        {events.length === 0 && !stats && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-3 text-2xl text-zinc-700">{"\u{1F50D}"}</div>
            <p className="text-sm text-zinc-600">Send a message to see the agent&apos;s reasoning process</p>
            <p className="mt-1 text-xs text-zinc-700">Tool calls, SQL queries, and latency will appear here</p>
          </div>
        )}

        <div className="space-y-3">
          {events.map((evt) => (
            <div
              key={evt.id}
              className="animate-fade-in rounded-lg border border-zinc-800 bg-zinc-900/80 p-3"
            >
              <div className="mb-2 flex items-center justify-between">
                <EventBadge event={evt.event} />
                <span className="text-xs tabular-nums text-zinc-600">
                  {new Date(evt.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <EventDetail event={evt} />
            </div>
          ))}
        </div>

        <div ref={bottomRef} />
      </div>

      {/* Stats Footer */}
      {stats && (
        <div className="border-t border-zinc-800 px-5 py-3">
          <div className="grid grid-cols-4 gap-3 text-center">
            <div>
              <p className="text-xs text-zinc-500">Latency</p>
              <p className="text-sm font-medium text-zinc-200">{(stats.latency_ms / 1000).toFixed(1)}s</p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Input</p>
              <p className="text-sm font-medium text-zinc-200">{stats.input_tokens.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Output</p>
              <p className="text-sm font-medium text-zinc-200">{stats.output_tokens.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-xs text-zinc-500">Tools</p>
              <p className="text-sm font-medium text-zinc-200">{stats.tool_calls}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
