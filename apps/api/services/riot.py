import os
from typing import Dict, Any, Optional
from riotskillissue import RiotClient

from pathlib import Path

# Try to load .env files for local development (optional)
try:
    from dotenv import load_dotenv
    
    current_dir = Path(__file__).resolve().parent
    load_dotenv(current_dir / ".env")
    load_dotenv(current_dir / "dev.env")
    
    # Try parent directories for monorepo structure
    for parent in current_dir.parents:
        env_file = parent / "dev.env"
        if env_file.exists():
            load_dotenv(env_file)
            break
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

API_KEY = os.getenv("RIOT_API_KEY")

class RiotService:
    _instance = None
    client: RiotClient
    
    def __new__(cls):
        if cls._instance is None:
            masked_key = f"{API_KEY[:5]}...{API_KEY[-4:]}" if API_KEY else "None"
            print(f"Initializing RiotService with API Key: {masked_key}")
            cls._instance = super(RiotService, cls).__new__(cls)
            cls._instance.client = RiotClient(api_key=API_KEY)
        return cls._instance

    async def get_account_by_riot_id(self, region_routing: str, game_name: str, tag_line: str) -> Dict[str, Any]:
        return await self.client.account.get_by_riot_id(region_routing, game_name, tag_line)

    async def get_summoner_by_puuid(self, platform_region: str, puuid: str) -> Dict[str, Any]:
        return await self.client.summoner.get_by_puuid(platform_region, puuid)

    async def get_match_history(self, regional_routing: str, puuid: str, count: int = 20, queue: int = 420) -> list:
        return await self.client.match.get_match_ids_by_puuid(
            regional_routing, 
            puuid, 
            queue=queue, 
            count=count
        )

    async def get_match_details(self, regional_routing: str, match_id: str) -> Dict[str, Any]:
        return await self.client.match.get_match(regional_routing, match_id)

    async def get_match_timeline(self, regional_routing: str, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get match timeline data for territorial/positional analysis.
        Returns minute-by-minute position data for all participants.
        """
        try:
            return await self.client.match.get_timeline(regional_routing, match_id)
        except Exception as e:
            print(f"Error fetching timeline for {match_id}: {e}")
            return None

    async def get_league_entries(self, platform_region: str, puuid: str) -> list:
        """
        Get ranked league entries (tier, division, LP) for a summoner by PUUID.
        Returns list of queue entries (RANKED_SOLO_5x5, RANKED_FLEX_SR, etc.)
        """
        try:
            print(f"Fetching league entries for PUUID {puuid[:8]}... on region {platform_region}")
            entries = await self.client.league.get_league_entries_by_puuid(platform_region, puuid)
            print(f"Raw league entries response: {entries}")
            # Convert Pydantic models to dicts if needed
            if entries and hasattr(entries[0], 'model_dump'):
                return [entry.model_dump() for entry in entries]
            return entries
        except Exception as e:
            print(f"Error fetching league entries: {e}")
            import traceback
            traceback.print_exc()
            return []

riot_service = RiotService()


