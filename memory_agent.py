"""
SkillMap Agent with short-term memory (per-thread conversation history).

Run with:
    python memory_agent.py

Then chat with it. Follow-up questions like "tell me more about the second
job" will work because InMemorySaver keeps the message history for the
thread_id used below.

Note: InMemorySaver keeps state in RAM only -- history is lost when the
script exits. For production, swap it for SqliteSaver or PostgresSaver.
"""

import os
from dotenv import load_dotenv

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from tools import skill_demand_tool, search_jobs

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing. Add it to your .env file.")

model = init_chat_model(
    "google_genai:gemini-3.6-flash",
    api_key=GOOGLE_API_KEY,
)

system_prompt = """You are a Skill-to-Career Mapping assistant that helps
students understand skill demand and find matching job opportunities.

You have access to these tools:
- skill_demand_tool: Search for industry demand, salary insights, and career trends
- search_jobs: Find actual job listings requiring specific skills

Help the student by researching the skill they ask about and finding relevant
opportunities. Present results in a clean, readable format with clear sections
and proper spacing. Include all job details with apply links. Don't use
markdown formatting. Remember earlier parts of the conversation, since users
may ask follow-up questions like "tell me more about job 2"."""

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[skill_demand_tool, search_jobs],
    system_prompt=system_prompt,
    checkpointer=checkpointer,
)

# Same thread_id across calls = same conversation. A different thread_id
# would start a brand new, unrelated conversation.
config = {"configurable": {"thread_id": "1"}}


def extract_text(content) -> str:
    """Newer Gemini/LangChain responses return .content as either a plain
    string, or a list of content blocks like
    [{'type': 'text', 'text': '...'}, ...]. This normalizes both cases into
    clean, readable text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts).strip()
    return str(content)


def chat(query: str) -> str:
    response = agent.invoke({"messages": [{"role": "user", "content": query}]}, config=config)
    return extract_text(response["messages"][-1].content)


if __name__ == "__main__":
    print("SkillMap Agent (type 'quit' to exit)\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        answer = chat(user_input)
        print(f"\nAgent: {answer}\n")