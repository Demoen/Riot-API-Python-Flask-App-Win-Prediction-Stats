"""
ML Pipeline for Win Prediction
Refactored to use TRULY PREDICTIVE features rather than outcome-correlated stats.

Key principles:
1. Use EARLY GAME LEADS (measured BEFORE outcome is decided)
2. Use HABIT-BASED metrics (consistent whether winning or losing)
3. REMOVE any feature that naturally increases when winning
"""
import json
import os
import pandas as pd
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Participant, Match

# Load Skillshot Data
SKILLSHOT_DATA = {}
try:
    # Assuming file is in apps/api/ml/data/lol_skillshots.json relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'data', 'lol_skillshots.json')
    if os.path.exists(data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            SKILLSHOT_DATA = json.load(f)
    else:
        print(f"Warning: Skillshot data file not found at {data_path}")
except Exception as e:
    print(f"Error loading skillshot data: {e}")

# ============================================================================
# TRULY PREDICTIVE FEATURES - Used for ML model training
# These features are measured EARLY or are HABIT-based, not outcome-correlated
# ============================================================================
PREDICTIVE_FEATURES = [
    # --- EARLY GAME LEADS (Best predictors - measured at 8-14 min) ---
    # These are comparative LEADS, not totals, measured before game is decided
    'earlyLaningPhaseGoldExpAdvantage',   # Gold/XP lead at ~8 min
    'laningPhaseGoldExpAdvantage',         # Gold/XP lead at ~14 min  
    'maxCsAdvantageOnLaneOpponent',        # Peak CS LEAD over lane opponent
    'maxLevelLeadLaneOpponent',            # Peak Level LEAD over lane opponent
    'visionScoreAdvantageLaneOpponent',    # Vision LEAD over lane opponent
    
    # --- EARLY GAME EFFICIENCY (Before snowball effects) ---
    'laneMinionsFirst10Minutes',           # CS at 10 min (consistent skill indicator)
    'turretPlatesTaken',                   # Plates fall at 14 min (early game only)
    'skillshotsEarlyGame',                 # Skillshots hit early (before snowball)
    
    # --- MECHANICAL SKILL (Calculated ratios - skill-based, not outcome-based) ---
    # Hit rate = consistent mechanical skill indicator
    'skillshotHitRate',                    # skillshotsHit / totalAbilityCasts (calculated)
    'skillshotDodgeRate',                  # skillshotsDodged / enemyAbilityCasts (calculated)
    
    # --- VISION HABITS (Consistent playstyle, NOT correlated with winning) ---
    # You place wards whether you're winning or losing - it's a habit
    'wardsPlaced',                         # Vision habit
    'controlWardsPlaced',                  # Control ward buying habit
    'detectorWardsPlaced',                 # Sweeper/detector usage
    'controlWardTimeCoverageInRiverOrEnemyHalf',  # Proactive vision placement
    
    # --- COMMUNICATION HABITS (Ping frequency is consistent) ---
    # Your ping habits don't change based on winning - it's your playstyle
    'enemyMissingPings',                   # Map awareness habit
    'onMyWayPings',                        # Coordination habit
    'assistMePings',                       # Communication habit
    'getBackPings',                        # Warning habit
    
    # --- CONTEXT (External factors you can't control) ---
    'hadAfkTeammate',                      # Out of control factor
]

# ============================================================================
# OUTCOME-CORRELATED FEATURES - Shown in UI but NOT used for prediction
# These are HIGH when winning BECAUSE you're winning (causation reversed)
# ============================================================================
DISPLAY_FEATURES = [
    # --- Combat Stats (You get more kills BECAUSE you're winning) ---
    'kills', 'deaths', 'assists', 'kda',
    'killParticipation', 'soloKills',
    'totalDamageDealtToChampions', 'damagePerMinute',
    'teamDamagePercentage', 'damageTakenOnTeamPercentage',
    'totalDamageTaken', 'totalHeal', 'timeCCingOthers',
    
    # --- Economy (You get more gold BECAUSE you're winning) ---
    'goldPerMinute', 'totalMinionsKilled', 'neutralMinionsKilled',
    
    # --- Objectives (You get more objectives BECAUSE you're winning) ---
    # These are NOT predictive - you take more dragons when you're ahead
    'damageDealtToObjectives',
    'turretTakedowns', 'dragonTakedowns', 'baronTakedowns',
    'dragonKills', 'baronKills',
    'objectivesStolen', 'epicMonsterSteals',
    
    # --- Vision Score (Higher BECAUSE you're alive longer when winning) ---
    'visionScore', 'visionScorePerMinute', 'wardsKilled',
    
    # --- Mechanical (More opportunities BECAUSE you're alive longer) ---
    'skillshotsHit', 'skillshotsDodged',
    # Spell casts for calculating hit rate: skillshotsHit / totalSpellCasts
    'spell1Casts', 'spell2Casts', 'spell3Casts', 'spell4Casts',
    
    # --- Jungle specific (More successful invades BECAUSE you're ahead) ---
    'junglerKillsEarlyJungle',
    'killsOnLanersEarlyJungleAsJungler',
    'epicMonsterKillsNearEnemyJungler',
    
    # --- Pings (these could go either way) ---
    'allInPings', 'commandPings', 'holdPings', 
    'needVisionPings', 'pushPings', 'visionClearedPings',
    
    # --- Composite Metrics ---
    'aggressionScore', 'visionDominance', 'jungleInvasionPressure', 'combat_efficiency'
]

# Combined for data loading
ALL_FEATURES = PREDICTIVE_FEATURES + DISPLAY_FEATURES

# Legacy compatibility
FEATURE_COLUMNS = PREDICTIVE_FEATURES

def get_skillshot_casts(stats, champion_name):
    """Calculate total casts of skillshot abilities for a champion."""
    # Default to all if not in our data (fallback)
    if not champion_name or champion_name not in SKILLSHOT_DATA:
        return (
            stats.get('spell1Casts', 0) + 
            stats.get('spell2Casts', 0) + 
            stats.get('spell3Casts', 0) + 
            stats.get('spell4Casts', 0)
        )
    
    skillshot_keys = SKILLSHOT_DATA[champion_name] # e.g. [1, 3, 4]
    total_casts = 0
    for key in skillshot_keys:
        total_casts += stats.get(f'spell{key}Casts', 0)
    return total_casts


async def load_player_data(db: AsyncSession, puuid: str, limit: int = 50) -> pd.DataFrame:
    """
    Load match data for a specific player from the database.
    """
    result = await db.execute(
        select(Participant, Match)
        .join(Match)
        .where(Participant.puuid == puuid)
        .order_by(Match.game_creation.desc())
        .limit(limit)
    )
    
    rows = []
    # Explicitly fetch all rows to ensure cursor is consumed
    query_rows = result.all()
    
    for participant, match in query_rows:
        row = {}
        stats = participant.stats_json
        challenges = stats.get('challenges', {})
        champion_name = stats.get('championName')
        
        # Load all features (predictive + display)
        for feature in ALL_FEATURES:
            if feature == 'kda':
                continue
            # Skip calculated features - we'll compute them below
            if feature in ['skillshotHitRate', 'skillshotDodgeRate', 'skillshotsDodged', 'skillshotsHit', 'spell1Casts', 'spell2Casts', 'spell3Casts', 'spell4Casts']:
                continue
                
            val = 0
            if hasattr(participant, feature) and getattr(participant, feature) is not None:
                val = getattr(participant, feature)
            elif feature in stats:
                val = stats[feature]
            elif feature in challenges:
                val = challenges[feature]
            
            row[feature] = val
            
        # Add basic stats for display
        row['skillshotsHit'] = challenges.get('skillshotsHit', 0)
        row['skillshotsDodged'] = challenges.get('skillshotsDodged', 0)
        row['spell1Casts'] = stats.get('spell1Casts', 0)
        row['spell2Casts'] = stats.get('spell2Casts', 0)
        row['spell3Casts'] = stats.get('spell3Casts', 0)
        row['spell4Casts'] = stats.get('spell4Casts', 0)
        row['championName'] = champion_name
        
        # --- Calculate Skillshot Hit Rate ---
        # skillshotsHit / (sum of SKILLSHOT ability casts only)
        # Using refined data from Meraki Analytics
        spell_casts = get_skillshot_casts(stats, champion_name)
        
        # Add skillshot keys for display (e.g. ["Q", "E"])
        skillshot_keys_list = []
        if champion_name and champion_name in SKILLSHOT_DATA:
            key_map = {1: 'Q', 2: 'W', 3: 'E', 4: 'R'}
            skillshot_keys_list = [key_map.get(k, str(k)) for k in sorted(SKILLSHOT_DATA[champion_name])]
        else:
            skillshot_keys_list = ['Q', 'W', 'E', 'R'] # Fallback
        row['championSkillshots'] = skillshot_keys_list
        
        skillshots_hit = challenges.get('skillshotsHit', 0)
        # Cap at 100% (data can sometimes be weird with multi-hit skillshots)
        hit_rate = (skillshots_hit / spell_casts * 100) if spell_casts > 0 else 0
        row['skillshotHitRate'] = min(hit_rate, 100.0)
        
        # --- Calculate Skillshot Dodge Rate ---
        # skillshotsDodged / (sum of ENEMY SKILLSHOT spell casts)
        skillshots_dodged = challenges.get('skillshotsDodged', 0)
        enemy_spell_casts = 0
        enemy_casts_debug = 0 # Track total casts for comparison
        
        # Get enemy spell casts from match data
        if match.data:
            match_info = match.data.get('info', {})
            participants_data = match_info.get('participants', [])
            player_team_id = participant.team_id
            
            for p_data in participants_data:
                # If enemy team
                if p_data.get('teamId') != player_team_id:
                     enemy_champ = p_data.get('championName')
                     enemy_spells_cast = get_skillshot_casts(p_data, enemy_champ)
                     enemy_spell_casts += enemy_spells_cast
                     
                     # Debug total casts (old method)
                     enemy_casts_debug += (
                         p_data.get('spell1Casts', 0) + p_data.get('spell2Casts', 0) + 
                         p_data.get('spell3Casts', 0) + p_data.get('spell4Casts', 0)
                     )
        
        # Determine valid dodge rate denominator
        # If we have refined data, use it. If 0 (e.g. no skillshot champs?), use debug total as fallback to avoid division by zero or inflated rates?
        # Actually if enemies have NO skillshots (e.g. master yi / udyr only?), then dodge rate is undefined or 0.
        denominator = enemy_spell_casts if enemy_spell_casts > 0 else enemy_casts_debug
        
        row['skillshotDodgeRate'] = (skillshots_dodged / denominator * 100) if denominator > 0 else 0
        
        # Add denominator for UI usage if needed (e.g. "Dodged / X casts")
        row['enemySkillshotCasts'] = denominator
        row['mySkillshotCasts'] = spell_casts
        
        # Add skillshot configuration string for UI
        if champion_name in SKILLSHOT_DATA:
            keys = SKILLSHOT_DATA[champion_name]
            mapping = {1: 'Q', 2: 'W', 3: 'E', 4: 'R'}
            valid_keys = [k for k in keys if k in mapping]
            mapped_keys = [mapping[k] for k in sorted(valid_keys)]
            config_str = "[" + ", ".join(mapped_keys) + "]"
        else:
            config_str = "[Q, W, E, R]"
        row['skillshotConfig'] = config_str
            

            
        # Calculate KDA
        k = row.get('kills', 0)
        d = row.get('deaths', 0)
        a = row.get('assists', 0)
        row['kda'] = (k + a) / d if d > 0 else k + a
        
        row['win'] = 1 if participant.win else 0
        row['gameCreation'] = match.game_creation
        row['match_id'] = match.match_id
        row['gameDuration'] = match.game_duration
        row['queueId'] = match.queue_id
        
        # Calculate Gold Per Minute if missing
        if 'goldPerMinute' not in row or row['goldPerMinute'] == 0:
            gold_earned = row.get('goldEarned', stats.get('goldEarned', 0))
            game_duration_min = match.game_duration / 60 if match.game_duration > 0 else 1
            row['goldPerMinute'] = gold_earned / game_duration_min
        
        # --- Composite Features (Aggression, Vision, Invasion) ---
        # Aggression: Normalized combination of damage and kills to 0-100 scale
        dmg_per_min = row.get('damagePerMinute', 0)
        solo_kills = row.get('soloKills', 0)
        
        # Benchmarks for 100% score
        BENCHMARK_DPM = 1000.0
        BENCHMARK_SOLO = 5.0
        
        dpm_score = min(dmg_per_min / BENCHMARK_DPM, 1.2) * 100 # Allow up to 120% cap for super performance
        solo_score = min(solo_kills / BENCHMARK_SOLO, 1.5) * 100
        
        # Weighted mix: 70% Damage, 30% Solo Kills
        # Cap at 100 total
        raw_aggression = (dpm_score * 0.7) + (solo_score * 0.3)
        row['aggressionScore'] = min(raw_aggression, 100.0)
        
        # Vision Dominance: Vision Score + Control Wards + Wards Killed
        vision_score = row.get('visionScore', 0)
        control_wards = row.get('controlWardsPlaced', 0)
        wards_killed = row.get('wardsKilled', 0)
        row['visionDominance'] = (vision_score * 1.5) + (control_wards * 5) + (wards_killed * 2)

        # Jungle Invasion Pressure: Stolen camps + Kills in enemy jungle
        enemy_jungle_minions = row.get('enemyJungleMinionsKilled', 0) # Needs to be in challenges usually
        # Fallback if not directly available, assume counterJungle is part of it
        # Actually 'enemyJungleMonsterKills' is often a challenge
        enemy_jungle_kills = challenges.get('enemyJungleMonsterKills', 0)
        epic_steals = challenges.get('epicMonsterSteals', 0)
        row['jungleInvasionPressure'] = (enemy_jungle_kills * 2) + (epic_steals * 50)

        # Combat Efficiency: DMG per Gold ratio normalized (Benchmark 2.0 = 100%)
        gold_earned = row.get('goldEarned', stats.get('goldEarned', 0))
        total_dmg = row.get('totalDamageDealtToChampions', 0)
        if gold_earned > 0:
            dpg_ratio = total_dmg / gold_earned
            # 2.0 DPG is elite performance (100% score)
            efficiency = (dpg_ratio / 2.0) * 100
            row['combat_efficiency'] = min(100.0, max(0.0, efficiency))
        else:
            row['combat_efficiency'] = 0.0

        rows.append(row)
        
    return pd.DataFrame(rows)


def prepare_features(df: pd.DataFrame, use_predictive_only: bool = True) -> pd.DataFrame:
    """
    Prepare feature matrix for model training.
    """
    if df.empty:
        cols = PREDICTIVE_FEATURES if use_predictive_only else ALL_FEATURES
        return pd.DataFrame(columns=cols)
    
    features = PREDICTIVE_FEATURES if use_predictive_only else ALL_FEATURES
        
    for col in features:
        if col not in df.columns:
            df[col] = 0
            
    # Fix FutureWarning by explicitly converting to numeric types
    return df[features].apply(pd.to_numeric, errors='coerce').fillna(0)


def get_feature_categories() -> dict:
    """
    Return categorized PREDICTIVE features for UI display.
    These are the categories that actually predict win probability.
    """
    return {
        'Early Game Leads': [
            'earlyLaningPhaseGoldExpAdvantage',
            'laningPhaseGoldExpAdvantage',
            'maxCsAdvantageOnLaneOpponent',
            'maxLevelLeadLaneOpponent',
            'visionScoreAdvantageLaneOpponent',
        ],
        'Early Game Efficiency': [
            'laneMinionsFirst10Minutes',
            'turretPlatesTaken',
        ],
        'Vision Habits': [
            'wardsPlaced',
            'controlWardsPlaced',
            'detectorWardsPlaced',
            'controlWardTimeCoverageInRiverOrEnemyHalf',
        ],
        'Communication Habits': [
            'enemyMissingPings',
            'onMyWayPings',
            'assistMePings',
            'getBackPings',
        ],
    }
