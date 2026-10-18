"use client";

import React, { useEffect, useRef, useState } from "react";
import Link from "next/link";

function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: React.ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.15 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={className}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0)" : "translateY(18px)",
        transition: `opacity 0.7s cubic-bezier(0.16,1,0.3,1) ${delay}ms, transform 0.7s cubic-bezier(0.16,1,0.3,1) ${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

/** A duotone H3 hex-grid panel standing in for product imagery — the
 * one place color appears besides the single accent cell. */
function HexDataPanel() {
  return (
    <div
      style={{
        transform: "rotate(-3deg) scale(1.04)",
        marginRight: "-6%",
      }}
    >
      <svg width="100%" height="auto" viewBox="0 0 440 440" role="img" aria-label="Stylised H3 hexagonal scoring grid over Bengaluru">
        <defs>
          <pattern id="hexlines" width="46" height="80" patternUnits="userSpaceOnUse">
            <polygon points="23,2 44,14 44,38 23,50 2,38 2,14" fill="none" stroke="rgba(21,19,15,0.16)" strokeWidth="1" />
            <polygon points="23,40 44,52 44,76 23,88 2,76 2,52" fill="none" stroke="rgba(21,19,15,0.16)" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="440" height="440" fill="url(#hexlines)" />
        <polygon points="138,130 172,149 172,187 138,206 104,187 104,149" fill="#15130F" opacity="0.82" />
        <polygon points="184,168 218,187 218,225 184,244 150,225 150,187" fill="#15130F" opacity="0.5" />
        <polygon points="92,206 126,225 126,263 92,282 58,263 58,225" fill="#15130F" opacity="0.28" />
        <polygon points="230,110 264,129 264,167 230,186 196,167 196,129" fill="#15130F" opacity="0.16" />
        <polygon points="276,187 310,206 310,244 276,263 242,244 242,206" fill="#2F6E4E" opacity="0.92" />
      </svg>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div
      className="min-h-screen flex flex-col bg-[#F6F1E7] text-[#15130F]"
      style={{ fontFamily: "var(--font-geist-sans)" }}
    >
      {/* Header */}
      <header className="px-6 sm:px-14 py-7 sm:py-9">
        <div className="max-w-[1400px] mx-auto flex items-center justify-between">
          <Link
            href="/"
            className="text-base font-medium tracking-tight"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Disha AI
          </Link>

          <nav className="hidden sm:flex items-center gap-10 text-sm text-[#15130F]/60">
            <Link href="/explore" className="hover:text-[#15130F] transition-colors">
              Explore Map
            </Link>
            <Link href="/trust" className="hover:text-[#15130F] transition-colors">
              Trust &amp; Verification
            </Link>
            <a
              href="https://github.com/manya1106/DishaAI"
              target="_blank"
              rel="noreferrer"
              className="hover:text-[#15130F] transition-colors"
            >
              GitHub ↗
            </a>
          </nav>

          <Link href="/new-analysis" className="sm:hidden text-sm underline">
            Explore
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="px-6 sm:px-14 pt-8 sm:pt-16">
        <div className="max-w-[1400px] mx-auto">
          <Reveal>
            <p className="text-[11px] sm:text-xs tracking-[0.2em] uppercase text-[#15130F]/45 mb-7 sm:mb-10">
              Autonomous agent swarm — Bengaluru, India
            </p>

            <h1
              className="leading-[0.98]"
              style={{ fontFamily: "var(--font-display)" }}
            >
              <span className="block font-normal text-[12vw] sm:text-[6vw] tracking-tight">
                Find the right
              </span>
              <span className="block font-semibold text-[13vw] sm:text-[6.6vw] tracking-tight">
                location.
              </span>
              <span className="block font-normal italic text-[9vw] sm:text-[4.4vw] tracking-tight mt-1 sm:mt-2 text-[#15130F]/80">
                Prove every claim.
              </span>
            </h1>
          </Reveal>

          <div className="mt-12 sm:mt-16 grid grid-cols-1 lg:grid-cols-[minmax(0,420px)_1fr] gap-10 lg:gap-16 items-end">
            <Reveal delay={120}>
              <p className="text-[17px] leading-relaxed text-[#15130F]/70">
                Shop owners usually pick locations by gut feel, or AI advice that
                hallucinates plausible-sounding numbers. Disha runs a deterministic
                scoring engine and an agent swarm built to refuse itself the moment a
                claim isn&apos;t grounded in real data.
              </p>

              <div className="mt-8 flex items-center gap-8">
                <Link
                  href="/new-analysis"
                  className="px-6 py-3.5 bg-[#15130F] text-[#F6F1E7] text-sm font-medium hover:bg-[#2A2720] transition-colors"
                >
                  Launch the demo
                </Link>
                <Link
                  href="/trust"
                  className="text-sm font-medium border-b border-[#15130F]/30 hover:border-[#15130F] pb-0.5 transition-colors"
                >
                  Inspect the verifier
                </Link>
              </div>
            </Reveal>

            <Reveal delay={240} className="lg:justify-self-end w-full max-w-[460px]">
              <HexDataPanel />
              <p className="mt-3 text-[11px] tracking-[0.14em] uppercase text-[#15130F]/40">
                H3 res-8 · 1,382 eligible cells, live
              </p>
            </Reveal>
          </div>
        </div>
      </section>

      {/* Stats, set as a sentence rather than a dashboard */}
      <section className="px-6 sm:px-14 py-24 sm:py-36">
        <div className="max-w-[1400px] mx-auto border-t border-[#15130F]/15 pt-14 sm:pt-20">
          <Reveal>
            <p
              className="max-w-4xl text-[28px] sm:text-[42px] leading-[1.25] tracking-tight"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Zero leaked unsupported claims. A hundred percent refusal rate on
              speculative traps. Four agents coordinating on every answer, grounded in
              thirty-six thousand real points of interest across Bengaluru.
            </p>
          </Reveal>
        </div>
      </section>

      {/* Numbered pillars */}
      <section className="px-6 sm:px-14 pb-24 sm:pb-36">
        <div className="max-w-[1400px] mx-auto">
          <Reveal>
            <h2
              className="text-[32px] sm:text-[46px] tracking-tight max-w-xl"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Built so the AI can&apos;t lie to you.
            </h2>
          </Reveal>

          <div className="mt-14 sm:mt-20">
            {[
              {
                n: "01",
                title: "Deterministic scoring",
                body: "Nine signals — competition density, transit access, footfall, daytime population, and more — computed with pure mathematical functions over real OpenStreetMap data. Same input, same output, every time. The model never touches the math.",
              },
              {
                n: "02",
                title: "A swarm that polices itself",
                body: "A Narrator Agent drafts an explanation from the computed evidence. A Verifier Agent checks every sentence against it before anything reaches you — and the hand-off between them is something you can actually inspect.",
              },
              {
                n: "03",
                title: "Honest about its limits",
                body: "We never fabricate rupee rents or footfall counts. Rent is shown as an honest heuristic tier, clearly labelled — not a number invented to sound precise.",
              },
            ].map((pillar, i) => (
              <Reveal key={pillar.n} delay={i * 90}>
                <div className="grid grid-cols-[64px_1fr] sm:grid-cols-[120px_1fr_1.3fr] gap-6 sm:gap-10 py-9 sm:py-11 border-t border-[#15130F]/15 items-baseline">
                  <div
                    className="text-2xl sm:text-3xl text-[#15130F]/35"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {pillar.n}
                  </div>
                  <div
                    className="text-lg sm:text-xl font-medium sm:col-span-1"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    {pillar.title}
                  </div>
                  <p className="col-span-2 sm:col-span-1 text-[15px] leading-relaxed text-[#15130F]/65">
                    {pillar.body}
                  </p>
                </div>
              </Reveal>
            ))}
            <div className="border-t border-[#15130F]/15" />
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="bg-[#15130F] text-[#F6F1E7] px-6 sm:px-14 py-24 sm:py-32">
        <Reveal>
          <div className="max-w-[1400px] mx-auto flex flex-col sm:flex-row sm:items-end justify-between gap-10">
            <h2
              className="text-[36px] sm:text-[56px] leading-[1.05] tracking-tight max-w-2xl"
              style={{ fontFamily: "var(--font-display)" }}
            >
              See the swarm verify itself, live.
            </h2>
            <Link
              href="/new-analysis"
              className="shrink-0 px-6 py-3.5 bg-[#F6F1E7] text-[#15130F] text-sm font-medium hover:bg-white transition-colors self-start sm:self-end"
            >
              Launch Bengaluru demo
            </Link>
          </div>
        </Reveal>
      </section>

      {/* Footer */}
      <footer className="mt-auto px-6 sm:px-14 py-8 text-xs text-[#15130F]/45 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <p>© 2026 Disha AI — open-source location intelligence, MIT License.</p>
        <p>Data © OpenStreetMap contributors</p>
      </footer>
    </div>
  );
}
