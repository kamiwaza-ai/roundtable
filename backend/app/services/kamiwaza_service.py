import httpx
from typing import List, Dict, Any

from ..config import Settings, get_settings

class KamiwazaService:
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        if not self.settings.kamiwaza_api_uri:
            raise ValueError("KAMIWAZA_API_URI environment variable is not set")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Fetch available deployed Kamiwaza models"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.settings.kamiwaza_api_uri}/api/serving/deployments")
            response.raise_for_status()
            deployments = response.json()
            
            # Filter to only include deployed models and format response
            return [
                {
                    "model_name": d["m_name"],
                    "status": d["status"],
                    "instances": [
                        {
                            "host_name": instance.get("host_name") or "localhost",
                            "port": d["lb_port"],
                            "url": f"http://{instance.get('host_name') or 'localhost'}:{d['lb_port']}/v1"
                        }
                        for instance in d["instances"]
                    ],
                    "capabilities": {
                        "chat_completion": True,
                        "text_completion": True,
                        "embeddings": False
                    }
                }
                for d in deployments
                if d["status"] == "DEPLOYED"
            ] 