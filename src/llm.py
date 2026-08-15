from dotenv import load_dotenv
from google import genai
import os
import json


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# 2. READ GEMINI API KEY
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )


# ============================================================
# 3. CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=api_key
)


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
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    response_text = response.text.strip()

    try:

        result = json.loads(
            response_text
        )

        intent = result.get(
            "intent",
            "unknown"
        ).lower().strip()

        if intent in [
            "conversation",
            "support",
            "unknown"
        ]:
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

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text