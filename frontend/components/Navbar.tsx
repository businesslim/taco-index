"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

export function Navbar() {
  const pathname = usePathname();

  return (
    <header className="border-b border-border px-6 py-4">
      <div className="max-w-5xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/logo.png" alt="TACO Index" width={28} height={28} className="invert" />
            <h1 className="text-xl font-bold hidden sm:block">TACO Index</h1>
          </Link>
          <nav className="flex items-center">
            <Link
              href="/"
              className={`px-3 py-2 text-sm transition-colors ${
                pathname === "/"
                  ? "text-slate-100 border-b-2 border-amber-500"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              TACO Index
            </Link>
            <Link
              href="/influencers"
              className={`px-3 py-2 text-sm transition-colors ${
                pathname === "/influencers"
                  ? "text-slate-100 border-b-2 border-amber-500"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <span className="hidden sm:inline">Influencer Indexes</span>
              <span className="sm:hidden">Influencers</span>
            </Link>
          </nav>
        </div>
        <a
          href="https://t.me/TACOIndexBot"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-colors"
          style={{
            backgroundColor: "#F59E0B22",
            color: "#F59E0B",
            border: "1px solid #F59E0B44",
          }}
        >
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
            <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
          </svg>
          <span className="hidden sm:inline">Telegram Bot</span>
        </a>
      </div>
    </header>
  );
}
