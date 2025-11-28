import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

class WinPredictionModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_columns = [
            # KDA & Economy
            'kills', 'deaths', 'assists', 'goldEarned', 'goldPerMinute',
            'totalMinionsKilled', 'neutralMinionsKilled',
            
            # Damage & Combat
            'totalDamageDealtToChampions', 'physicalDamageDealtToChampions', 
            'magicDamageDealtToChampions', 'trueDamageDealtToChampions',
            'totalDamageTaken', 'totalHeal', 'timeCCingOthers',
            'damagePerMinute', 'damageTakenOnTeamPercentage', 'teamDamagePercentage',
            'killParticipation', 'soloKills',
            
            # Objectives
            'visionScore', 'turretKills', 'dragonKills', 'baronKills',
            'damageDealtToObjectives', 'turretTakedowns', 'turretPlatesTaken',
            'objectivesStolen', 'epicMonsterSteals',
            
            # Laning & Opponent Comparison
            'laneMinionsFirst10Minutes', 'maxCsAdvantageOnLaneOpponent', 
            'maxLevelLeadLaneOpponent', 'earlyLaningPhaseGoldExpAdvantage',
            'laningPhaseGoldExpAdvantage', 'visionScoreAdvantageLaneOpponent',
            'controlWardTimeCoverageInRiverOrEnemyHalf',
            
            # Vision
            'wardsPlaced', 'wardsKilled', 'detectorWardsPlaced',
            'visionScorePerMinute', 'controlWardsPlaced',
            
            # Pings (Communication)
            'allInPings', 'assistMePings', 'commandPings', 'enemyMissingPings', 
            'getBackPings', 'holdPings', 'needVisionPings', 'onMyWayPings', 
            'pushPings', 'visionClearedPings'
        ]
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
                        # 1. Check top-level participant data
                        if feature in p:
                            row[feature] = p[feature]
                        # 2. Check 'challenges' dictionary (nested)
                        elif 'challenges' in p and feature in p['challenges']:
                            row[feature] = p['challenges'][feature]
                        # 3. Special handling / Defaults
                        else:
                            row[feature] = 0 # Default to 0 if not found
                    
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

        # Split data (though for this simple app we might just train on all for "personal stats" analysis)
        # For better "prediction" of *future* games, we should split. 
        # But here we are analyzing "what makes YOU win".
        
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate feature importance
        importances = self.model.feature_importances_
        feature_importance = dict(zip(self.feature_columns, importances))
        sorted_importance = sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)
        
        return {
            "feature_importance": sorted_importance,
            "accuracy": self.model.score(X, y) # Training accuracy
        }

    def predict_win_probability(self, current_stats):
        if not self.is_trained:
            return 0.0
        
        # Ensure input has all features
        input_df = pd.DataFrame([current_stats], columns=self.feature_columns)
        input_df = input_df.fillna(0)
        
        probability = self.model.predict_proba(input_df)[0][1] # Probability of class 1 (Win)
        return probability * 100
