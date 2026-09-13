# SkillMap Agent

A LangChain agent that answers "what's the demand for skill X, and what jobs
are open right now for it in India" using Google Gemini for reasoning, Tavily
for market-research search, and JSearch (RapidAPI) for live job listings.

## Quick start in VS Code

1. **Unzip** `skillmap-agent.zip` anywhere on your computer.
2. **Open the folder in VS Code**: `File → Open Folder...` → select the
   unzipped `skillmap-agent` folder.
3. **Install the Python extension** if you don't have it — VS Code will
   prompt you (it's listed in `.vscode/extensions.json`). Click Install.
4. **Open a terminal in VS Code**: `Terminal → New Terminal`.
5. **Create a virtual environment** (run in that terminal):
   ```bash
   python -m venv venv
   ```
6. **Select the interpreter**: press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac) →
   type "Python: Select Interpreter" → choose the one inside `./venv`.
   Close and reopen the terminal so it activates automatically (you'll see
   `(venv)` at the start of the prompt). If it doesn't auto-activate, run:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
7. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
8. **Add your API keys**: copy `.env.example` to a new file named `.env`
   (same folder), then open `.env` and paste in your real keys (see "API
   keys" below for where to get them). `.env` is already git-ignored so you
   won't accidentally commit your keys.
9. **Run it** — either:
   - In the terminal: `python agent.py "your question here"`
   - Or press `F5` in VS Code and pick one of the two run configurations
     ("Run: agent.py" or "Run: memory_agent.py") from the dropdown — these
     are pre-configured in `.vscode/launch.json`.

## API keys

You need three free-tier keys:
- **Google AI Studio** (Gemini): https://aistudio.google.com/app/apikey
- **Tavily**: https://app.tavily.com
- **RapidAPI / JSearch**: subscribe to the free plan at
  https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

## Run it

```bash
# single question, no memory
python agent.py "What's the demand for Generative AI and show me jobs in India"

# interactive chat with memory (follow-up questions work)
python memory_agent.py
```

## Files

- `tools.py` — the two tools: `skill_demand_tool` (Tavily) and `search_jobs` (custom JSearch tool)
- `agent.py` — single-turn agent (Steps 1–5 from the course)
- `memory_agent.py` — same agent + `InMemorySaver` checkpointer + `thread_id`, run as a chat loop

---



Once this runs, the same pattern (Tavily tool + one custom `@tool` + `create_agent`)
extends directly to the other agent ideas in the course: Interview Prep Agent,
Salary Insights Agent, Course Finder Agent, Skill Comparison Agent, etc. Swap
the tools and system prompt, keep the scaffolding.
