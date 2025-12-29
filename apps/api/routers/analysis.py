from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from services.ingestion import IngestionService
from services.riot import riot_service
from ml.pipeline import load_player_data
from ml.training import model_instance
from ml.timeline_analysis import analyze_match_territory, aggregate_territory_metrics
from models import Match, Participant
from pydantic import BaseModel
from typing import Optional
import asyncio

router = APIRouter(prefix="/api")

# Data Dragon version for profile icons
DDRAGON_VERSION = "14.24.1"

# Region to routing mapping
REGION_TO_ROUTING = {
    "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe",
    "na1": "americas", "br1": "americas", "la1": "americas", "la2": "americas",
    "kr": "asia", "jp1": "asia",
    "oc1": "sea", "ph2": "sea", "sg2": "sea", "th2": "sea", "tw2": "sea", "vn2": "sea",
}

class AnalyzeRequest(BaseModel):
    riot_id: str
    region: str

@router.post("/analyze")
async def analyze_player(request: AnalyzeRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # 1. Parse Riot ID
    if "#" not in request.riot_id:
        raise HTTPException(status_code=400, detail="Invalid Riot ID format")
    game_name, tag_line = request.riot_id.split("#", 1)
    
    # 2. Ingest Data
    ingestion = IngestionService(db)
    try:
        user = await ingestion.get_or_update_user("europe", request.region, game_name, tag_line)
        await ingestion.ingest_match_history(user, count=20)
    except Exception as e:
        import traceback
        traceback.print_exc()
        status = 500
        if "404" in str(e):
            status = 404
        elif "403" in str(e) or "401" in str(e):
            status = 403
        raise HTTPException(status_code=status, detail=f"Analysis failed: {str(e)}")
        
    # 3. Load Data & Train
    df = await load_player_data(db, user.puuid)
    metrics = model_instance.train(df)
    
    if "error" in metrics:
        return {
            "status": "partial", 
            "message": metrics["error"], 
            "user": user, 
            "player_moods": [], 
            "win_probability": 50.0,
            "weighted_averages": {},
            "territory_metrics": {},
            "ddragon_version": DDRAGON_VERSION
        }
    
    # 4. Calculate weighted averages for prediction (Still used for UI display)
    weighted_averages = model_instance.calculate_weighted_averages(df)
    
    # 8. Extract last match stats (Moved up for prediction usage)
    last_match_stats = {}
    if not df.empty:
        last_row = df.iloc[0]  # First row is most recent (ordered by game_creation desc)
        
        # Convert to dict and sanitize NaN/Inf values for JSON
        raw_stats = last_row.to_dict()
        import math
        last_match_stats = {
            k: (0 if (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) else v)
            for k, v in raw_stats.items()
        }
    
    # 6. Analyze player mood from recent matches
    player_moods = model_instance.analyze_player_mood(df)
    
    # 7. Calculate win rate from data (Baseline)
    win_rate = float(df['win'].mean() * 100) if not df.empty else 50.0
    
    # 5. Predict win probability using trained model
    # CHANGED: Now uses LAST MATCH stats per user request ("based on last game predictive indicators")
    raw_model_prediction = model_instance.predict_win_probability(last_match_stats)
    
    # BLEND: Adjust towards 20-game winrate baseline (anchoring) to dampen extreme model outliers
    # Formula: 70% Baseline (Win Rate) + 30% Model (Specific Game Performance)
    # User requested: "take [winrate] as a baseline and adjust from there less agressively"
    win_probability = (win_rate * 0.7) + (raw_model_prediction * 0.3)
    
    # 9. Analyze territorial control from recent matches (limit to 5 for performance)
    territory_metrics = await analyze_territory_for_player(db, user.puuid, request.region)
        
    return {
        "status": "success",
        "user": user,
        "metrics": metrics,
        "win_probability": win_probability,
        "player_moods": player_moods,
        "weighted_averages": weighted_averages,
        "last_match_stats": last_match_stats,
        "win_rate": win_rate,
        "total_matches": len(df),
        "territory_metrics": territory_metrics,
        "ddragon_version": DDRAGON_VERSION
    }


async def analyze_territory_for_player(db: AsyncSession, puuid: str, region: str, limit: int = 5) -> dict:
    """
    Analyze territorial control for a player's recent matches.
    Fetches timeline data for the most recent matches.
    """
    try:
        # Get recent match IDs with participant info
        result = await db.execute(
            select(Participant, Match)
            .join(Match)
            .where(Participant.puuid == puuid)
            .order_by(Match.game_creation.desc())
            .limit(limit)
        )
        
        matches_data = result.all()
        print(f"Territory analysis: Found {len(matches_data)} matches for {puuid[:8]}...")
        
        if not matches_data:
            print("No matches found for territory analysis")
            return {}
        
        # Get regional routing
        regional_routing = REGION_TO_ROUTING.get(region.lower(), "europe")
        print(f"Using regional routing: {regional_routing}")
        
        # Analyze each match's timeline
        territory_results = []
        for row in matches_data:
            participant = row[0]  # First element is Participant
            match = row[1]        # Second element is Match
            
            try:
                # Get participant_id from stats_json (not a model attribute)
                stats = participant.stats_json or {}
                participant_id = stats.get('participantId', 1)  # Default to 1 if not found
                
                print(f"Analyzing timeline for match {match.match_id} (participant {participant_id})...")
                metrics = await analyze_match_territory(
                    riot_service,
                    regional_routing,
                    match.match_id,
                    puuid,
                    participant_id,
                    participant.team_id
                )
                print(f"Got territory metrics: {metrics}")
                territory_results.append(metrics)
            except Exception as e:
                print(f"Error analyzing timeline for {match.match_id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Aggregate results
        if territory_results:
            aggregated = aggregate_territory_metrics(territory_results)
            print(f"Aggregated territory metrics: {aggregated}")
            return aggregated
        
        print("No territory results to aggregate")
        return {}
        
    except Exception as e:
        print(f"Error in territory analysis: {e}")
        import traceback
        traceback.print_exc()
        return {}

