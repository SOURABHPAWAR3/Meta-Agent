import os
import sys
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# ── Make sure parent directory is importable ──────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import MetaAgent, AgentCreator, FunctionCreator

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")


# ── 3 Real-world test cases ───────────────────────────────────────────────────
TEST_CASES = [
    {
        "id": 1,
        "label": "📅 Appointment Booking Bot",
        "request": (
            "Create a support bot for appointment booking. "
            "It should greet, ask for name and date, "
            "and confirm availability via an API."
        )
    },
    {
        "id": 2,
        "label": "💰 Loan Eligibility Qualifier (BFSI)",
        "request": (
            "Build an outbound sales agent for a bank. "
            "It should call leads, introduce the personal loan offer, "
            "ask for monthly income and employment type, "
            "check loan eligibility via API, and transfer "
            "eligible leads to a human agent."
        )
    },
    {
        "id": 3,
        "label": "🛒 E-Commerce Order Support Bot",
        "request": (
            "Create a customer support bot for an e-commerce company. "
            "It should handle order status queries by asking for "
            "the order ID and phone number, fetch the order status "
            "from an API, and offer refund or replacement if "
            "the order is delayed or damaged."
        )
    }
]


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_output(data: dict, filename: str):
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def print_banner(text: str, char: str = "█"):
    print(f"\n{char*60}")
    print(f"  {text}")
    print(f"{char*60}")


def print_section(title: str, data: dict):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def summarize_output(result: dict, case_id: int):
    """Print a clean summary instead of full JSON for readability."""
    plan      = result.get("meta_plan", {})
    config    = result.get("agent_config", {})
    functions = result.get("functions", [])

    print(f"\n{'═'*60}")
    print(f"  SUMMARY — Test Case {case_id}")
    print(f"{'═'*60}")
    print(f"  🎯 Agent Goal     : {plan.get('agent_goal', 'N/A')}")
    print(f"  🤖 Agent Name     : {config.get('agent_name', 'N/A')}")
    print(f"  🗣️  Tone           : {plan.get('persona', {}).get('tone', 'N/A')}")
    print(f"  📋 Tasks          : {len(plan.get('conversation_tasks', []))} steps")
    print(f"  📊 Data Collected : {plan.get('data_to_collect', [])}")
    print(f"  🔧 Functions      : {[f['name'] for f in functions]}")
    print(f"  ⏱️  Max Duration   : {config.get('max_call_duration_seconds', 'N/A')}s")
    print(f"  💬 Flow Steps     : {len(config.get('conversation_flow', []))}")


# ── Pipeline runner ───────────────────────────────────────────────────────────
def run_single_case(case: dict) -> dict:
    """Run the full Meta Agent pipeline for a single test case."""

    print_banner(f"TEST CASE {case['id']} — {case['label']}")
    print(f"\n📝 Request: \"{case['request']}\"")

    # Init agents
    meta_agent    = MetaAgent(api_key=GEMINI_API_KEY)
    agent_creator = AgentCreator(api_key=GEMINI_API_KEY)
    func_creator  = FunctionCreator(api_key=GEMINI_API_KEY)

    # Run pipeline
    meta_plan   = meta_agent.parse_request(case["request"])
    agent_config = agent_creator.create_agent(meta_plan)
    functions   = func_creator.create_functions(meta_plan)

    # Merge
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = {
        "meta": {
            "generated_at": timestamp,
            "test_case_id": case["id"],
            "test_case_label": case["label"],
            "user_request": case["request"],
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

    # Save
    filename = f"case_{case['id']}_{timestamp}.json"
    filepath = save_output(final_output, filename)
    print(f"\n  💾 Saved → {filepath}")

    # Print summary
    summarize_output(final_output, case["id"])

    return final_output


# ── Main runner ───────────────────────────────────────────────────────────────
def run_all_examples():
    print_banner("META AGENT — EXAMPLE TEST SUITE", char="★")
    print(f"  Running {len(TEST_CASES)} test cases...\n")

    results = []
    for i, case in enumerate(TEST_CASES):
        try:
            result = run_single_case(case)
            results.append({
                "case_id": case["id"],
                "label": case["label"],
                "status": "✅ SUCCESS",
                "functions_generated": len(result.get("functions", [])),
                "flow_steps": len(
                    result.get("agent_config", {})
                           .get("conversation_flow", [])
                )
            })
        except Exception as e:
            print(f"\n❌ Case {case['id']} failed: {e}")
            results.append({
                "case_id": case["id"],
                "label": case["label"],
                "status": f"❌ FAILED: {str(e)[:50]}"
            })

        # ── Wait between cases to avoid rate limiting ──────────────────
        if i < len(TEST_CASES) - 1:
            print(f"\n  ⏳ Waiting 15s before next case to avoid rate limits...")
            time.sleep(15)

    # ── Final report ──────────────────────────────────────────────────────
    print_banner("FINAL TEST REPORT", char="★")
    print(f"\n{'Case':<6} {'Label':<38} {'Status':<12} {'Functions':<12} {'Flow Steps'}")
    print(f"{'─'*6} {'─'*38} {'─'*12} {'─'*12} {'─'*10}")
    for r in results:
        print(
            f"{r['case_id']:<6} "
            f"{r['label']:<38} "
            f"{r['status']:<12} "
            f"{r.get('functions_generated', 'N/A'):<12} "
            f"{r.get('flow_steps', 'N/A')}"
        )
    print(f"\n✅ All outputs saved to output/ folder")
    print(f"{'★'*60}\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run_all_examples()