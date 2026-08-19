from datetime import datetime, timezone
import time
from dotenv import load_dotenv
from google import genai
import os
import json
from src.monitoring.usage import LLMUsage
from src.monitoring.cost import calculate_cost
from src.monitoring.database import save_usage_record

# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# 2. READ GEMINI API KEY
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")


# ============================================================
# 3. CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=api_key)


# ============================================================
# 4. CLASSIFY USER INTENT
# ============================================================


def classify_intent(question):

    prompt = f"""
You are an intent classification system for CloudDesk,
a customer support application.

Classify the user's message into exactly ONE of these
three categories:

1. conversation
   - Greetings
   - Casual conversation
   - Thanks
   - Goodbye
   - Questions about the assistant itself

2. support
   - Questions related to CloudDesk
   - Account problems
   - Password or login issues
   - Billing
   - Invoices
   - Subscriptions
   - Payments
   - Integrations
   - Security
   - Notifications
   - Data export
   - Support tickets
   - User management
   - Any problem that appears related to CloudDesk

3. unknown
   - Questions unrelated to CloudDesk
   - General knowledge questions
   - Entertainment
   - Sports
   - Weather
   - Politics
   - Any topic outside CloudDesk support

IMPORTANT:
Return ONLY valid JSON.

The JSON must contain exactly one field called "intent".

Valid responses are:

{{"intent": "conversation"}}

OR

{{"intent": "support"}}

OR

{{"intent": "unknown"}}

USER MESSAGE:

{question}
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", contents=prompt
    )
    response_text = response.text.strip()
    try:

        result = json.loads(response_text)

        intent = result.get("intent", "unknown").lower().strip()

        if intent in ["conversation", "support", "unknown"]:
            return intent

    except json.JSONDecodeError:

        pass

    # --------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------

    return "unknown"


# ============================================================
# 5. GENERATE FINAL ANSWER
# ============================================================


def generate_answer(question, context):

    prompt = f"""
You are CloudDesk's customer support assistant.

Answer the customer's question using ONLY the
knowledge-base context below.

Rules:
- Do not invent information.
- Do not use outside knowledge.
- If the answer is not contained in the context,
  say that you do not know.
- Be concise and helpful.

KNOWLEDGE BASE:

{context}

CUSTOMER QUESTION:

{question}
"""

    start_time = time.perf_counter()

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", contents=prompt
    )

    end_time = time.perf_counter()

    latency_ms = (end_time - start_time) * 1000

    cost_result = calculate_cost(
        input_tokens=response.usage_metadata.prompt_token_count,
        output_tokens=response.usage_metadata.candidates_token_count,
        input_price_per_million=5.0,
        output_price_per_million=15.0,
    )

    print("********************************************************")
    print("input_tokens", response.usage_metadata.prompt_token_count)
    print("output_tokens", response.usage_metadata.candidates_token_count)
    print("total_tokens", response.usage_metadata.total_token_count)
    print("request_id", response.response_id)
    print(f"Latency: {latency_ms:.2f} ms")
    print("timestamp", datetime.now(timezone.utc))
    print("Input Cost:", cost_result["input_cost"])
    print("Output Cost:", cost_result["output_cost"])
    print("Total Cost:", cost_result["total_cost"])
    print("#########################################################")
    
    usage_record = LLMUsage(
    provider="Google",
    model="gemini-3.1-flash-lite",
    request_id=response.response_id,
    timestamp=datetime.now(timezone.utc),
    input_tokens=response.usage_metadata.prompt_token_count,
    output_tokens=response.usage_metadata.candidates_token_count,
    total_tokens=response.usage_metadata.total_token_count,
    latency_ms=latency_ms,
    input_cost=cost_result["input_cost"],
    output_cost=cost_result["output_cost"],
    total_cost=cost_result["total_cost"],
    status="success",
    )
    
    #print("usage_record", usage_record)    
    save_usage_record(usage_record)

    return response.text
