"""
Tools used by the SkillMap Agent.

1. skill_demand_tool  -> built-in Tavily web search (industry demand, salary trends)
2. search_jobs        -> custom tool that calls the JSearch API on RapidAPI
                         (live job listings from LinkedIn, Indeed, Glassdoor, etc.)
"""

import os
import requests
from dotenv import load_dotenv

from langchain_tavily import TavilySearch
from langchain.tools import tool

# Load variables from a local .env file into the process environment.
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing. Add it to your .env file.")
if not RAPIDAPI_KEY:
    raise ValueError("RAPIDAPI_KEY is missing. Add it to your .env file.")


# ---------------------------------------------------------------------------
# Tool 1: Skill demand search (built-in Tavily tool)
# ---------------------------------------------------------------------------
# NOTE: current langchain-tavily no longer accepts `tavily_api_key` as a kwarg
# for authentication in every version -- it reads TAVILY_API_KEY from the
# environment automatically. Passing it explicitly still works on most
# versions, but relying on the env var (loaded above) is the safer path.
skill_demand_tool = TavilySearch(
    max_results=5,
    search_depth="advanced",
    topic="general",
)


# ---------------------------------------------------------------------------
# Tool 2: Live job search (custom tool via JSearch / RapidAPI)
# ---------------------------------------------------------------------------
@tool
def search_jobs(skill: str, location: str) -> list:
    """Search for live job listings requiring a specific skill using the
    JSearch API (aggregates LinkedIn, Indeed, Glassdoor, and more).

    Args:
        skill: The skill or role to search for, e.g. "Generative AI".
        location: The location to search in, e.g. "India".
    """
    print(f"\n[tool call] search_jobs(skill={skill!r}, location={location!r})")

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }
    querystring = {
        "query": f"{skill} in {location}",
        "page": "1",
        "num_pages": "1",
        "country": "in",
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        return [{"error": f"JSearch request failed: {exc}"}]

    data = response.json().get("data", [])

    jobs = []
    for job in data[:10]:
        jobs.append(
            {
                "title": job.get("job_title"),
                "company": job.get("employer_name"),
                "location": job.get("job_city") or job.get("job_country"),
                "employment_type": job.get("job_employment_type"),
                "apply_link": job.get("job_apply_link"),
            }
        )

    return jobs if jobs else [{"error": "No jobs found for that query."}]
