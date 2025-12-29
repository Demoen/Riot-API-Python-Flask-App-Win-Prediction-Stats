"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
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
    // Ideally we'd validate existence here, but for now we just push to the dashboard/analysis page
    // We encode the hash to avoid URL issues
    const encodedId = encodeURIComponent(riotId);
    router.push(`/summoner/${region}/${encodedId}`);
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Background Ambience */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-indigo-900/20 via-black to-black z-0 pointer-events-none" />

      <div className="z-10 max-w-lg w-full text-center space-y-8">
        <div className="space-y-2">
          <h1 className="text-5xl font-bold tracking-tighter bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            Riot Win Prediction
          </h1>
          <p className="text-gray-400">
            Advanced ML analysis for your ranked games.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="w-full space-y-4">
          <div className="flex gap-2">
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-3 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            >
              {REGIONS.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>

            <div className="relative flex-1">
              <input
                type="text"
                value={riotId}
                onChange={(e) => setRiotId(e.target.value)}
                placeholder="Riot ID (e.g. Agurin#EUW)"
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-4 pr-10 py-3 text-sm focus:ring-2 focus:ring-indigo-500 outline-none placeholder:text-zinc-600"
              />
              <Search className="absolute right-3 top-3 text-zinc-500 w-5 h-5" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !riotId}
            className={cn(
              "w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-lg transition-all",
              loading && "opacity-50 cursor-not-allowed"
            )}
          >
            {loading ? "Searching..." : "Analyze Profile"}
          </button>
        </form>

        <div className="pt-8 grid grid-cols-3 gap-4 text-center text-sm text-gray-500">
          <div>
            <div className="text-white font-bold text-lg">98%</div>
            <div>Accuracy</div>
          </div>
          <div>
            <div className="text-white font-bold text-lg">150+</div>
            <div>Features</div>
          </div>
          <div>
            <div className="text-white font-bold text-lg">24/7</div>
            <div>Live Analysis</div>
          </div>
        </div>
      </div>
    </main>
  );
}
