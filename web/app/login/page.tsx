"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { LogoIcon, Wordmark } from "../components/Logo";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passcode, setPasscode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, passcode }),
      });

      if (res.ok) {
        router.push("/");
        router.refresh();
      } else {
        const data = await res.json();
        setError(data.error || "Invalid credentials");
      }
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex min-h-screen overflow-hidden">
      {/* Background ambient washes */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-40 top-0 h-[600px] w-[600px] rounded-full bg-amber-500/8 blur-[150px]" />
        <div className="absolute right-0 top-1/4 h-[500px] w-[500px] rounded-full bg-amber-600/5 blur-[130px]" />
        <div className="absolute left-1/3 bottom-0 h-[400px] w-[400px] rounded-full bg-orange-500/5 blur-[120px]" />
      </div>

      {/* Left: Hero / Branding */}
      <div className="relative hidden w-1/2 flex-col justify-between p-12 lg:flex xl:p-16">
        <div className="flex items-center gap-3">
          <LogoIcon size="lg" />
          <Wordmark />
        </div>

        <div className="max-w-lg">
          <h1 className="text-5xl font-bold leading-[1.1] tracking-tight text-zinc-100 xl:text-6xl">
            AI-powered support,{" "}
            <span className="bg-gradient-to-r from-amber-400 via-orange-400 to-amber-500 bg-clip-text text-transparent">
              instantly.
            </span>
          </h1>
          <p className="mt-5 text-lg leading-relaxed text-zinc-400">
            Watch our AI agent reason through product queries, search inventory, and generate quotes in real time.
          </p>

          {/* Feature highlights */}
          <div className="mt-10 space-y-4">
            {[
              { title: "Agent Reasoning View", desc: "See every tool call, SQL query, and decision as it happens" },
              { title: "215+ Product Catalog", desc: "Real inventory with live search, pricing, and availability" },
              { title: "Instant PDF Quotes", desc: "AI-generated branded quotes ready to download" },
            ].map(({ title, desc }) => (
              <div key={title} className="flex items-start gap-3">
                <div className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-500/15 text-amber-400">
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-zinc-200">{title}</p>
                  <p className="text-sm text-zinc-500">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div />
      </div>

      {/* Right: Login Form */}
      <div className="relative flex w-full items-center justify-center px-6 lg:w-1/2 lg:border-l lg:border-zinc-800/50">
        {/* Subtle surface tint */}
        <div className="pointer-events-none absolute inset-0 bg-zinc-900/30" />

        <div className="relative w-full max-w-sm animate-slide-up">
          {/* Mobile logo — hidden on desktop */}
          <div className="mb-8 flex flex-col items-center gap-3 lg:hidden">
            <LogoIcon size="lg" />
            <Wordmark className="text-lg" />
          </div>

          <div className="mb-8 lg:mb-10">
            <h2 className="text-2xl font-semibold tracking-tight text-zinc-100">
              Welcome back
            </h2>
            <p className="mt-1.5 text-sm text-zinc-500">Sign in to access the AI agent demo</p>
          </div>

          {/* Form Card */}
          <div className="glass-card rounded-2xl p-6">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="email" className="mb-1.5 block text-xs font-medium text-zinc-400">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-xl border border-zinc-700/50 bg-zinc-800/50 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 outline-none transition-all focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 focus:bg-zinc-800/80"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label htmlFor="password" className="mb-1.5 block text-xs font-medium text-zinc-400">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-xl border border-zinc-700/50 bg-zinc-800/50 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 outline-none transition-all focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 focus:bg-zinc-800/80"
                  placeholder="Enter password"
                />
              </div>

              <div>
                <label htmlFor="passcode" className="mb-1.5 block text-xs font-medium text-zinc-400">
                  Passcode
                </label>
                <input
                  id="passcode"
                  type="text"
                  required
                  value={passcode}
                  onChange={(e) => setPasscode(e.target.value)}
                  className="w-full rounded-xl border border-zinc-700/50 bg-zinc-800/50 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 outline-none transition-all focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 focus:bg-zinc-800/80"
                  placeholder="Enter access code"
                />
              </div>

              {error && (
                <div className="rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-2.5 text-sm text-red-400">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 px-4 py-2.5 text-sm font-semibold text-zinc-950 shadow-lg shadow-amber-500/20 transition-all hover:shadow-amber-500/30 hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
              >
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
