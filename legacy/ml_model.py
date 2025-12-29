import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

class WinPredictionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
        # Features that are NOT direct outcomes of winning (removed causal features)
        # Removed: turretKills, turretTakedowns, turretPlatesTaken (direct win conditions)
        # Kept: Features that reflect player skill and decision-making
        self.feature_columns = [
            # Individual Performance Metrics (skill-based)
            'kills', 'deaths', 'assists', 'kda',
            'killParticipation', 'soloKills',
            
            # Economy & Farming (player efficiency)
            'goldPerMinute', 'totalMinionsKilled', 'neutralMinionsKilled',
            'laneMinionsFirst10Minutes',
            
            # Combat Efficiency (how you fight, not outcomes)
            'totalDamageDealtToChampions', 'damagePerMinute', 
            'teamDamagePercentage', 'damageTakenOnTeamPercentage',
            'totalDamageTaken', 'totalHeal', 'timeCCingOthers',
            
            # Early Game Performance (laning phase)
            'maxCsAdvantageOnLaneOpponent', 'maxLevelLeadLaneOpponent', 
            'earlyLaningPhaseGoldExpAdvantage', 'laningPhaseGoldExpAdvantage',
            
            # Vision Control (map awareness)
            'visionScore', 'visionScorePerMinute', 'wardsPlaced', 
            'wardsKilled', 'detectorWardsPlaced', 'controlWardsPlaced',
            'visionScoreAdvantageLaneOpponent',
            'controlWardTimeCoverageInRiverOrEnemyHalf',
            
            # Objective Control (fighting for objectives, not results)
            'dragonKills', 'baronKills', 'damageDealtToObjectives',
            'objectivesStolen', 'epicMonsterSteals',
            
            # Team Communication
            'allInPings', 'assistMePings', 'commandPings', 'enemyMissingPings', 
            'getBackPings', 'holdPings', 'needVisionPings', 'onMyWayPings', 
            'pushPings', 'visionClearedPings',
            
            # Team Issues
            'hadAfkTeammate'
        ]
        
        # Feature categories for better analysis
        self.feature_categories = {
            'Combat & KDA': ['kills', 'deaths', 'assists', 'kda', 'killParticipation', 'soloKills',
                            'totalDamageDealtToChampions', 'damagePerMinute', 'teamDamagePercentage',
                            'damageTakenOnTeamPercentage', 'totalDamageTaken', 'totalHeal', 'timeCCingOthers'],
            'Economy & Farming': ['goldPerMinute', 'totalMinionsKilled', 'neutralMinionsKilled',
                                 'laneMinionsFirst10Minutes'],
            'Early Game': ['maxCsAdvantageOnLaneOpponent', 'maxLevelLeadLaneOpponent',
                          'earlyLaningPhaseGoldExpAdvantage', 'laningPhaseGoldExpAdvantage'],
            'Vision Control': ['visionScore', 'visionScorePerMinute', 'wardsPlaced', 'wardsKilled',
                              'detectorWardsPlaced', 'controlWardsPlaced', 'visionScoreAdvantageLaneOpponent',
                              'controlWardTimeCoverageInRiverOrEnemyHalf'],
            'Objective Control': ['dragonKills', 'baronKills', 'damageDealtToObjectives',
                                 'objectivesStolen', 'epicMonsterSteals'],
            'Communication': ['allInPings', 'assistMePings', 'commandPings', 'enemyMissingPings',
                            'getBackPings', 'holdPings', 'needVisionPings', 'onMyWayPings',
                            'pushPings', 'visionClearedPings']
        }
        
        self.is_trained = False

    def prepare_data(self, matches, summoner_puuid):
        data = []
        for match in matches:
            if 'info' not in match: 
                continue
                
            participants = match['info']['participants']
            for p in participants:
                if p['puuid'] == summoner_puuid:
                    # Extract features
                    row = {}
                    for feature in self.feature_columns:
                        # Skip calculated features
                        if feature == 'kda':
                            continue
                            
                        # 1. Check top-level participant data
                        if feature in p:
                            row[feature] = p[feature]
                        # 2. Check 'challenges' dictionary (nested)
                        elif 'challenges' in p and feature in p['challenges']:
                            row[feature] = p['challenges'][feature]
                        # 3. Special handling / Defaults
                        else:
                            row[feature] = 0 # Default to 0 if not found
                    
                    # Calculate KDA
                    kills = row.get('kills', 0)
                    deaths = row.get('deaths', 0)
                    assists = row.get('assists', 0)
                    row['kda'] = (kills + assists) / deaths if deaths > 0 else kills + assists
                    
                    # Add win status
                    row['win'] = 1 if p['win'] else 0
                    data.append(row)
                    break
        
        return pd.DataFrame(data)

    def train(self, matches, summoner_puuid):
        df = self.prepare_data(matches, summoner_puuid)
        
        if df.empty or len(df) < 5: # Need some data to train
            return {"error": "Not enough data to train model (need at least 5 matches)"}

        X = df[self.feature_columns]
        y = df['win']

        # Create sample weights that prioritize recent games
        # Matches are ordered from newest to oldest
        n_matches = len(df)
        sample_weights = np.zeros(n_matches)
        
        for i in range(n_matches):
            if i == 0:  # Most recent game gets 4x weight
                sample_weights[i] = 4.0
            elif i < 5:  # Games 2-5 get 2x weight
                sample_weights[i] = 2.0
            else:  # Older games get normal weight
                sample_weights[i] = 1.0
        
        # Train the model with weighted samples
        self.model.fit(X, y, sample_weight=sample_weights)
        self.is_trained = True
        
        # Store the dataframe for weighted average calculation
        self.trained_df = df
        self.sample_weights = sample_weights
        
        # Calculate feature importance
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_columns, importances))
        sorted_importance = sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)
        
        # Calculate category importance
        category_importance = {}
        for category, features in self.feature_categories.items():
            total_importance = sum(feature_importance.get(f, 0) for f in features)
            category_importance[category] = total_importance
        
        sorted_category_importance = sorted(category_importance.items(), key=lambda item: item[1], reverse=True)
        
        # Analyze win vs loss differences
        wins_df = df[df['win'] == 1]
        losses_df = df[df['win'] == 0]
        
        performance_insights = {}
        if len(wins_df) > 0 and len(losses_df) > 0:
            for feature in self.feature_columns:
                avg_win = wins_df[feature].mean()
                avg_loss = losses_df[feature].mean()
                difference = avg_win - avg_loss
                percent_diff = (difference / avg_loss * 100) if avg_loss != 0 else 0
                
                performance_insights[feature] = {
                    'avg_when_winning': avg_win,
                    'avg_when_losing': avg_loss,
                    'difference': difference,
                    'percent_difference': percent_diff
                }
        
        # Find top differentiators (what changes most between wins and losses)
        top_differentiators = sorted(
            performance_insights.items(),
            key=lambda x: abs(x[1]['percent_difference']),
            reverse=True
        )[:10]
        
        return {
            "feature_importance": sorted_importance,
            "category_importance": sorted_category_importance,
            "performance_insights": performance_insights,
            "top_differentiators": top_differentiators,
            "accuracy": self.model.score(X, y),
            "total_matches": len(df),
            "wins": int(y.sum()),
            "losses": int(len(df) - y.sum())
        }

    def predict_win_probability(self, current_stats):
        if not self.is_trained:
            return 0.0
        
        # Ensure input has all features
        input_df = pd.DataFrame([current_stats], columns=self.feature_columns)
        input_df = input_df.fillna(0)
        
        probability = self.model.predict_proba(input_df)[0][1] # Probability of class 1 (Win)
        return probability * 100
    
    def calculate_weighted_averages(self, matches, summoner_puuid):
        """
        Calculate weighted averages that prioritize recent games
        Most recent game gets 4x weight, games 2-5 get 2x weight, rest get 1x weight
        """
        df = self.prepare_data(matches, summoner_puuid)
        
        if df.empty:
            return {}
        
        n_matches = len(df)
        weights = np.zeros(n_matches)
        
        for i in range(n_matches):
            if i == 0:  # Most recent game
                weights[i] = 4.0
            elif i < 5:  # Games 2-5
                weights[i] = 2.0
            else:  # Older games
                weights[i] = 1.0
        
        # Calculate weighted averages
        weighted_averages = {}
        for feature in self.feature_columns:
            if feature in df.columns:
                weighted_avg = np.average(df[feature], weights=weights)
                weighted_averages[feature] = weighted_avg
        
        return weighted_averages

    def analyze_player_mood(self, matches, summoner_puuid):
        """
        Analyze the last 3 matches to detect the player's current 'mood' or state.
        Returns a list of fun/meme-like tags based on performance patterns.
        """
        # Get data for last 3 matches
        recent_matches = matches[:3]
        df = self.prepare_data(recent_matches, summoner_puuid)
        
        if df.empty:
            return []
            
        moods = []
        
        # Calculate recent stats
        avg_kda = df['kda'].mean()
        win_rate = df['win'].mean() * 100
        avg_deaths = df['deaths'].mean()
        avg_kills = df['kills'].mean()
        avg_assists = df['assists'].mean()
        avg_vision = df.get('visionScore', pd.Series([0])).mean()
        avg_cs_min = (df.get('totalMinionsKilled', pd.Series([0])) + df.get('neutralMinionsKilled', pd.Series([0]))).mean() / 30 # Approx duration
        avg_kp = df.get('killParticipation', pd.Series([0])).mean()
        avg_damage_share = df.get('teamDamagePercentage', pd.Series([0])).mean()
        avg_damage_taken_share = df.get('damageTakenOnTeamPercentage', pd.Series([0])).mean()
        avg_afk = df.get('hadAfkTeammate', pd.Series([0])).sum()
        avg_solo_kills = df.get('soloKills', pd.Series([0])).mean()
        avg_obj_damage = df.get('damageDealtToObjectives', pd.Series([0])).mean()
        avg_turret_plates = df.get('turretPlatesTaken', pd.Series([0])).mean()
        avg_gold_min = df.get('goldPerMinute', pd.Series([0])).mean()
        avg_cs_diff = df.get('maxCsAdvantageOnLaneOpponent', pd.Series([0])).mean()
        
        # New Stats for more vibes
        avg_game_duration = df.get('gameDuration', pd.Series([1800])).mean()
        avg_turret_dmg = df.get('damageDealtToTurrets', pd.Series([0])).mean()
        avg_time_dead = df.get('totalTimeSpentDead', pd.Series([0])).mean()
        
        # Pings
        ping_cols = [c for c in df.columns if 'Pings' in c]
        total_pings = df[ping_cols].sum(axis=1).mean() if ping_cols else 0
        missing_pings = df.get('enemyMissingPings', pd.Series([0])).mean()

        # --- Performance & Outcome Based ---

        # 1. High Performing (The Smurf)
        if win_rate == 100 and avg_kda > 5.0:
            moods.append({
                "title": "Smurf Detected",
                "icon": "fa-crown",
                "color": "text-yellow-400",
                "description": f"Clean sweep! {int(win_rate)}% WR and {avg_kda:.1f} KDA. Are you boosting this account?",
                "advice": "Touch grass. Seriously."
            })
        elif win_rate >= 66 and avg_kda > 3.5:
             moods.append({
                "title": "Locked In",
                "icon": "fa-fire",
                "color": "text-orange-500",
                "description": f"You're sweating in low elo with a {int(win_rate)}% WR and {avg_kda:.1f} KDA.",
                "advice": "Stop tryharding in normals."
            })

        # 2. Tilted / Feeder
        if avg_deaths > 9:
             moods.append({
                "title": "Gray Screen Simulator",
                "icon": "fa-skull",
                "color": "text-gray-500",
                "description": f"Averaging {avg_deaths:.1f} deaths. Your team hates you.",
                "advice": "Uninstall or play Yuumi."
            })
        elif avg_deaths > 7 and win_rate < 34:
            moods.append({
                "title": "Tilt Queue?",
                "icon": "fa-heart-broken",
                "color": "text-red-500",
                "description": f"Losing ({int(win_rate)}% WR) and feeding ({avg_deaths:.1f} deaths). A classic combo.",
                "advice": "Alt+F4 is a valid combo."
            })

        # 3. Loser's Queue (Good stats, bad result)
        if win_rate <= 33 and avg_kda > 3.0 and avg_damage_share > 0.25:
            moods.append({
                "title": "Loser's Queue Victim",
                "icon": "fa-umbrella",
                "color": "text-blue-400",
                "description": f"Playing perfectly ({avg_kda:.1f} KDA) but Riot hates you personally.",
                "advice": "Cry about it on Reddit."
            })
        
        # 4. Getting Carried
        if win_rate >= 66 and avg_kda < 2.0 and avg_damage_share < 0.15:
             moods.append({
                "title": "Backpack Enjoyer",
                "icon": "fa-child",
                "color": "text-pink-400",
                "description": f"Winning ({int(win_rate)}% WR) while doing absolutely nothing ({avg_damage_share*100:.1f}% dmg).",
                "advice": "Say 'gg ez' after getting carried."
            })

        # 5. AFK Teammate
        if avg_afk > 0:
             moods.append({
                "title": "4v5 Warrior",
                "icon": "fa-user-slash",
                "color": "text-red-400",
                "description": f"Had an AFK in {int(avg_afk)} games. Riot's matchmaking at its finest.",
                "advice": "Scream into a pillow."
            })

        # --- Playstyle Based ---

        # 6. The Duelist (High Solo Kills)
        if avg_solo_kills > 2:
             moods.append({
                "title": "Main Character Syndrome",
                "icon": "fa-fist-raised",
                "color": "text-orange-600",
                "description": f"You ignore the team and 1v1 everyone ({avg_solo_kills:.1f} solo kills).",
                "advice": "It's a team game, genius."
            })

        # 7. Lane Kingdom (High CS/Level Lead)
        if avg_cs_diff > 20:
             moods.append({
                "title": "Lane Kingdom",
                "icon": "fa-chess-rook",
                "color": "text-purple-500",
                "description": f"Bullying your laner (+{avg_cs_diff:.0f} CS diff). They probably reported you.",
                "advice": "Stop torturing them and end the game."
            })

        # 8. The Farmer (High CS/min)
        if df.get('laneMinionsFirst10Minutes', pd.Series([0])).mean() > 80: 
             moods.append({
                "title": "PvE Player",
                "icon": "fa-wheat",
                "color": "text-green-400",
                "description": "You're playing Stardew Valley while your team fights.",
                "advice": "Minions don't give LP."
            })

        # 9. Visionary
        if avg_vision > 2.0 * (df.get('gameDuration', pd.Series([1800])).mean() / 60): 
             moods.append({
                "title": "Ward Bot",
                "icon": "fa-eye",
                "color": "text-cyan-400",
                "description": f"Vision score {avg_vision:.1f}. You're basically a walking ward.",
                "advice": "Try doing damage next time."
            })
        elif avg_vision < 10 and df.get('controlWardsPlaced', pd.Series([0])).mean() < 0.5:
             moods.append({
                "title": "Lee Sin Cosplay",
                "icon": "fa-low-vision",
                "color": "text-gray-400",
                "description": f"Vision score {avg_vision:.1f}. You play with your monitor off.",
                "advice": "Buy a ward, you cheapskate."
            })

        # 10. Aggressive / Coin Flip
        if avg_kills > 8 and avg_deaths > 8:
             moods.append({
                "title": "Yasuo Main Energy",
                "icon": "fa-coins",
                "color": "text-yellow-600",
                "description": f"Feeding ({avg_deaths:.1f}) and killing ({avg_kills:.1f}). A complete coinflip.",
                "advice": "Stop diving under tower."
            })

        # 11. The Tank / Meat Shield
        if avg_damage_taken_share > 0.30 and avg_deaths < 6:
             moods.append({
                "title": "Unkillable Demon King",
                "icon": "fa-shield-alt",
                "color": "text-indigo-400",
                "description": f"Tanking {avg_damage_taken_share*100:.1f}% of damage. They literally can't kill you.",
                "advice": "Spam mastery emote while tanking."
            })
        elif avg_damage_taken_share > 0.30 and avg_deaths >= 6:
             moods.append({
                "title": "Damage Sponge",
                "icon": "fa-hamburger",
                "color": "text-red-300",
                "description": f"You take {avg_damage_taken_share*100:.1f}% of damage by face-checking everything.",
                "advice": "Learn to dodge."
            })

        # 12. Hyper Carry (High Dmg %)
        if avg_damage_share > 0.35:
             moods.append({
                "title": "1v9 Machine",
                "icon": "fa-khanda",
                "color": "text-red-600",
                "description": f"Doing {avg_damage_share*100:.1f}% of team damage. Your team is useless.",
                "advice": "Don't break your back carrying these animals."
            })

        # 13. Objective Focus
        if avg_obj_damage > 20000:
             moods.append({
                "title": "Objective Obsessed",
                "icon": "fa-dragon",
                "color": "text-emerald-500",
                "description": f"{avg_obj_damage/1000:.1f}k obj damage. You hit dragons more than champions.",
                "advice": "Champions give gold too, you know."
            })

        # 14. Rich
        if avg_gold_min > 500:
             moods.append({
                "title": "Capitalist Pig",
                "icon": "fa-money-bill-wave",
                "color": "text-yellow-300",
                "description": f"Hoarding {avg_gold_min:.0f} Gold/Min. Share some with the poor.",
                "advice": "Full build at 20 min? Touch grass."
            })

        # 15. Communication
        if missing_pings > 15:
             moods.append({
                "title": "Toxic Pinger",
                "icon": "fa-question",
                "color": "text-yellow-500",
                "description": f"Spamming '?' {missing_pings:.1f} times a game. We know you're flaming.",
                "advice": "Unbind your ping key."
            })
        elif total_pings > 40:
             moods.append({
                "title": "Micro-Manager",
                "icon": "fa-bullhorn",
                "color": "text-blue-500",
                "description": f"{total_pings:.1f} pings per game. Nobody is listening to you.",
                "advice": "Shut up and play."
            })

        # 16. Pacifist
        if avg_damage_share < 0.10 and avg_assists > 8:
             moods.append({
                "title": "KDA Player",
                "icon": "fa-peace",
                "color": "text-teal-300",
                "description": f"Only {avg_damage_share*100:.1f}% dmg. Scared to fight?",
                "advice": "Right-click the enemy champions."
            })

        # 17. Thief
        if df.get('objectivesStolen', pd.Series([0])).sum() > 0:
             moods.append({
                "title": "Burglar",
                "icon": "fa-mask",
                "color": "text-purple-600",
                "description": "Stole an objective. Probably luck.",
                "advice": "Don't push your luck."
            })

        # 18. Team Player
        if avg_kp > 0.70:
             moods.append({
                "title": "Participation Trophy",
                "icon": "fa-users",
                "color": "text-cyan-500",
                "description": f"{avg_kp*100:.0f}% KP. You're just following your team around.",
                "advice": "Try doing something on your own."
            })
        elif avg_kp < 0.25 and win_rate > 50:
             moods.append({
                "title": "AFK Splitpusher",
                "icon": "fa-wolf-pack-battalion",
                "color": "text-gray-300",
                "description": f"Winning with {avg_kp*100:.0f}% KP. You're playing a single player game.",
                "advice": "Group up or get reported."
            })

        # 19. Early Game
        if df.get('earlyLaningPhaseGoldExpAdvantage', pd.Series([0])).mean() < -500:
             moods.append({
                "title": "Lane Liability",
                "icon": "fa-baby",
                "color": "text-red-400",
                "description": "Losing lane by 500+ gold. You are the reason we lose.",
                "advice": "Learn to lane or play support."
            })

        # 20. Late Game Thrower
        if df.get('gameDuration', pd.Series([0])).mean() > 2100 and win_rate < 50:
             moods.append({
                "title": "Late Game Choker",
                "icon": "fa-hourglass-end",
                "color": "text-purple-400",
                "description": "Long games (>35m) and you still lose.",
                "advice": "Learn to close out games."
            })

        # 21. Professional Choker (Win Lane -> Lose Game)
        if df.get('earlyLaningPhaseGoldExpAdvantage', pd.Series([0])).mean() > 300 and win_rate < 34:
             moods.append({
                "title": "Professional Choker",
                "icon": "fa-sad-tear",
                "color": "text-blue-500",
                "description": "You win lane hard, then throw the game harder.",
                "advice": "Stop 1v5ing and group."
            })

        # 22. Lucky Charm (Lose Lane -> Win Game)
        if df.get('earlyLaningPhaseGoldExpAdvantage', pd.Series([0])).mean() < -300 and win_rate > 66:
             moods.append({
                "title": "Lucky Charm",
                "icon": "fa-clover",
                "color": "text-green-500",
                "description": "Got absolutely rolled in lane but got carried.",
                "advice": "Better lucky than good."
            })

        # 23. The Fun Police (High CC)
        if df.get('timeCCingOthers', pd.Series([0])).mean() > 30:
             moods.append({
                "title": "The Fun Police",
                "icon": "fa-hand-paper",
                "color": "text-indigo-500",
                "description": "You don't let anyone play the game (>30s CC).",
                "advice": "Your opponents hate you. Good."
            })

        # 24. Ambulance (High Healing)
        if df.get('totalHeal', pd.Series([0])).mean() > 15000:
             moods.append({
                "title": "Hospital Bed",
                "icon": "fa-notes-medical",
                "color": "text-red-300",
                "description": "Healing numbers go brrr.",
                "advice": "You can't heal stupidity."
            })

        # 25. Ward Sweeper (High Wards Killed)
        if df.get('wardsKilled', pd.Series([0])).mean() > 8:
             moods.append({
                "title": "Umbral Glaive Abuser",
                "icon": "fa-broom",
                "color": "text-red-500",
                "description": "You hate vision. You destroy it.",
                "advice": "They can still see you dying."
            })

        # 26. The Accountant (High Gold, Low Dmg)
        if avg_gold_min > 450 and df.get('damagePerMinute', pd.Series([0])).mean() < 400:
             moods.append({
                "title": "The Accountant",
                "icon": "fa-file-invoice-dollar",
                "color": "text-yellow-600",
                "description": "Full build, zero damage. Hoarding gold.",
                "advice": "Spend your gold on damage, not skins."
            })
        
        # 27. Neutral Objective Gamer
        if df.get('neutralMinionsKilled', pd.Series([0])).mean() > 120:
             moods.append({
                "title": "PvE Legend",
                "icon": "fa-paw",
                "color": "text-green-600",
                "description": "You love hitting wolves more than champions.",
                "advice": "Gank a lane, maybe?"
            })

        # 28. Baron Enthusiast
        if df.get('baronKills', pd.Series([0])).mean() > 0.8:
             moods.append({
                "title": "Baron Tosser",
                "icon": "fa-skull-crossbones",
                "color": "text-purple-700",
                "description": "You force Baron every game. It's an addiction.",
                "advice": "Don't flip the game at 20."
            })

        # 29. Tower Destroyer
        if avg_turret_dmg > 5000:
             moods.append({
                "title": "Demolition Crew",
                "icon": "fa-hammer",
                "color": "text-orange-700",
                "description": f"You deal {avg_turret_dmg/1000:.1f}k damage to turrets. Ziggs main?",
                "advice": "Towers fall, but so do your teammates."
            })

        # 30. Gray Screen Simulator (Enhanced)
        if avg_time_dead > 300:
             moods.append({
                "title": "Spectator Mode",
                "icon": "fa-ghost",
                "color": "text-gray-600",
                "description": f"You spent {avg_time_dead/60:.1f} minutes dead on average. Nice movie.",
                "advice": "Try dodging skillshots instead of catching them."
            })

        # 31. Marathon Runner
        if avg_game_duration > 2400: # > 40 mins
             moods.append({
                "title": "Hostage Taker",
                "icon": "fa-hourglass",
                "color": "text-red-700",
                "description": f"Avg game time {avg_game_duration/60:.0f} mins. You refuse to end.",
                "advice": "Just hit the Nexus."
            })

        # Default if nothing matches
        if not moods:
             moods.append({
                "title": "NPC Energy",
                "icon": "fa-robot",
                "color": "text-gray-400",
                "description": "You exist. That's about it.",
                "advice": "Do something. Anything."
            })

        # Shuffle and return top 4 to keep it fresh but relevant
        # Sort by "relevance" or specific order if needed, but random is fun for "vibe"
        # Prioritize Smurf/Tilted as they are strong indicators
        
        # Simple deduplication if logic overlaps (though ifs above try to separate)
        unique_moods = {m['title']: m for m in moods}.values()
        
        return list(unique_moods)

