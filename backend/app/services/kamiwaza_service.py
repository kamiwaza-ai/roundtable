import httpx
from typing import List, Dict, Any
from urllib.parse import urlparse

from ..config import Settings, get_settings

class KamiwazaService:
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        if not self.settings.kamiwaza_api_uri:
            raise ValueError("KAMIWAZA_API_URI environment variable is not set")
        # Parse the API URI to get the host
        parsed_uri = urlparse(self.settings.kamiwaza_api_uri)
        self.default_host = parsed_uri.hostname
        # Fix: Set verify_ssl to False for self-signed certificates
        self.verify_ssl = False  # Don't verify SSL since we're dealing with self-signed certs
        # Ensure we use HTTPS if available
        self.api_uri = self.settings.kamiwaza_api_uri
        if parsed_uri.scheme == "http":
            self.api_uri = self.api_uri.replace("http://", "https://", 1)

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Fetch available deployed Kamiwaza models"""
        async with httpx.AsyncClient(verify=self.verify_ssl, timeout=30.0) as client:
            response = await client.get(f"{self.api_uri}/api/serving/deployments")
            response.raise_for_status()
            deployments = response.json()
            
            # Filter to only include deployed models and format response
            return [
                {
                    "model_name": d["m_name"],
                    "status": d["status"],
                    "instances": [
                        {
                            "host_name": self.default_host,
                            "port": d["lb_port"],
                            "url": f"http://{self.default_host}:{d['lb_port']}/v1"
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