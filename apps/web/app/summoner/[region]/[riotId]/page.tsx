"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { analyzeStats } from "@/lib/api";
import {
    ArrowLeft, Trophy, Skull, Crown, Flame, HeartCrack, Umbrella,
    Baby, UserX, Swords, Castle, Wheat, Eye, EyeOff, Coins, Shield, Target,
    Sword, Banknote, HelpCircle, HeartHandshake, Ghost, Users, MoveHorizontal,
    TrendingDown, Frown, Sparkles, Hand, HeartPulse, Bot, Gamepad2,
    ChartLine, Crosshair, Trees, Activity, MessageCircle, BarChart3,
    Zap, Heart, Timer, Layers, Map, Compass, TrendingUp
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

// Map icon names from backend to Lucide components
const iconMap: Record<string, React.ElementType> = {
    "crown": Crown,
    "flame": Flame,
    "skull": Skull,
    "heart-crack": HeartCrack,
    "umbrella": Umbrella,
    "baby": Baby,
    "user-x": UserX,
    "swords": Swords,
    "castle": Castle,
    "wheat": Wheat,
    "eye": Eye,
    "eye-off": EyeOff,
    "coins": Coins,
    "shield": Shield,
    "target": Target,
    "sword": Sword,
    "banknote": Banknote,
    "help-circle": HelpCircle,
    "heart-handshake": HeartHandshake,
    "ghost": Ghost,
    "users": Users,
    "move-horizontal": MoveHorizontal,
    "trending-down": TrendingDown,
    "frown": Frown,
    "sparkles": Sparkles,
    "hand": Hand,
    "heart-pulse": HeartPulse,
    "bot": Bot,
};

interface Mood {
    title: string;
    icon: string;
    color: string;
    description: string;
    advice: string;
}

// Stat Card Component
function StatCard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon?: React.ElementType; color?: string }) {
    return (
        <div className="bg-black/40 p-4 rounded-xl border border-zinc-800/50 hover:border-zinc-700/50 transition-all hover:-translate-y-0.5">
            <div className="flex items-center gap-2 text-zinc-400 text-sm mb-1">
                {Icon && <Icon className="w-4 h-4" />}
                {label}
            </div>
            <div className={cn("text-xl font-bold", color || "text-white")}>{value}</div>
        </div>
    );
}

// Feature List Item Component
function FeatureItem({ name, value, valueColor }: { name: string; value: string | number; valueColor?: string }) {
    return (
        <li className="flex justify-between items-center py-2 border-b border-zinc-800/30 last:border-0">
            <span className="text-zinc-400 text-sm">{name}</span>
            <span className={cn("font-semibold", valueColor || "text-white")}>{value}</span>
        </li>
    );
}

// Detailed Card Section
function DetailCard({ title, icon: Icon, iconColor, children }: { title: string; icon: React.ElementType; iconColor: string; children: React.ReactNode }) {
    return (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Icon className={cn("w-5 h-5", iconColor)} />
                {title}
            </h3>
            <ul className="space-y-0">{children}</ul>
        </div>
    );
}

// Progress Bar Component
function ProgressBar({ value, color }: { value: number; color: string }) {
    return (
        <div className="w-full h-8 bg-zinc-800 rounded-full overflow-hidden relative">
            <div
                className={cn("h-full rounded-full transition-all duration-1000 flex items-center justify-end pr-3", color)}
                style={{ width: `${Math.max(value, 5)}%` }}
            >
                <span className="text-white font-bold text-sm">{value.toFixed(1)}%</span>
            </div>
        </div>
    );
}

export default function Dashboard() {
    const params = useParams();
    const region = params.region as string;
    const riotId = decodeURIComponent(params.riotId as string);

    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [progress, setProgress] = useState({ message: "Initializing...", percent: 0 });
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const result = await analyzeStats(riotId, region, (p) => {
                    setProgress(p);
                });
                setData(result);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }
        if (riotId && region) fetchData();
    }, [riotId, region]);

    if (loading) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
                <div className="flex flex-col items-center gap-6 w-full max-w-md">
                    <div className="w-20 h-20 relative">
                        {/* Outer Spinner */}
                        <div className="absolute inset-0 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
                        {/* Inner Spinner */}
                        <div className="absolute inset-4 border-4 border-purple-500/30 border-b-purple-500 rounded-full animate-spin" style={{ animationDuration: '1.5s', animationDirection: 'reverse' }} />
                        {/* Center Icon */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Gamepad2 className="w-6 h-6 text-white/50 animate-pulse" />
                        </div>
                    </div>

                    <div className="w-full space-y-2">
                        <div className="flex justify-between text-xs text-zinc-400 uppercase tracking-wider font-semibold">
                            <span>{progress.message}</span>
                            <span>{progress.percent}%</span>
                        </div>
                        <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 transition-all duration-300 ease-out"
                                style={{ width: `${progress.percent}%` }}
                            />
                        </div>
                    </div>

                    <p className="text-zinc-600 text-sm text-center animate-pulse max-w-xs">
                        {progress.percent < 20 && "Connecting to Riot API..."}
                        {progress.percent >= 20 && progress.percent < 80 && "Analyzing recent match performance..."}
                        {progress.percent >= 80 && "Finalizing Win Prediction..."}
                    </p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center">
                <div className="text-center space-y-4">
                    <Skull className="w-16 h-16 text-red-500 mx-auto" />
                    <h2 className="text-2xl font-bold">Analysis Failed</h2>
                    <p className="text-zinc-500">{error}</p>
                    <Link href="/" className="inline-block text-indigo-400 hover:text-indigo-300">&larr; Try again</Link>
                </div>
            </div>
        );
    }

    const {
        user,
        metrics,
        win_probability,
        player_moods = [],
        weighted_averages = {},
        last_match_stats = {},
        win_rate = 0,
        total_matches = 0,
        territory_metrics = {},
        ddragon_version = "14.24.1"
    } = data;

    const { top_differentiators = [], category_importance = [] } = metrics || {};
    const avg = weighted_averages;
    const lastMatch = last_match_stats; // For Predictive Indicators section

    // Helper for formatting numbers
    const fmt = (val: number | undefined, decimals = 1) => val !== undefined ? val.toFixed(decimals) : "0";
    const fmtPct = (val: number | undefined) => val !== undefined ? (val * 100).toFixed(1) + "%" : "0%";
    const fmtSigned = (val: number | undefined) => val !== undefined ? (val >= 0 ? "+" : "") + val.toFixed(1) : "0";

    // Profile icon URL
    const profileIconUrl = user.profile_icon_id
        ? `https://ddragon.leagueoflegends.com/cdn/${ddragon_version}/img/profileicon/${user.profile_icon_id}.png`
        : null;

    return (
        <div className="min-h-screen bg-black text-white">
            {/* Animated Background */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }} />
            </div>

            <div className="relative z-10 p-4 md:p-8 max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <header className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 animate-in fade-in slide-in-from-top duration-500">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="p-2 rounded-full hover:bg-zinc-800 transition-colors">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        {profileIconUrl && (
                            <img
                                src={profileIconUrl}
                                alt="Profile Icon"
                                className="w-20 h-20 rounded-2xl border-2 border-indigo-500 shadow-lg shadow-indigo-500/20"
                            />
                        )}
                        <div>
                            <h1 className="text-3xl font-bold">
                                <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                                    {user.game_name}
                                </span>
                                <span className="text-zinc-500">#{user.tag_line}</span>
                            </h1>
                            <div className="text-sm text-zinc-500 flex items-center gap-2 mt-1">
                                <span className="uppercase font-medium">{user.region}</span>
                                <span>•</span>
                                <span>Level {user.summoner_level}</span>
                                <span>•</span>
                                <Gamepad2 className="w-4 h-4" />
                                <span>{total_matches} Matches Analyzed</span>
                            </div>
                        </div>
                    </div>

                    {/* Vibe Badges (Moved from section below) */}
                    <div className="flex flex-wrap items-center gap-2 md:justify-end mt-4 md:mt-0">
                        {player_moods.slice(0, 3).map((mood: Mood, idx: number) => {
                            const IconComponent = iconMap[mood.icon] || Bot;
                            return (
                                <div key={idx} className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${mood.color.replace('text-', 'border-')} bg-black/40 border-opacity-30 hover:bg-opacity-40 cursor-help transition-all`} title={`${mood.description}\n\n"${mood.advice}"`}>
                                    <IconComponent className={cn("w-4 h-4", mood.color)} />
                                    <span className={cn("text-xs font-bold", mood.color)}>{mood.title}</span>
                                </div>
                            );
                        })}
                    </div>
                </header>

                {/* Win Probability Card */}
                <section className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "100ms" }}>
                    <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-yellow-500" />
                        Win Probability (Next Game)
                    </h3>
                    <ProgressBar value={win_probability} color={win_probability >= 50 ? "bg-gradient-to-r from-green-600 to-emerald-500" : "bg-gradient-to-r from-red-600 to-rose-500"} />
                    <p className="text-zinc-500 text-sm mt-3 flex items-center gap-2">
                        <ChartLine className="w-4 h-4 text-indigo-400" />
                        <strong>Prediction</strong> based on early game leads, not outcome-correlated stats.
                    </p>
                </section>

                {/* Predictive Indicators - What the ML Model Actually Uses */}
                <section className="bg-gradient-to-br from-amber-900/20 to-orange-900/20 border border-amber-500/20 rounded-xl p-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "125ms" }}>
                    <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-amber-400" />
                        Predictive Indicators
                        <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-1 rounded-full ml-2">
                            🧠 Last Game: {lastMatch.championName} • {fmt(lastMatch.kda)} KDA
                        </span>
                    </h3>
                    <p className="text-zinc-500 text-sm mb-4">Your most recent game stats - these features predict win probability</p>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                        {/* Early Game Leads */}
                        <div className="bg-black/40 rounded-xl p-4 border border-amber-500/10">
                            <h4 className="font-semibold text-amber-400 mb-3 flex items-center gap-2">
                                <Zap className="w-4 h-4" />
                                Early Game Leads
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Gold/XP @8min</span>
                                    <span className={cn("font-bold", (lastMatch.earlyLaningPhaseGoldExpAdvantage || 0) > 0 ? "text-green-400" : (lastMatch.earlyLaningPhaseGoldExpAdvantage || 0) < 0 ? "text-red-400" : "text-zinc-400")}>
                                        {fmtSigned(lastMatch.earlyLaningPhaseGoldExpAdvantage)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Gold/XP @14min</span>
                                    <span className={cn("font-bold", (lastMatch.laningPhaseGoldExpAdvantage || 0) > 0 ? "text-green-400" : (lastMatch.laningPhaseGoldExpAdvantage || 0) < 0 ? "text-red-400" : "text-zinc-400")}>
                                        {fmtSigned(lastMatch.laningPhaseGoldExpAdvantage)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Max CS Lead</span>
                                    <span className={cn("font-bold", (lastMatch.maxCsAdvantageOnLaneOpponent || 0) > 0 ? "text-green-400" : (lastMatch.maxCsAdvantageOnLaneOpponent || 0) < 0 ? "text-red-400" : "text-zinc-400")}>
                                        {fmtSigned(lastMatch.maxCsAdvantageOnLaneOpponent)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Max Level Lead</span>
                                    <span className={cn("font-bold", (lastMatch.maxLevelLeadLaneOpponent || 0) > 0 ? "text-green-400" : (lastMatch.maxLevelLeadLaneOpponent || 0) < 0 ? "text-red-400" : "text-zinc-400")}>
                                        {fmtSigned(lastMatch.maxLevelLeadLaneOpponent)}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">CS @10min</span>
                                    <span className="font-bold text-amber-400">{fmt(lastMatch.laneMinionsFirst10Minutes, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Turret Plates</span>
                                    <span className="font-bold text-amber-400">{fmt(lastMatch.turretPlatesTaken)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Mechanical Skills - NOW PREDICTIVE with calculated rates */}
                        <div className="bg-black/40 rounded-xl p-4 border border-cyan-500/10">
                            <h4 className="font-semibold text-cyan-400 mb-3 flex items-center gap-2">
                                <Target className="w-4 h-4" />
                                Mechanical Skills
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between items-center">
                                    <span className="text-zinc-400">Skillshot Hit Rate</span>
                                    <span className="font-bold text-cyan-400">{(lastMatch.skillshotHitRate || 0).toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-zinc-400">Skillshot Dodge Rate</span>
                                    <span className="font-bold text-cyan-400">{(lastMatch.skillshotDodgeRate || 0).toFixed(1)}%</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Skillshots Hit</span>
                                    <span className="font-bold text-cyan-400">{lastMatch.skillshotsHit || 0} <span className="text-zinc-500 font-normal">/ {lastMatch.mySkillshotCasts || 0}</span></span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Dodged</span>
                                    <span className="font-bold text-cyan-400">{lastMatch.skillshotsDodged || 0} <span className="text-zinc-500 font-normal">/ {lastMatch.enemySkillshotCasts || 0}</span></span>
                                </div>
                            </div>
                            <p className="text-zinc-600 text-xs mt-2 leading-relaxed">
                                Hit Rate = Hits / Your Skillshot Casts<br />
                                Dodge Rate = Dodged / Enemy Skillshot Casts<br />
                                Last Game Champion = {lastMatch.championName} ( <span className="opacity-70">Skillshots: [{Array.isArray(lastMatch.championSkillshots) ? lastMatch.championSkillshots.join(", ") : "?"}]</span> )
                            </p>
                        </div>

                        <div className="bg-black/40 rounded-xl p-4 border border-green-500/10">
                            <h4 className="font-semibold text-green-400 mb-3 flex items-center gap-2">
                                <Eye className="w-4 h-4" />
                                Vision Habits
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Vision Score Adv.</span>
                                    {/* visionScoreAdvantageLaneOpponent can be undefined, handle gracefully */}
                                    <span className="font-bold text-green-400">{fmtSigned(lastMatch.visionScoreAdvantageLaneOpponent || 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Wards Placed</span>
                                    <span className="font-bold text-green-400">{fmt(lastMatch.wardsPlaced, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Control Wards</span>
                                    <span className="font-bold text-green-400">{fmt(lastMatch.controlWardsPlaced, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Detector Wards</span>
                                    <span className="font-bold text-green-400">{fmt(lastMatch.detectorWardsPlaced, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Vision in Enemy Half</span>
                                    <span className="font-bold text-emerald-400">{fmtPct(lastMatch.controlWardTimeCoverageInRiverOrEnemyHalf)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Communication Habits */}
                        <div className="bg-black/40 rounded-xl p-4 border border-blue-500/10">
                            <h4 className="font-semibold text-blue-400 mb-3 flex items-center gap-2">
                                <MessageCircle className="w-4 h-4" />
                                Communication Habits
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Enemy Missing</span>
                                    <span className="font-bold text-blue-400">{fmt(lastMatch.enemyMissingPings, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">On My Way</span>
                                    <span className="font-bold text-blue-400">{fmt(lastMatch.onMyWayPings, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Assist Me</span>
                                    <span className="font-bold text-blue-400">{fmt(lastMatch.assistMePings, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Retreat</span>
                                    <span className="font-bold text-blue-400">{fmt(lastMatch.getBackPings, 0)}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Territory Control - From Timeline Analysis */}
                    {territory_metrics && (territory_metrics.time_in_enemy_territory_pct > 0 || territory_metrics.river_control_pct > 0) && (
                        <div className="bg-black/30 rounded-xl p-4 border border-cyan-500/10 mb-4">
                            <h4 className="font-semibold text-cyan-400 mb-3 flex items-center gap-2">
                                <Map className="w-4 h-4" />
                                Territory Control
                                <span className="text-xs bg-cyan-500/20 text-cyan-400 px-2 py-1 rounded-full">⚽ Like Football</span>
                            </h4>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-cyan-400">{(territory_metrics.time_in_enemy_territory_pct || 0).toFixed(1)}%</div>
                                    <div className="text-zinc-500 text-xs">Time in Enemy Half</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-cyan-400">{(territory_metrics.forward_positioning_score || 0).toFixed(1)}</div>
                                    <div className="text-zinc-500 text-xs">Forward Score</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-purple-400">{(territory_metrics.jungle_invasion_pct || 0).toFixed(1)}%</div>
                                    <div className="text-zinc-500 text-xs">Jungle Invasion</div>
                                </div>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-blue-400">{(territory_metrics.river_control_pct || 0).toFixed(1)}%</div>
                                    <div className="text-zinc-500 text-xs">River Control</div>
                                </div>
                            </div>
                        </div>
                    )}

                </section>

                {/* Category Importance (Moved Here) */}
                {category_importance.length > 0 && (
                    <section className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "350ms" }}>
                        <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                            <Layers className="w-5 h-5 text-yellow-400" />
                            Predictive Category Importance
                            <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded-full">🧠 ML Model</span>
                        </h3>
                        <p className="text-zinc-500 text-sm mb-4">Which predictive factors matter most for YOUR win probability (not outcome-correlated)</p>
                        <div className="space-y-3">
                            {category_importance.map(([cat, val]: [string, number], idx: number) => {
                                const colors = ["bg-amber-500", "bg-cyan-500", "bg-purple-500", "bg-green-500", "bg-blue-500", "bg-pink-500", "bg-emerald-500"];
                                const maxVal = category_importance[0][1] || 1;
                                const pct = (val / maxVal) * 100;
                                return (
                                    <div key={idx}>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="font-medium">{cat}</span>
                                            <span className="text-zinc-400">{(val * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="h-3 bg-zinc-800 rounded-full overflow-hidden">
                                            <div className={cn("h-full rounded-full transition-all duration-500", colors[idx % colors.length])} style={{ width: `${pct}%` }} />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </section>
                )}

                {/* Player Moods */}
                {/* Current Vibe section removed (Moved to Header) */}

                {/* Average Stats Grid */}
                <section className="animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "200ms" }}>
                    <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                        <ChartLine className="w-5 h-5 text-indigo-400" />
                        Average Stats
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <StatCard
                            label="Win Rate"
                            value={`${win_rate.toFixed(1)}%`}
                            color={win_rate >= 50 ? "text-green-400" : "text-red-400"}
                        />
                        <StatCard
                            label="KDA"
                            value={`${fmt(avg.kills)} / ${fmt(avg.deaths)} / ${fmt(avg.assists)}`}
                        />
                        <StatCard
                            label="CS @ 10min"
                            value={fmt(avg.laneMinionsFirst10Minutes, 0)}
                            icon={Wheat}
                        />
                        <StatCard
                            label="Vision Score"
                            value={fmt(avg.visionScore)}
                            icon={Eye}
                        />
                        <StatCard
                            label="Solo Kills"
                            value={fmt(avg.soloKills)}
                            icon={Skull}
                        />
                    </div>
                </section>

                {/* Detailed Stat Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "250ms" }}>

                    {/* Combat */}
                    <DetailCard title="Combat" icon={Crosshair} iconColor="text-red-400">
                        <FeatureItem name="Total Damage" value={fmt(avg.totalDamageDealtToChampions, 0)} />
                        <FeatureItem name="Damage/Min" value={fmt(avg.damagePerMinute, 0)} />
                        <FeatureItem name="Team Damage %" value={fmtPct(avg.teamDamagePercentage)} />
                        <FeatureItem name="Damage Taken" value={fmt(avg.totalDamageTaken, 0)} />
                        <FeatureItem name="Healing" value={fmt(avg.totalHeal, 0)} />
                        <FeatureItem name="CC Time" value={`${fmt(avg.timeCCingOthers)}s`} />
                    </DetailCard>

                    {/* Objectives */}
                    <DetailCard title="Objectives" icon={Target} iconColor="text-purple-400">
                        <FeatureItem name="Objective Damage" value={fmt(avg.damageDealtToObjectives, 0)} />
                        <FeatureItem name="Dragon Kills" value={fmt(avg.dragonTakedowns || avg.dragonKills)} />
                        <FeatureItem name="Baron Kills" value={fmt(avg.baronTakedowns || avg.baronKills)} />
                        <FeatureItem name="Epic Steals" value={fmt(avg.epicMonsterSteals)} />
                        <FeatureItem name="Objectives Stolen" value={fmt(avg.objectivesStolen)} />
                    </DetailCard>

                    {/* Early Game & Laning */}
                    <DetailCard title="Early Game & Laning" icon={Zap} iconColor="text-yellow-400">
                        <FeatureItem name="CS @ 10 Minutes" value={fmt(avg.laneMinionsFirst10Minutes, 0)} />
                        <FeatureItem
                            name="Max CS Lead in Lane"
                            value={fmtSigned(avg.maxCsAdvantageOnLaneOpponent)}
                            valueColor={avg.maxCsAdvantageOnLaneOpponent > 0 ? "text-green-400" : avg.maxCsAdvantageOnLaneOpponent < 0 ? "text-red-400" : "text-zinc-400"}
                        />
                        <FeatureItem
                            name="Max Level Lead"
                            value={fmtSigned(avg.maxLevelLeadLaneOpponent)}
                            valueColor={avg.maxLevelLeadLaneOpponent > 0 ? "text-green-400" : avg.maxLevelLeadLaneOpponent < 0 ? "text-red-400" : "text-zinc-400"}
                        />
                        <FeatureItem
                            name="Early Gold/XP Advantage"
                            value={fmtSigned(avg.earlyLaningPhaseGoldExpAdvantage)}
                            valueColor={avg.earlyLaningPhaseGoldExpAdvantage > 0 ? "text-green-400" : avg.earlyLaningPhaseGoldExpAdvantage < 0 ? "text-red-400" : "text-zinc-400"}
                        />
                        <FeatureItem name="Gold per Minute" value={fmt(avg.goldPerMinute, 0)} />
                    </DetailCard>

                    {/* Vision Control */}
                    <DetailCard title="Vision Control" icon={Eye} iconColor="text-blue-400">
                        <FeatureItem name="Vision Score/Min" value={fmt(avg.visionScorePerMinute, 2)} />
                        <FeatureItem name="Wards Placed" value={fmt(avg.wardsPlaced)} />
                        <FeatureItem name="Wards Killed" value={fmt(avg.wardsKilled)} />
                        <FeatureItem name="Control Wards" value={fmt(avg.controlWardsPlaced)} />
                        <FeatureItem name="Control Ward Coverage" value={fmtPct(avg.controlWardTimeCoverageInRiverOrEnemyHalf)} />
                    </DetailCard>
                </div>


                {/* Display Stats - Outcome-Correlated (NOT used for prediction) */}
                <section className="bg-zinc-900/50 border border-zinc-800/50 rounded-xl p-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "275ms" }}>
                    <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                        <Target className="w-5 h-5 text-zinc-400" />
                        Display Stats
                        <span className="text-xs bg-zinc-700/50 text-zinc-400 px-2 py-1 rounded-full">Not used for ML</span>
                    </h3>
                    <p className="text-zinc-500 text-sm mb-4">These stats are outcome-correlated (higher when winning) - shown for context only</p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        {/* Raw Skill Numbers */}
                        <div className="bg-black/30 rounded-xl p-4 border border-zinc-700/30">
                            <h4 className="font-semibold text-zinc-300 mb-3 flex items-center gap-2">
                                <Crosshair className="w-4 h-4" />
                                Raw Numbers
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between items-center">
                                    <span className="text-zinc-400">Skills Hit / Casts</span>
                                    <span className="font-bold text-zinc-400">
                                        {fmt(avg.skillshotsHit, 0)} / {fmt((avg.spell1Casts || 0) + (avg.spell2Casts || 0) + (avg.spell3Casts || 0) + (avg.spell4Casts || 0), 0)}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-zinc-400">Skillshots Dodged</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.skillshotsDodged, 0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Solo Kills</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.soloKills)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Objective Stats */}
                        <div className="bg-black/30 rounded-xl p-4 border border-zinc-700/30">
                            <h4 className="font-semibold text-zinc-300 mb-3 flex items-center gap-2">
                                <Crown className="w-4 h-4" />
                                Objective Stats
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Dragon Takedowns</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.dragonTakedowns)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Baron Takedowns</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.baronTakedowns)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Turret Takedowns</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.turretTakedowns)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Objective Damage</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.damageDealtToObjectives, 0)}</span>
                                </div>
                            </div>
                        </div>

                        {/* Combat Stats */}
                        <div className="bg-black/30 rounded-xl p-4 border border-zinc-700/30">
                            <h4 className="font-semibold text-zinc-300 mb-3 flex items-center gap-2">
                                <Swords className="w-4 h-4" />
                                Combat Stats
                            </h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Kills / Deaths / Assists</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.kills)}/{fmt(avg.deaths)}/{fmt(avg.assists)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">KDA Ratio</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.kda)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Kill Participation</span>
                                    <span className="font-bold text-zinc-400">{fmtPct(avg.killParticipation)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-zinc-400">Damage/min</span>
                                    <span className="font-bold text-zinc-400">{fmt(avg.damagePerMinute, 0)}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                </section>

                {/* Communication Pings */}
                <section className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "300ms" }}>
                    <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                        <MessageCircle className="w-5 h-5 text-green-400" />
                        Communication (Pings)
                    </h3>
                    <p className="text-zinc-500 text-sm mb-4">Track your in-game communication patterns</p>
                    <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                        <StatCard label="🔵 On My Way" value={fmt(avg.onMyWayPings)} />
                        <StatCard label="❓ Enemy Missing" value={fmt(avg.enemyMissingPings)} />
                        <StatCard label="🎯 Assist Me" value={fmt(avg.assistMePings)} />
                        <StatCard label="👁️ Need Vision" value={fmt(avg.needVisionPings)} />
                        <StatCard label="⚔️ Engage" value={fmt(avg.allInPings)} />
                        <StatCard label="⚠️ Retreat" value={fmt(avg.getBackPings)} />
                        <StatCard label="⬆️ Push" value={fmt(avg.pushPings)} />
                        <StatCard label="✨ Vision Cleared" value={fmt(avg.visionClearedPings)} />
                        <StatCard label="📍 Basic Ping" value={fmt(avg.commandPings)} />
                        <StatCard label="✋ Hold" value={fmt(avg.holdPings)} />
                    </div>
                </section>

                {/* Category Importance moved up */}

                {/* Top Differentiators */}
                {top_differentiators.length > 0 && (
                    <section className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "400ms" }}>
                        <h3 className="text-xl font-semibold mb-2 flex items-center gap-2">
                            <BarChart3 className="w-5 h-5 text-red-400" />
                            Key Win Factors
                            <span className="text-xs bg-red-500/20 text-red-400 px-2 py-1 rounded-full">Predictive</span>
                        </h3>
                        <p className="text-zinc-500 text-sm mb-4">These predictive metrics differ most between your wins and losses</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {top_differentiators.slice(0, 6).map(([feature, stats]: [string, any], idx: number) => {
                                // Calculate sensible difference display
                                const winVal = stats.avg_when_winning || 0;
                                const loseVal = stats.avg_when_losing || 0;
                                const absDiff = winVal - loseVal;
                                const isPositive = absDiff > 0;

                                // Cap percentage to avoid crazy values when base is near zero
                                let pctDiff = stats.percent_difference || 0;
                                const showPercent = Math.abs(pctDiff) <= 500 && Math.abs(loseVal) > 0.1;

                                // Clamp to reasonable display range
                                pctDiff = Math.max(-500, Math.min(500, pctDiff));

                                return (
                                    <div
                                        key={idx}
                                        className={cn(
                                            "p-4 rounded-xl border-l-4",
                                            "bg-gradient-to-r from-zinc-900/80 to-transparent",
                                            isPositive ? "border-green-500" : "border-red-500"
                                        )}
                                    >
                                        <div className="font-semibold mb-3 text-white">
                                            {feature.replace(/([A-Z])/g, ' $1').replace(/_/g, ' ').trim()}
                                        </div>
                                        <div className="space-y-2 text-sm">
                                            <div className="flex justify-between">
                                                <span className="text-green-400">When Winning:</span>
                                                <span className="font-bold">{winVal.toFixed(1)}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span className="text-red-400">When Losing:</span>
                                                <span className="font-bold">{loseVal.toFixed(1)}</span>
                                            </div>
                                        </div>
                                        <div className={cn(
                                            "mt-3 text-center py-2 rounded-lg font-bold text-lg",
                                            isPositive ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"
                                        )}>
                                            {showPercent ? (
                                                <>{pctDiff >= 0 ? "+" : ""}{pctDiff.toFixed(1)}%</>
                                            ) : (
                                                <>{isPositive ? "+" : ""}{absDiff.toFixed(1)} difference</>
                                            )}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </section>
                )}

                {/* Training Data Footer */}
                <section className="bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-4 text-center text-sm text-zinc-500 animate-in fade-in slide-in-from-bottom duration-500" style={{ animationDelay: "450ms" }}>
                    <div className="flex items-center justify-center gap-6">
                        <span><strong>{total_matches}</strong> Matches Analyzed</span>
                        <span>•</span>
                        <span>Model Accuracy: <strong>{((metrics?.accuracy || 0) * 100).toFixed(1)}%</strong></span>
                        <span>•</span>
                        <span className="text-green-400"><strong>{metrics?.wins || 0}W</strong></span>
                        <span className="text-red-400"><strong>{metrics?.losses || 0}L</strong></span>
                    </div>
                </section>
            </div>
        </div>
    );
}
