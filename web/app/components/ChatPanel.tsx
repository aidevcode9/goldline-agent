"use client";

import { useState, useRef, useEffect } from "react";
import type { ChatMessage } from "../hooks/useChat";
import { LogoIconGhost } from "./Logo";

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

interface ChatPanelProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSend: (message: string) => void;
  onReset: () => void;
}

function isSafeHref(url: string): boolean {
  if (url.startsWith("/")) return true;
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

function renderInline(text: string, keyPrefix: string) {
  // Handle **bold** and *italic*
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/g);
  return parts.map((seg, j) => {
    const boldMatch = seg.match(/^\*\*(.+)\*\*$/);
    if (boldMatch) return <strong key={`${keyPrefix}-${j}`} className="font-semibold">{boldMatch[1]}</strong>;
    const italicMatch = seg.match(/^\*(.+)\*$/);
    if (italicMatch) return <em key={`${keyPrefix}-${j}`}>{italicMatch[1]}</em>;
    return <span key={`${keyPrefix}-${j}`}>{seg}</span>;
  });
}

function renderContent(content: string) {
  const parts = content.split(/(\[[^\]]+\]\([^)]+\))/g);
  return parts.map((part, i) => {
    const match = part.match(/\[([^\]]+)\]\(([^)]+)\)/);
    if (match) {
      const rawHref = match[2];
      if (!isSafeHref(rawHref)) return <span key={i}>{match[1]}</span>;
      const href = rawHref.startsWith("/") ? `${API_URL}${rawHref}` : rawHref;
      return (
        <a key={i} href={href} target="_blank" rel="noopener noreferrer"
           className="inline-flex items-center gap-1 underline text-amber-300 hover:text-amber-200 transition-colors">
          {match[1]}
        </a>
      );
    }
    return <span key={i}>{renderInline(part, String(i))}</span>;
  });
}

export default function ChatPanel({ messages, isLoading, onSend, onReset }: ChatPanelProps) {
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
      <div className="flex items-center gap-3 border-b border-zinc-800/50 px-5 py-4">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-zinc-800/50 ring-1 ring-zinc-700/30">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-zinc-400">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <div className="flex-1">
          <h2 className="text-sm font-semibold text-zinc-100">
            <span className="bg-gradient-to-r from-amber-400 to-amber-500 bg-clip-text text-transparent">Gold</span>
            <span>Line</span>
            {" "}
            <span className="font-normal text-zinc-500">Assistant</span>
          </h2>
          <p className="text-xs text-zinc-500">Office Supplies Support</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={onReset}
            disabled={isLoading}
            className="rounded-lg border border-zinc-700/50 px-3 py-1.5 text-xs text-zinc-400 transition-all hover:border-amber-500/40 hover:text-amber-400 hover:bg-amber-500/5 disabled:opacity-40"
          >
            New Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center animate-slide-up">
            <div className="animate-glow mb-5">
              <LogoIconGhost size="xl" />
            </div>
            <h3 className="text-xl font-semibold text-zinc-200">
              Welcome to{" "}
              <span className="bg-gradient-to-r from-amber-400 to-amber-500 bg-clip-text text-transparent">Gold</span>
              <span>Line</span>
              {" "}Support
            </h3>
            <p className="mt-2 max-w-sm text-sm text-zinc-500 leading-relaxed">
              Ask about products, pricing, stock availability, return policies, or bulk orders.
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-2.5">
              {[
                { label: "Do you have copy paper?", icon: (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                  </svg>
                )},
                { label: "What's your return policy?", icon: (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  </svg>
                )},
                { label: "Show me toner options", icon: (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="6 9 6 2 18 2 18 9" />
                    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
                    <rect x="6" y="14" width="12" height="8" />
                  </svg>
                )},
              ].map(({ label, icon }) => (
                <button
                  key={label}
                  onClick={() => onSend(label)}
                  disabled={isLoading}
                  className="group flex items-center gap-2 rounded-xl border border-zinc-700/50 bg-zinc-800/30 px-4 py-2.5 text-xs text-zinc-400 transition-all hover:border-amber-500/40 hover:text-amber-400 hover:bg-amber-500/5 hover:shadow-lg hover:shadow-amber-500/5 disabled:opacity-40"
                >
                  <span className="shrink-0 transition-transform group-hover:scale-110">{icon}</span>
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-gradient-to-r from-amber-500 to-amber-400 text-zinc-950 shadow-lg shadow-amber-500/15"
                  : "bg-zinc-800/80 text-zinc-200 ring-1 ring-zinc-700/50"
              }`}
            >
              <p className="whitespace-pre-wrap">{renderContent(msg.content)}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="rounded-2xl bg-zinc-800/80 px-4 py-3 ring-1 ring-zinc-700/50">
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
      <form onSubmit={handleSubmit} className="border-t border-zinc-800/50 px-5 py-4">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products, policies, orders..."
            disabled={isLoading}
            className="flex-1 rounded-xl border border-zinc-700/50 bg-zinc-800/50 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 outline-none transition-all focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 focus:bg-zinc-800/80 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 px-5 py-2.5 text-sm font-medium text-zinc-950 shadow-lg shadow-amber-500/20 transition-all hover:shadow-amber-500/30 hover:brightness-110 disabled:opacity-40 disabled:shadow-none"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
