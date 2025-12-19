from fastapi import FastAPI
from investment_agent.agent import root_agent

app = FastAPI(title="Investment Research API")

@app.post("/chat")
async def chat(message: str):
    """Chat with the root investment research agent"""
    # This is a simplified example - ADK has more sophisticated message handling
    response = await root_agent.process_message(message)
    return {"response": response}

@app.get("/agents")
async def list_agents():
    """List available agents"""
    return {
        "agents": [
            "root_agent (investment_agent)",
            "graph_database_agent",
            "investor_research_agent", 
            "investment_research_agent"
        ]
    }

def main():
    print("Investment Research API ready!")
    # For running: uv run adk api_server

if __name__ == "__main__":
    main()