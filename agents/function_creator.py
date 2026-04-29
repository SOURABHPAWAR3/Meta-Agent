import json
import time
import re
from google import genai
from prompts.function_creator_prompt import (
    FUNCTION_CREATOR_SYSTEM_PROMPT,
    FUNCTION_CREATOR_USER_TEMPLATE
)


class FunctionCreator:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model  = "gemini-2.0-flash"
        self.system_prompt = FUNCTION_CREATOR_SYSTEM_PROMPT

    def create_functions(self, meta_plan: dict, retries: int = 3) -> dict:
        if not meta_plan.get("requires_functions", True):
            print("[FunctionCreator] No functions required.")
            return {"functions": []}

        prompt = FUNCTION_CREATOR_USER_TEMPLATE.format(
            meta_plan=json.dumps(meta_plan, indent=2)
        )
        print("\n[FunctionCreator] Building function definitions...")

        for attempt in range(1, retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=self.system_prompt,
                        temperature=0.3,
                    )
                )
                raw       = self._clean_json(response.text.strip())
                functions = json.loads(raw)
                print("[FunctionCreator] ✅ Functions created successfully")
                return functions

            except Exception as e:
                error_str = str(e)
                if ("503" in error_str or "429" in error_str) and attempt < retries:
                    wait = self._get_retry_wait(error_str, attempt)
                    print(f"[FunctionCreator] ⚠️  Rate limit hit, retrying in {wait}s... (attempt {attempt}/{retries})")
                    time.sleep(wait)
                else:
                    print(f"[FunctionCreator] ❌ Failed after {attempt} attempts: {e}")
                    raise

    def _get_retry_wait(self, error_str: str, attempt: int) -> int:
        match = re.search(r'retryDelay.*?(\d+)s', error_str)
        if match:
            return int(match.group(1)) + 2
        return attempt * 10

    def _clean_json(self, raw: str) -> str:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return raw.strip()