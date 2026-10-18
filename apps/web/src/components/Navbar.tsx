"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass } from "lucide-react";
import { api } from "../lib/api";
import { HealthResponse } from "../lib/types";

export default function Navbar() {
  const pathname = usePathname();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthFailed, setHealthFailed] = useState(false);

  useEffect(() => {
    let isMounted = true;
    api
      .getHealth()
      .then((h) => {
        if (isMounted) setHealth(h);
      })
      .catch(() => {
        if (isMounted) setHealthFailed(true);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const isLive = health?.status === "ok";
  const dbLive = health?.db === "configured" || health?.db === "connected";

  return (
    <header className="sticky top-0 z-50 bg-[#F6F1E7]/90 backdrop-blur-sm border-b border-[#15130F]/10 px-4 sm:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-full bg-[#15130F] flex items-center justify-center">
            <Compass className="w-4 h-4 text-[#F6F1E7] group-hover:rotate-45 transition-transform duration-300" />
          </div>
          <div>
            <span
              className="font-medium text-base tracking-tight text-[#15130F]"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Disha AI
            </span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="hidden sm:flex items-center gap-1">
          <Link
            href="/new-analysis"
            className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              pathname.startsWith("/new-analysis")
                ? "bg-[#15130F] text-[#F6F1E7]"
                : "text-[#15130F]/65 hover:text-[#15130F] hover:bg-[#15130F]/5"
            }`}
          >
            New analysis
          </Link>
          <Link
            href="/explore"
            className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              pathname.startsWith("/explore")
                ? "bg-[#15130F] text-[#F6F1E7]"
                : "text-[#15130F]/65 hover:text-[#15130F] hover:bg-[#15130F]/5"
            }`}
          >
            Explore Map
          </Link>
          <Link
            href="/trust"
            className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
              pathname.startsWith("/trust")
                ? "bg-[#15130F] text-[#F6F1E7]"
                : "text-[#15130F]/65 hover:text-[#15130F] hover:bg-[#15130F]/5"
            }`}
          >
            Trust &amp; Eval
          </Link>
        </nav>

        {/* Live system status — a real health-check result, not copy */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full border border-[#15130F]/12 text-xs">
            <span
              className={healthFailed ? "inline-block w-[7px] h-[7px] rounded-full bg-[#8B3A2F]" : isLive ? "live-dot" : "inline-block w-[7px] h-[7px] rounded-full bg-[#A6693B] animate-pulse"}
            />
            <span className="text-[#15130F]/55">
              {healthFailed
                ? "API offline"
                : !health
                ? "Checking API…"
                : `Live · ${health.data_mode === "postgres" ? "Postgres" : health.data_mode}${dbLive ? "" : " (fallback)"}`}
            </span>
          </div>

          <a
            href="https://github.com/manya1106/DishaAI"
            target="_blank"
            rel="noreferrer"
            className="p-2 rounded-full hover:bg-[#15130F]/5 text-[#15130F]/60 hover:text-[#15130F] transition-colors"
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
