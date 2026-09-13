"""
SkillMap Agent (no memory) - single-turn version.

Run with:
    python agent.py "What's the demand for generative ai in the industry
    and show me related job openings in India"
"""

import sys
import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from tools import skill_demand_tool, search_jobs

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

# --- Step 1 & Defining the model --------------------------------------------
# Model string uses the "provider:model" format. gemini-3.6-flash is the
# current generally-available Flash model (Sept 2026). If it's ever retired,
# swap in the newest Flash model listed at https://ai.google.dev/gemini-api/docs/models
model = init_chat_model(
    "google_genai:gemini-3.6-flash",
    api_key=GOOGLE_API_KEY,
)

# --- Step 4: System prompt ---------------------------------------------------
system_prompt = """You are a Skill-to-Career Mapping assistant that helps
students understand skill demand and find matching job opportunities.

You have access to these tools:
- skill_demand_tool: Search for industry demand, salary insights, and career trends
- search_jobs: Find actual job listings requiring specific skills

Help the student by researching the skill they ask about and finding relevant
opportunities. Present results in a clean, readable format with clear sections
and proper spacing. Include all job details with apply links. Don't use
markdown formatting."""

# --- Step 1 & 4: Create the agent --------------------------------------------
agent = create_agent(
    model=model,
    tools=[skill_demand_tool, search_jobs],
    system_prompt=system_prompt,
)


def extract_text(content) -> str:
    """Gemini/Anthropic responses can come back as a plain string OR as a
    list of content blocks like [{'type': 'text', 'text': '...'}, ...].
    This pulls out just the readable text either way."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


def run(query: str) -> str:
    """Step 5: Execute the agent for a single query."""
    response = agent.invoke({"messages": [{"role": "user", "content": query}]})
    return extract_text(response["messages"][-1].content)


if __name__ == "__main__":
    user_query = " ".join(sys.argv[1:]) or (
        "What's the demand for generative AI in the industry and show me "
        "related job openings in India"
    )
    print(run(user_query))