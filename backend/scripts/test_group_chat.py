import asyncio
import httpx
from uuid import UUID
from typing import List, Dict
import os


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
                "name": "security_analyst",
                "title": "Senior Security Analyst",
                "background": """You are a seasoned security analyst with expertise in 
                threat detection, incident response, and digital forensics. You excel at 
                analyzing security logs, identifying attack patterns, and conducting 
                root cause analysis.""",
                "agent_type": "assistant",
                "llm_config": {
                    "temperature": 0.7,
                    "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
                },
                "tool_config": None
            },
            {
                "name": "network_engineer",
                "title": "Network Security Engineer",
                "background": """You are a network security expert specializing in 
                infrastructure security, firewall configuration, and network monitoring. 
                You understand network protocols, security architecture, and best practices 
                for network defense.""",
                "agent_type": "assistant",
                "llm_config": {
                    "temperature": 0.7,
                    "model": os.getenv("AZURE_OPENAI_MODEL", "gpt-4o-mini")
                },
                "tool_config": None
            },
            {
                "name": "incident_manager",
                "title": "Incident Response Manager",
                "background": """You are an incident response manager with experience in 
                coordinating security incidents, managing communication with stakeholders, 
                and implementing incident response procedures. You focus on business impact, 
                compliance requirements, and recovery strategies.""",
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
            "title": "Security Incident Analysis and Response2",
            "context": "Analyze and respond to a potential data breach in our cloud infrastructure",
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
        We've detected unusual activity in our cloud infrastructure suggesting a potential 
        data breach. Our monitoring systems have identified:
        1. Unexpected outbound traffic from several database servers
        2. Multiple failed login attempts from foreign IP addresses
        3. Unusual process execution patterns on critical systems
        4. Several modified system files on application servers

        Please analyze the situation and develop an immediate response plan addressing:
        1. Initial assessment and threat evaluation
        2. Immediate containment measures
        3. Investigation and evidence collection approach
        4. Communication strategy for stakeholders
        5. Long-term remediation recommendations
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