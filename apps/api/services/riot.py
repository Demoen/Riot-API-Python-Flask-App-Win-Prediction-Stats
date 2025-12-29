import os
from typing import Dict, Any, Optional
from riotskillissue import RiotClient
from dotenv import load_dotenv

load_dotenv()

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

riot_service = RiotService()

