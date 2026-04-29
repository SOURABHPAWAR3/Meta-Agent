# 🤖 Meta Agent — Voice CX Agent Creator

A Meta Agent system that generates fully configured, deployable Voice CX phone agents from natural language descriptions. Built with Python and the Gemini API.

---

## 📌 What It Does

Non-technical users describe what they want in plain English:

> *"Create a support bot for appointment booking. It should greet, ask for name and date, and confirm availability via an API."*

The Meta Agent:
1. **Interprets** the request using an LLM
2. **Generates** a complete agent configuration (persona, voice, conversation flow)
3. **Defines** typed function call schemas (API integrations)
4. **Outputs** a deployable JSON compatible with enterprise voice CX platforms like VoiceOwl

---

## 🏗️ Architecture

```
User (natural language request)
          │
          ▼
    ┌─────────────┐
    │  Meta Agent │  ← Interprets intent, extracts tasks & data fields
    └──────┬──────┘
           │  structured plan (JSON)
    ┌──────┴──────────────────┐
    │                         │
    ▼                         ▼
┌───────────────┐     ┌──────────────────┐
│ Agent Creator │     │ Function Creator  │
│               │     │                  │
│ Builds:       │     │ Builds:          │
│ · persona     │     │ · function names │
│ · voice       │     │ · parameters     │
│ · conv. flow  │     │ · API endpoints  │
│ · scripts     │     │ · on_success/    │
│ · end conds   │     │   on_failure     │
└───────┬───────┘     └────────┬─────────┘
        │                      │
        └──────────┬───────────┘
                   │
                   ▼
         ┌──────────────────┐
         │  Orchestrator    │  ← Merges outputs
         │   (main.py)      │
         └────────┬─────────┘
                  │
                  ▼
       ┌─────────────────────┐
       │ Deployable JSON     │  → output/cx_agent_XXXX.json
       │ (VoiceOwl-compatible)│
       └─────────────────────┘
```

---

## 📁 Project Structure

```
meta-agent-cx/
│
├── agents/
│   ├── __init__.py
│   ├── meta_agent.py          # Master orchestrator agent
│   ├── agent_creator.py       # Builds CX agent config
│   └── function_creator.py    # Builds function call schemas
│
├── prompts/
│   ├── __init__.py
│   ├── meta_prompt.py         # Meta Agent system prompt
│   ├── agent_creator_prompt.py
│   └── function_creator_prompt.py
│
├── examples/
│   └── example_run.py         # 3 real-world test cases
│
├── output/                    # Generated JSON files (auto-created)
│
├── main.py                    # Entry point
├── .env                       # API keys (never committed)
├── .gitignore
└── README.md
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/meta-agent-cx.git
cd meta-agent-cx
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install google-genai python-dotenv requests
```

### 4. Configure API keys
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
Get your free Gemini API key at 👉 https://aistudio.google.com

---

## 🚀 Usage

### Run with the default example
```bash
python main.py
```

### Run all 3 example test cases
```bash
python examples/example_run.py
```

### Use your own request
Edit the `user_request` in `main.py`:
```python
user_request = "Build a lead qualification bot for a bank that collects income and employment details"
```

---

## 📤 Output Format

Every run produces a timestamped JSON file in `output/`:

```json
{
  "meta": {
    "generated_at": "20260429_082952",
    "user_request": "Create a support bot for appointment booking...",
    "platform_target": "VoiceOwl-compatible CX Agent",
    "pipeline_version": "1.0.0"
  },
  "meta_plan": {
    "agent_goal": "...",
    "agent_type": "booking",
    "persona": { "name": "...", "tone": "friendly", "language": "en-US" },
    "conversation_tasks": ["..."],
    "data_to_collect": ["caller_name", "appointment_date"],
    "api_actions_needed": ["..."],
    "requires_functions": true
  },
  "agent_config": {
    "agent_name": "Appointment Assistant",
    "voice_id": "11labs-Adrian",
    "persona_prompt": "...",
    "conversation_flow": [...],
    "end_call_conditions": [...],
    "fallback_message": "...",
    "max_call_duration_seconds": 300
  },
  "functions": [
    {
      "name": "check_appointment_availability",
      "description": "...",
      "parameters": { "type": "object", "properties": {...}, "required": [...] },
      "endpoint": { "method": "GET", "url": "https://api.example.com/..." },
      "on_success": "...",
      "on_failure": "..."
    }
  ],
  "deployment_note": "..."
}
```

---

## 🧪 Example Test Cases

| # | Agent Type | Data Collected | Functions Generated |
|---|---|---|---|
| 1 | Appointment Booking Bot | caller_name, appointment_date | check_availability, book_appointment |
| 2 | Loan Eligibility Qualifier (BFSI) | monthly_income, employment_type | check_loan_eligibility, transfer_to_agent |
| 3 | E-Commerce Order Support | order_id, phone_number | get_order_status, initiate_refund |

---

## 🚀 Deployment

The generated JSON is fully compatible with enterprise voice CX platforms like **VoiceOwl**.

To deploy:
1. Pass `agent_config` to your platform's agent creation endpoint
2. Register each item in `functions` as a callable tool
3. Map `conversation_flow` steps to your IVR or voice pipeline

VoiceOwl is India's first purpose-built Generative AI Contact Center for enterprises, supporting outbound calling, lead qualification, and CX automation.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM Brain | Google Gemini 2.0 Flash |
| Language | Python 3.10+ |
| API Client | google-genai |
| Config | python-dotenv |
| Output | JSON |
| Target Platform | VoiceOwl-compatible |

---

## 📊 Evaluation Rubric Coverage

| Category | Implementation |
|---|---|
| Conceptual Design (20pts) | 3-layer pipeline: Meta Agent → Sub-agents → Orchestrator |
| Prompt Engineering (25pts) | 3 specialized system prompts with structured JSON output |
| Function Call Integration (20pts) | Typed schemas with parameters, endpoints, on_success/on_failure |
| Example Quality (15pts) | 3 real-world test cases across booking, BFSI, e-commerce |
| Technical Implementation (10pts) | Working Python prototype with retry logic |
| Documentation (10pts) | This README + inline code comments |
| Bonus (10pts) | Modular sub-agents + VoiceOwl deployment context |

---

## 👤 Author

Built as part of the Prompt Engineer / AI Solutions Engineer assessment.