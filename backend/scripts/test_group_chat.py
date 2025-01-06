import asyncio
import httpx
from uuid import UUID
from typing import List, Dict
import os
from app.models.round_table import RoundTable
from app.models.round_table_participant import RoundTableParticipant

async def create_agent(client: httpx.AsyncClient, agent_data: Dict) -> Dict:
    """Create an agent via the API"""
    response = await client.post("/api/v1/agents/", json=agent_data)
    response.raise_for_status()
    return response.json()

async def create_round_table(client: httpx.AsyncClient, round_table_data: Dict) -> Dict:
    """Create a round table via the API"""
    response = await client.post("/api/v1/round-tables/", json=round_table_data)
    response.raise_for_status()
    return response.json()

async def start_discussion(
    client: httpx.AsyncClient, 
    round_table_id: UUID, 
    prompt: str
) -> Dict:
    """Start a round table discussion"""
    response = await client.post(
        f"/api/v1/round-tables/{round_table_id}/discuss",
        params={"discussion_prompt": prompt}
    )
    response.raise_for_status()
    return response.json()

async def main():
    # API base URL
    base_url = "http://localhost:8000"
    
    # Create client with longer timeout
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(timeout=300.0)  # 5 minutes instead of default 5 seconds
    ) as client:
        # Create test agents
        agents = []
        agent_configs = [
            {
                "name": "business_analyst",
                "title": "Senior Business Analyst",
                "background": """You are an experienced business analyst skilled in market research,
                data analysis, and strategic planning. Focus on data-driven insights and practical
                business implications.""",
                "agent_type": "assistant",
                "llm_config": {
                    "temperature": 0.7,
                    "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
                },
                "tool_config": None
            },
            {
                "name": "strategy_consultant",
                "title": "Management Consultant",
                "background": """You are a strategic management consultant with expertise in
                corporate strategy, market entry, and competitive analysis. Provide strategic
                frameworks and actionable recommendations.""",
                "agent_type": "assistant",
                "llm_config": {
                    "temperature": 0.7,
                    "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
                },
                "tool_config": None
            },
            {
                "name": "product_manager",
                "title": "Senior Product Manager",
                "background": """You are a seasoned product manager with experience in launching 
                and scaling software products. Focus on user needs, product-market fit, and 
                feature prioritization. Provide insights on product positioning and user adoption.""",
                "agent_type": "assistant",
                "llm_config": {
                    "temperature": 0.7,
                    "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
                },
                "tool_config": None
            }
        ]

        print("Creating agents...")
        for config in agent_configs:
            agent = await create_agent(client, config)
            agents.append(agent)
            print(f"Created agent: {agent['name']} (ID: {agent['id']})")

        # Create round table
        round_table_data = {
            "title": "Test Strategy Discussion",
            "context": "Develop market entry strategy for a new product",
            "participant_ids": [agent["id"] for agent in agents],
            "settings": {
                "max_rounds": 10,
                "speaker_selection_method": "auto",
                "allow_repeat_speaker": True,
                "send_introductions": True
            }
        }

        print("\nCreating round table...")
        round_table = await create_round_table(client, round_table_data)
        print(f"Created round table: {round_table['title']} (ID: {round_table['id']})")

        # Start the discussion
        discussion_prompt = """
        We need to develop a market entry strategy for a new AI-powered productivity tool.
        Consider the following aspects:
        1. Target market selection
        2. Competitive analysis
        3. Pricing strategy
        4. Go-to-market approach
        
        Please analyze these aspects and provide recommendations.
        """

        print("\nStarting discussion...")
        result = await start_discussion(client, round_table["id"], discussion_prompt)
        
        print("\nDiscussion completed!")
        print("\nChat History:")
        
        # The chat history is in the result directly
        chat_history = result.get("chat_history", [])
        for entry in chat_history:
            # Each entry has a format like "business_analyst (to chat_manager): message content"
            print(f"\n{entry}")
            print("-" * 80)

        # If there's a summary, print it too
        if "summary" in result:
            print("\nDiscussion Summary:")
            print(result["summary"])

if __name__ == "__main__":
    asyncio.run(main()) 