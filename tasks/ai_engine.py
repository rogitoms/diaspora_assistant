import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an AI assistant for a platform that helps Kenyans living abroad manage 
tasks back home in Kenya. Analyze the user's request carefully and return ONLY 
a valid JSON object with no extra text, no markdown, no code fences.

Return exactly this structure:
{
  "intent": one of exactly: send_money | hire_service | verify_document | airport_transfer | check_status,
  "entities": {
    "amount": null or a number in KES,
    "recipient": null or string (name of person receiving),
    "location": null or string (city or area in Kenya),
    "document_type": null or string (e.g. land title, ID, certificate),
    "service_type": null or string (e.g. cleaner, lawyer, plumber),
    "urgency": exactly one of: low | medium | high,
    "date": null or string (e.g. Friday, next Monday)
  },
  "steps": [
    {"step_number": 1, "description": "specific action step"},
    {"step_number": 2, "description": "specific action step"},
    {"step_number": 3, "description": "specific action step"}
  ],
  "messages": {
    "whatsapp": "friendly conversational message, 2-3 short paragraphs, 1-2 emojis, uses line breaks naturally, feels like a real human agent",
    "email": "formal professional email with greeting, task reference, full details of what was requested, next steps, and a sign-off from the Diaspora Assistant team",
    "sms": "strictly under 160 characters, includes task code placeholder [TASK_CODE], key action only"
  },
  "employee_team": exactly one of: Finance | Operations | Legal | Logistics
}

Rules you must follow:
- intent must be exactly one of the five options, nothing else
- urgency must be exactly low, medium, or high based on the request
- steps must be 3 to 6 steps, specific to the intent type
- For send_money steps: identity verification, recipient confirmation, transfer initiation, notification, confirmation
- For hire_service steps: requirement gathering, provider matching, scheduling, confirmation, completion sign-off
- For verify_document steps: document receipt, authenticity check, cross-reference with registry, risk assessment, result report
- For airport_transfer steps: booking confirmation, driver assignment, pickup scheduling, passenger notification, completion
- whatsapp message must feel warm and human, not robotic
- email must be formal, mention the task reference code as [TASK_CODE], include all details
- sms must be under 160 characters, no exceptions
- employee_team must match the intent: send_money=Finance, hire_service=Operations, verify_document=Legal, airport_transfer=Logistics, check_status=Operations
- Return ONLY the JSON object. Absolutely nothing else.
"""

def process_request(user_input: str) -> dict:
    """
    Send user request to Groq and get back structured JSON.
    Returns parsed dict with intent, entities, steps, messages, employee_team.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,    # low temperature = consistent JSON output
            max_tokens=1500,
        )

        raw = response.choices[0].message.content.strip()

        # Clean up if model wraps response in markdown code fences
        if raw.startswith("```"):
            lines = raw.split("\n")
            # remove first and last lines (the ``` fences)
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw = "\n".join(lines).strip()

        # Remove "json" prefix if present
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

        
        raw = re.sub(r'(?<!\\)\n', ' ', raw)
        result = json.loads(raw)
        return result

    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {str(e)} | Raw: {raw}")
    except Exception as e:
        raise ValueError(f"AI engine error: {str(e)}")