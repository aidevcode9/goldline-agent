"use client";

import { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "../hooks/useChat";

interface ChatPanelProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSend: (message: string) => void;
}

export default function ChatPanel({ messages, isLoading, onSend }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setInput("");
  };

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-zinc-800 px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-500/20 text-amber-400 text-sm font-bold">
          GL
        </div>
        <div>
          <h2 className="text-sm font-semibold text-zinc-100">GoldLine Assistant</h2>
          <p className="text-xs text-zinc-500">Office Supplies Support</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-400 text-2xl font-bold">
              GL
            </div>
            <h3 className="text-lg font-medium text-zinc-300">Welcome to GoldLine Support</h3>
            <p className="mt-2 max-w-sm text-sm text-zinc-500">
              Ask about products, pricing, stock availability, return policies, or bulk orders.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {["Do you have copy paper?", "What's your return policy?", "Show me toner options"].map(
                (q) => (
                  <button
                    key={q}
                    onClick={() => onSend(q)}
                    disabled={isLoading}
                    className="rounded-lg border border-zinc-700 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:border-amber-500/50 hover:text-amber-400 disabled:opacity-40"
                  >
                    {q}
                  </button>
                ),
              )}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-amber-500 text-zinc-950"
                  : "bg-zinc-800 text-zinc-200"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-zinc-800 px-4 py-3">
              <div className="flex gap-1.5">
                <span className="h-2 w-2 animate-bounce rounded-full bg-amber-400 [animation-delay:0ms]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-amber-400 [animation-delay:150ms]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-amber-400 [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-zinc-800 px-5 py-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products, policies, orders..."
            disabled={isLoading}
            className="flex-1 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition-colors focus:border-amber-500/50 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="rounded-xl bg-amber-500 px-5 py-2.5 text-sm font-medium text-zinc-950 transition-colors hover:bg-amber-400 disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
