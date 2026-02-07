"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Sparkles, Zap, Clock, Trophy, Target, Eye, Activity, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

const REGIONS = [
  { id: "euw", name: "Europe West", label: "EUW" },
  { id: "eune", name: "Europe Nordic & East", label: "EUNE" },
  { id: "na", name: "North America", label: "NA" },
  { id: "kr", name: "Korea", label: "KR" },
  { id: "br", name: "Brazil", label: "BR" },
  { id: "lan", name: "Latin America North", label: "LAN" },
  { id: "las", name: "Latin America South", label: "LAS" },
  { id: "oce", name: "Oceania", label: "OCE" },
  { id: "tr", name: "Turkey", label: "TR" },
  { id: "ru", name: "Russia", label: "RU" },
  { id: "jp", name: "Japan", label: "JP" },
];

export default function Home() {
  const router = useRouter();
  const [riotId, setRiotId] = useState("");
  const [region, setRegion] = useState("euw");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!riotId.includes("#")) {
      alert("Please use format Name#Tag");
      return;
    }
    setLoading(true);
    const encodedId = encodeURIComponent(riotId);
    router.push(`/summoner/${region}/${encodedId}`);
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-[#05050f] text-white flex flex-col font-sans selection:bg-[#5842F4]/30 relative overflow-hidden">
      {/* Background Mesh */}
      <div className="fixed inset-0 z-0 opacity-40 pointer-events-none bg-mesh"></div>
      <div className="fixed inset-0 z-[-1] opacity-20 pointer-events-none" style={{ backgroundImage: "radial-gradient(#1e293b 1px, transparent 1px)", backgroundSize: "40px 40px" }}></div>

      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b border-white/5 bg-[#05050f]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3 group cursor-pointer" onClick={() => router.push('/')}>
            <div className="w-12 h-12 flex items-center justify-center transition-transform group-hover:scale-105">
              <img src="/logo.png" alt="NexusInsight" className="w-full h-full object-contain" />
            </div>
            <h2 className="text-2xl font-bold tracking-tighter uppercase italic">NEXUS<span className="text-[#5842F4]">INSIGHT</span></h2>
          </div>
          <div className="flex items-center gap-4">
            <button className="hidden md:block text-xs font-bold uppercase tracking-widest px-4 py-2 hover:text-[#5842F4] transition-colors">Login</button>
            <button className="bg-[#5842F4]/10 border border-[#5842F4]/30 text-[#5842F4] text-xs font-bold uppercase tracking-widest px-6 py-2.5 rounded hover:bg-[#5842F4] hover:text-white transition-all duration-300">
              Join Nexus
            </button>
          </div>
        </div>
      </header>

      <div className="relative z-10 flex flex-col items-center pt-20 pb-32 px-4 text-center">

        {/* Main Title Section */}
        <div className="inline-flex items-center gap-2 px-4 py-1 rounded-full bg-white/5 border border-white/10 text-[#00D1FF] text-[10px] font-bold uppercase tracking-[0.3em] mb-8">
          <span className="flex h-2 w-2 rounded-full bg-[#00D1FF] animate-pulse"></span>
          Random Forest Intelligence v4.2
        </div>

        <h1 className="text-5xl md:text-8xl font-black tracking-tighter mb-8 leading-[0.9] uppercase italic max-w-5xl mx-auto">
          Data-Driven <br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00f2ff] to-[#7000ff]">Performance</span>
        </h1>

        <p className="text-slate-400 text-lg md:text-xl max-w-2xl mb-12 font-light mx-auto leading-relaxed">
          Transform your gameplay with neural network analysis. Get precise benchmarks against high-ELO archetypes and master the meta.
        </p>

        {/* Search Bar */}
        <div className="w-full max-w-3xl glass p-1.5 rounded-2xl border border-white/10 shadow-[0_0_30px_rgba(0,242,255,0.15)] mb-12 transform hover:scale-[1.01] transition-all duration-500">
          <form onSubmit={handleSubmit} className="flex flex-col md:flex-row gap-1">
            <div className="relative flex-1 group">
              <Search className="absolute left-5 top-1/2 -translate-y-1/2 text-[#5842F4] w-6 h-6" />
              <input
                className="w-full h-16 bg-white/5 border-none outline-none focus:ring-0 focus:bg-white/10 pl-14 text-white placeholder:text-slate-500 font-bold text-lg rounded-xl transition-all"
                placeholder="SUMMONER NAME #TAG"
                type="text"
                value={riotId}
                onChange={(e) => setRiotId(e.target.value)}
              />
            </div>
            <div className="flex items-center gap-1 bg-white/5 px-2 rounded-xl border border-white/5">
              <select
                className="bg-transparent border-none outline-none text-xs font-bold uppercase tracking-widest text-slate-300 h-full cursor-pointer min-w-[80px]"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              >
                {REGIONS.map((r) => (
                  <option key={r.id} value={r.id} className="bg-[#0a0a0f]">{r.label}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-[#5842F4] text-white h-16 px-10 rounded-xl font-black uppercase tracking-widest hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-3 min-w-[160px]"
            >
              {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <>Analyze <ArrowRight className="w-5 h-5" /></>}
            </button>
          </form>
        </div>

        {/* Popular Profiles */}
        <div className="flex flex-wrap justify-center gap-6 text-slate-500 mb-24">
          <span className="text-[10px] font-black uppercase tracking-widest self-center opacity-50">Popular Profiles:</span>
          <button onClick={() => { setRiotId("Agurin#EUW"); setRegion("euw"); }} className="text-[11px] font-bold uppercase tracking-widest hover:text-[#5842F4] border-b border-transparent hover:border-[#5842F4] transition-all">Agurin#EUW</button>
          <button onClick={() => { setRiotId("Caps#EUW"); setRegion("euw"); }} className="text-[11px] font-bold uppercase tracking-widest hover:text-[#5842F4] border-b border-transparent hover:border-[#5842F4] transition-all">Caps#EUW</button>
          <button onClick={() => { setRiotId("Faker#KR1"); setRegion("kr"); }} className="text-[11px] font-bold uppercase tracking-widest hover:text-[#5842F4] border-b border-transparent hover:border-[#5842F4] transition-all">Faker#KR1</button>
        </div>

        {/* Feature Pillars */}
        <div className="w-full max-w-7xl mx-auto px-6">
          <div className="flex flex-col items-center mb-16 text-center">
            <h2 className="text-xs font-black text-[#00D1FF] uppercase tracking-[0.5em] mb-4">The Analytic Framework</h2>
            <h3 className="text-3xl md:text-5xl font-black tracking-tighter italic uppercase text-white">The Five Pillars of Mastery</h3>
            <div className="w-24 h-1 bg-gradient-to-r from-[#5842F4] to-[#00D1FF] mt-6 rounded-full"></div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {[
              { title: "Combat", icon: Trophy, color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/30", glow: "group-hover:bg-red-500/20", desc: "Lethality metrics, kill participation, and pressure heatmaps." },
              { title: "Economy", icon: Target, color: "text-[#00ffd5]", bg: "bg-[#00ffd5]/10", border: "border-[#00ffd5]/30", glow: "group-hover:bg-[#00ffd5]/20", desc: "Gold efficiency curves and itemization timing analysis." },
              { title: "Vision", icon: Eye, color: "text-[#5842F4]", bg: "bg-[#5842F4]/10", border: "border-[#5842F4]/30", glow: "group-hover:bg-[#5842F4]/20", desc: "Warding patterns, fog-of-war coverage, and predictions." },
              { title: "Objectives", icon: Zap, color: "text-[#00D1FF]", bg: "bg-[#00D1FF]/10", border: "border-[#00D1FF]/30", glow: "group-hover:bg-[#00D1FF]/20", desc: "Neutral priority analysis and tower pressure metrics." },
              { title: "Sync", icon: Activity, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30", glow: "group-hover:bg-emerald-500/20", desc: "Team synergy factors, ping responsiveness scores." }
            ].map((item, i) => (
              <div key={i} className="group relative glass p-8 rounded-3xl hover:border-opacity-50 transition-all duration-500 overflow-hidden text-left border border-white/5">
                <div className={`absolute -right-4 -top-4 w-24 h-24 rounded-full blur-2xl transition-all opacity-0 group-hover:opacity-100 ${item.bg}`}></div>
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-all duration-500 ${item.bg} ${item.border} border ${item.color}`}>
                  <item.icon className="w-7 h-7" />
                </div>
                <h4 className="font-black text-xl uppercase tracking-tight mb-3 italic">{item.title}</h4>
                <p className="text-sm text-slate-400 leading-relaxed font-light">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

    </main>
  );
}
