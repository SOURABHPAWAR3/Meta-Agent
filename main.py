import os
import json
from datetime import datetime
from dotenv import load_dotenv

from agents import MetaAgent, AgentCreator, FunctionCreator

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")


# ── Output saver ─────────────────────────────────────────────────────────────
def save_output(data: dict, filename: str):
    """Save generated JSON to the output/ folder."""
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved → {filepath}")
    return filepath


# ── Pretty printer ────────────────────────────────────────────────────────────
def print_section(title: str, data: dict):
    """Print a labeled JSON section to terminal."""
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ── Core pipeline ─────────────────────────────────────────────────────────────
def run_meta_agent_pipeline(user_request: str) -> dict:
    """
    Full Meta Agent pipeline:
    1. MetaAgent     → parses user request → structured plan
    2. AgentCreator  → plan → CX agent configuration
    3. FunctionCreator → plan → function call definitions
    4. Merge all outputs → final deployable JSON
    """

    print(f"\n{'█'*60}")
    print(f"  META AGENT PIPELINE STARTED")
    print(f"{'█'*60}")
    print(f"\n📝 User Request:\n  \"{user_request}\"")

    # ── Step 1: MetaAgent parses the request ──────────────────────────────
    meta_agent     = MetaAgent(api_key=GEMINI_API_KEY)
    meta_plan      = meta_agent.parse_request(user_request)
    print_section("STEP 1 — META AGENT PLAN", meta_plan)

    # ── Step 2: AgentCreator builds agent config ──────────────────────────
    agent_creator  = AgentCreator(api_key=GEMINI_API_KEY)
    agent_config   = agent_creator.create_agent(meta_plan)
    print_section("STEP 2 — AGENT CONFIGURATION", agent_config)

    # ── Step 3: FunctionCreator builds function definitions ───────────────
    func_creator   = FunctionCreator(api_key=GEMINI_API_KEY)
    functions      = func_creator.create_functions(meta_plan)
    print_section("STEP 3 — FUNCTION DEFINITIONS", functions)

    # ── Step 4: Merge into final deployable output ────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    final_output = {
        "meta": {
            "generated_at": timestamp,
            "user_request": user_request,
            "platform_target": "VoiceOwl-compatible CX Agent",
            "pipeline_version": "1.0.0"
        },
        "meta_plan": meta_plan,
        "agent_config": agent_config.get("agent_config", agent_config),
        "functions": functions.get("functions", []),
        "deployment_note": (
            "This configuration is compatible with enterprise voice CX "
            "platforms like VoiceOwl. To deploy: pass agent_config to "
            "your platform's agent creation endpoint and register each "
            "function definition as a callable tool."
        )
    }

    print_section("FINAL DEPLOYABLE OUTPUT", final_output)

    # ── Step 5: Save to output/ folder ────────────────────────────────────
    filename = f"cx_agent_{timestamp}.json"
    save_output(final_output, filename)

    print(f"\n{'█'*60}")
    print(f"  ✅ PIPELINE COMPLETE")
    print(f"{'█'*60}\n")

    return final_output


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # ── Example from the task document ───────────────────────────────────
    user_request = (
        "Create a support bot for appointment booking. "
        "It should greet, ask for name and date, "
        "and confirm availability via an API."
    )

    result = run_meta_agent_pipeline(user_request)