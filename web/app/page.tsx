"use client";

import { useChat } from "./hooks/useChat";
import ChatPanel from "./components/ChatPanel";
import TracePanel from "./components/TracePanel";

export default function Home() {
  const { messages, traceEvents, isLoading, stats, sendMessage } = useChat();

  return (
    <div className="flex h-screen flex-col">
      {/* Top Bar */}
      <header className="flex items-center justify-between border-b border-zinc-800 bg-zinc-950 px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500 text-xs font-bold text-zinc-950">
            GL
          </div>
          <span className="text-sm font-semibold tracking-tight text-zinc-100">
            GoldLine Office Supplies
          </span>
        </div>
        <span className="rounded-md bg-zinc-800 px-2.5 py-1 text-xs text-zinc-400">
          Agent Reasoning View
        </span>
      </header>

      {/* Split Panels */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Chat */}
        <div className="flex w-1/2 flex-col border-r border-zinc-800">
          <ChatPanel messages={messages} isLoading={isLoading} onSend={sendMessage} />
        </div>

        {/* Right: Trace */}
        <div className="flex w-1/2 flex-col">
          <TracePanel events={traceEvents} stats={stats} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
