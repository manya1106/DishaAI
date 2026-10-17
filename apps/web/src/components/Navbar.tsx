"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, ShieldCheck, Activity, Sparkles } from "lucide-react";
import { api } from "../lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let isMounted = true;
    api
      .getHealth()
      .then((h) => {
        if (isMounted) setServerOnline(h.status === "ok");
      })
      .catch(() => {
        if (isMounted) setServerOnline(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-4 sm:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 via-cyan-500 to-indigo-500 flex items-center justify-center p-0.5 shadow-lg shadow-emerald-500/20 group-hover:shadow-emerald-500/40 transition-all">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Compass className="w-5 h-5 text-emerald-400 group-hover:rotate-45 transition-transform duration-300" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-white">
                Disha<span className="text-emerald-400">.ai</span>
              </span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                O3 Trust
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              Verifiable Location Intelligence
            </p>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            href="/explore"
            className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              pathname.startsWith("/explore")
                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                : "text-slate-300 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            Explore Map
          </Link>

          <Link
            href="/trust"
            className={`px-3.5 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5 transition-all ${
              pathname.startsWith("/trust")
                ? "bg-indigo-500/15 text-indigo-400 border border-indigo-500/30"
                : "text-slate-300 hover:text-white hover:bg-slate-800/60"
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <span>Trust & Eval</span>
          </Link>
        </nav>

        {/* Status & Links */}
        <div className="flex items-center gap-3">
          {/* Health Pill */}
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                serverOnline === null
                  ? "bg-amber-400 animate-pulse"
                  : serverOnline
                  ? "bg-emerald-400 shadow-sm shadow-emerald-400"
                  : "bg-rose-500"
              }`}
            />
            <span className="text-slate-400">
              {serverOnline === null
                ? "Checking API..."
                : serverOnline
                ? "API Connected"
                : "API Offline"}
            </span>
          </div>

          <a
            href="https://github.com/manya1106/DishaAI"
            target="_blank"
            rel="noreferrer"
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-800 transition-colors"
            title="GitHub Repository"
          >
            <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
          </a>
        </div>
      </div>
    </header>
  );
}
