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

from fastapi.responses import StreamingResponse
import json

@router.post("/analyze")
async def analyze_player(request: AnalyzeRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # 1. Parse Riot ID
    if "#" not in request.riot_id:
        raise HTTPException(status_code=400, detail="Invalid Riot ID format")
    
    game_name, tag_line = request.riot_id.split("#", 1)

    async def analysis_generator():
        try:
            yield json.dumps({"type": "progress", "message": "Finding user account...", "percent": 5}) + "\n"
            
            # 2. Ingest Data
            ingestion = IngestionService(db)
            try:
                user = await ingestion.get_or_update_user("europe", request.region, game_name, tag_line)
                if not user:
                    yield json.dumps({"type": "error", "message": "User not found"}) + "\n"
                    return

                # Stream match ingestion progress
                match_count = 0
                async for progress in ingestion.ingest_match_history_generator(user, count=20):
                    current = progress["current"]
                    total = progress["total"]
                    percent = 10 + int((current / total) * 60) # Map 0-100% of matches to 10-70% total progress
                    yield json.dumps({"type": "progress", "message": progress["status"], "percent": percent}) + "\n"
                    match_count = total

            except Exception as e:
                import traceback
                traceback.print_exc()
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"
                return

            yield json.dumps({"type": "progress", "message": "Training AI model...", "percent": 80}) + "\n"
            
            # 3. Load Data & Train
            df = await load_player_data(db, user.puuid)
            metrics = model_instance.train(df)
            
            if "error" in metrics:
                # Handle partial analysis
                yield json.dumps({"type": "result", "data": {
                    "status": "partial", 
                    "message": metrics["error"], 
                    "user": user, 
                    # ... default empty structure ...
                    "win_probability": 50.0
                }}) + "\n"
                return
            
            yield json.dumps({"type": "progress", "message": "Analyzing playstyle...", "percent": 90}) + "\n"

            # 4. Calculate weighted averages
            weighted_averages = model_instance.calculate_weighted_averages(df)
            
            # 8. Extract last match stats
            last_match_stats = {}
            if not df.empty:
                last_row = df.iloc[0]
                raw_stats = last_row.to_dict()
                import math
                last_match_stats = {
                    k: (0 if (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) else v)
                    for k, v in raw_stats.items()
                }
            
            # 6. Analyze player mood
            player_moods = model_instance.analyze_player_mood(df)
            
            # 7. Calculate win rate
            win_rate = float(df['win'].mean() * 100) if not df.empty else 50.0
            
            # 5. Predict win probability
            raw_model_prediction = model_instance.predict_win_probability(last_match_stats)
            win_probability = (win_rate * 0.7) + (raw_model_prediction * 0.3)
            
            yield json.dumps({"type": "progress", "message": "Analyzing territory...", "percent": 95}) + "\n"

            # 9. Analyze territorial control
            territory_metrics = await analyze_territory_for_player(db, user.puuid, request.region)
                
            result_data = {
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
            
            # Use a custom JSON encoder for SQLAlchemy objects if needed, or rely on Pydantic/FastAPI
            # But since we are manually dumping to JSON line, we need to be careful with SQLAlchemy objects.
            # Convert user object to dict manually to be safe for json.dumps
            result_data["user"] = {
                "game_name": user.game_name,
                "tag_line": user.tag_line,
                "region": user.region,
                "profile_icon_id": user.profile_icon_id,
                "summoner_level": user.summoner_level,
                "puuid": user.puuid
            }
            
            yield json.dumps({"type": "result", "data": result_data}) + "\n"
        
        except Exception as e:
             import traceback
             traceback.print_exc()
             yield json.dumps({"type": "error", "message": f"Server error: {str(e)}"}) + "\n"

    return StreamingResponse(analysis_generator(), media_type="application/x-ndjson")


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

