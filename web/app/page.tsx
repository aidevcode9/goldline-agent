"use client";

import { useRouter } from "next/navigation";
import { useChat } from "./hooks/useChat";
import ChatPanel from "./components/ChatPanel";
import TracePanel from "./components/TracePanel";
import { LogoIcon, Wordmark } from "./components/Logo";

export default function Home() {
  const router = useRouter();
  const { messages, traceEvents, isLoading, stats, sendMessage, resetChat } = useChat();

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Top Bar */}
      <header className="gradient-border-b flex items-center justify-between bg-zinc-950 px-6 py-3">
        <div className="flex items-center gap-3">
          <LogoIcon size="sm" />
          <Wordmark />
        </div>
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-400 ring-1 ring-amber-500/20">
            Agent Reasoning View
          </span>
          <button
            onClick={handleLogout}
            className="rounded-lg px-2.5 py-1 text-xs text-zinc-500 transition-colors hover:text-zinc-300 hover:bg-zinc-800/50"
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Split Panels */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left: Chat */}
        <div className="flex w-1/2 flex-col border-r border-zinc-800/50">
          <ChatPanel messages={messages} isLoading={isLoading} onSend={sendMessage} onReset={resetChat} />
        </div>

        {/* Right: Trace */}
        <div className="flex w-1/2 flex-col">
          <TracePanel events={traceEvents} stats={stats} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
